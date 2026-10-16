import json
from pathlib import Path

import numpy as np
import pytest

from data import generate_synthetic_scott as g
from data import process_video as pv


@pytest.mark.parametrize("style", list(g.STYLES))
def test_generator_metrics_match_params(style):
    d = g.generate_scott_style_swing(style=style)
    m = g.compute_swing_metrics(d)
    p = g.STYLES[style]
    assert abs(m["tempo_ratio"] - p.tempo_ratio) < 0.05
    assert abs(m["x_factor_top_deg"] - (p.thorax_top - p.pelvis_top)) < 1e-6
    assert m["x_factor_max_deg"] >= m["x_factor_top_deg"]  # stretch in transition
    assert d["joints"].shape[1] == 11 and np.isfinite(d["joints"]).all()
    assert np.abs(d["joints"]).max() < 200


def test_style_ordering_known_traits():
    m = {s: g.compute_swing_metrics(g.generate_scott_style_swing(style=s)) for s in ["scott", "scheffler", "rory"]}
    assert m["scott"]["tempo_ratio"] > m["rory"]["tempo_ratio"] > m["scheffler"]["tempo_ratio"]
    assert m["scott"]["max_sway_back_m"] < m["scheffler"]["max_sway_back_m"]
    assert m["scheffler"]["max_slide_fwd_m"] > m["scott"]["max_slide_fwd_m"]
    assert m["rory"]["pelvis_top_deg"] > m["scheffler"]["pelvis_top_deg"]


def test_generator_seeded_and_loader_compatible(tmp_path):
    a = g.generate_scott_style_swing(style="scott", seed=1)["joints"]
    b = g.generate_scott_style_swing(style="scott", seed=1)["joints"]
    assert np.array_equal(a, b)
    g.save_reference(g.generate_scott_style_swing(style="scott"), tmp_path / "scott_swing.npz")
    from imitation.reference_dataset import ReferenceDataset
    ds = ReferenceDataset(tmp_path, styles=["scott"])
    assert len(ds) == 1 and ds.sample()["joints"].shape[1] == 11


def _fake_landmarks(n=60, dropout=()):
    rng = np.random.default_rng(0)
    base = np.zeros((N := 33, 4))
    base[:, 3] = 0.99
    pts = {pv.R_SH: (0.1, -0.5), pv.L_SH: (-0.1, -0.5), pv.R_HIP: (0.08, 0), pv.L_HIP: (-0.08, 0),
           pv.R_EL: (0.2, -0.3), pv.L_EL: (-0.2, -0.3), pv.R_WR: (0.25, -0.1), pv.L_WR: (-0.25, -0.1),
           pv.R_IDX: (0.27, -0.05), pv.R_KNEE: (0.08, 0.4), pv.L_KNEE: (-0.08, 0.4),
           pv.R_ANK: (0.08, 0.8), pv.L_ANK: (-0.08, 0.8), pv.R_FOOT: (0.15, 0.85), pv.L_FOOT: (-0.01, 0.85)}
    for i, (x, y) in pts.items():
        base[i, 0], base[i, 1] = x, y
    lm = np.repeat(base[None], n, 0)
    lm[..., :3] += rng.normal(0, 0.002, lm[..., :3].shape)
    for f in dropout:
        lm[f, :, :] = np.nan
    return lm


def test_gap_fill_and_visibility():
    lm = _fake_landmarks(60, dropout=[10, 11, 12])
    lm[30, pv.R_WR, 3] = 0.1  # low visibility single landmark
    out = pv.process_landmarks(lm, fps=30)
    assert np.isfinite(out["joints"]).all() and out["valid_frac"] > 0.95


def test_long_gap_rejected_and_bad_inputs():
    lm = _fake_landmarks(60, dropout=range(5, 50))
    with pytest.raises(ValueError):
        pv.process_landmarks(lm, fps=30)
    with pytest.raises(ValueError):
        pv.process_landmarks(_fake_landmarks(60), fps=float("nan"))
    with pytest.raises(ValueError):
        pv.process_landmarks(_fake_landmarks(5), fps=30)


def test_fps_resample_and_slowmo_dt():
    out = pv.process_landmarks(_fake_landmarks(250), fps=250, out_dt=0.01)  # 1 s real time
    assert abs(out["time"][-1] - 0.99) < 0.02 and float(out["dt"]) == 0.01


def test_resume_and_error_isolation(tmp_path):
    cv2 = pytest.importorskip("cv2")
    vids, out = tmp_path / "v", tmp_path / "out"
    vids.mkdir()
    for name in ["a.mp4", "b.mp4"]:
        w = cv2.VideoWriter(str(vids / name), cv2.VideoWriter_fourcc(*"mp4v"), 30, (64, 64))
        for _ in range(40):
            w.write(np.zeros((64, 64, 3), np.uint8))
        w.release()
    (vids / "corrupt.mp4").write_bytes(b"not a video")
    calls = {"n": 0}
    lm = _fake_landmarks(1)[0]

    def backend(frame):
        calls["n"] += 1
        return lm
    pv.make_backend = lambda model=None: (backend, lambda: None)
    rc = pv.main(["--videos", str(vids), "--out", str(out)])
    assert rc == 3  # corrupt one failed, others saved
    assert (out / "a_processed.npz").exists() and (out / "b_processed.npz").exists()
    first = calls["n"]
    pv.main(["--videos", str(vids), "--out", str(out)])
    assert calls["n"] == first  # resumed: good videos skipped (corrupt fails before backend)
    assert "a.mp4" in json.loads((out / "processed_index.json").read_text())
