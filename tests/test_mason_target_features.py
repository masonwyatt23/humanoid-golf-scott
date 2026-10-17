import json, os, glob
import numpy as np
import pytest
from data import mason_target_features as m

REFS = os.path.join(os.path.dirname(__file__), "..", "data", "references")
JSON = os.path.join(REFS, "mason_target_features.json")
needs = pytest.mark.skipif(not glob.glob(os.path.join(REFS, "mason_v2_*.npz")), reason="no refs")


def _synth(tmp, name, **kw):
    t = np.arange(0, 1.5, 0.01)
    J = np.stack([np.sin(t * 3 + i) * 30 for i in range(11)], 1)
    d = dict(time=t, joints=J, dt=0.01, recommended=True, commercial_ok=True, partial=False,
             handedness="left", native_footage=True, mirrored=False, quality_score=0.5, valid_frac=0.8,
             handedness_verified=True, view="down_the_line", t_start_in_video=1.0, t_takeaway=1.2,
             t_top=1.8, t_impact=2.0)
    d.update(kw)
    np.savez(os.path.join(tmp, name), **d)


def test_features_synthetic_mason_missing_fields(tmp_path):
    _synth(str(tmp_path), "mason_v2_x.npz")
    sel = m.select_mason(str(tmp_path))
    assert len(sel) == 1
    f = m.features(sel[0][1], "mason")
    assert f["backswing_s"] == pytest.approx(0.6) and f["downswing_s"] == pytest.approx(0.2)
    assert f["tempo_ratio"] == pytest.approx(3.0)
    assert f["x_factor_top_deg"] == m.UNAVAIL
    assert f["sequencing"]["pelvis_peak_vel_t"] == m.UNAVAIL
    assert 0 < f["tempo_rel_uncertainty"] < 2


def test_selection_excludes(tmp_path):
    for n, kw in [("a", {}), ("b", {"mirrored": True}), ("c", {"partial": True}),
                  ("d", {"commercial_ok": False}), ("e", {"recommended": False}),
                  ("f", {"handedness": "right"})]:
        _synth(str(tmp_path), f"mason_v2_{n}.npz", **kw)
    assert [os.path.basename(p) for p, _, _ in m.select_mason(str(tmp_path))] == ["mason_v2_a.npz"]


def test_stat_and_unavailable():
    s = m._stat([1, 2, 3, 4, "unavailable"])
    assert s["n"] == 4 and s["median"] == 2.5
    assert m._stat(["unavailable"])["median"] == m.UNAVAIL


@needs
def test_json_contents_and_determinism(tmp_path):
    r = json.load(open(JSON))
    assert r["mason"]["n_swings"] == 11
    assert r["mason"]["provenance"]["license_class"] == "self_owned"
    assert all("handedness_verified" in f for f in r["mason"]["per_swing"])
    assert abs(sum(f["weight"] for f in r["mason"]["per_swing"]) - 1) < 1e-3
    assert r["mason"]["aggregate"]["x_factor_top_deg"]["median"] == "unavailable"
    assert r["comparison"]["cmu_subject64"]["aggregate"]["x_factor_top_deg"]["n"] == 10
    assert not any(f["file"].endswith("_mirrored.npz") for f in r["mason"]["per_swing"])
    assert r["caveats"]
    out = tmp_path / "o.json"
    m.main(["--refs", REFS, "--out", str(out)])
    assert json.load(open(out)) == r


def _offset_file(tmp, off, name="mason_v2_off.npz"):
    """Landmarks trimmed so that frame 0 sits `off` s after t_start_in_video; joints encode the swing-time axis."""
    t0, n = 10.0, 150
    tv = lambda s: 0.7 * np.sin(2.1 * s) + 0.4 * np.sin(5.3 * s + 1) + 0.1 * s      # swing-time wrist-height signal
    lm = np.zeros((n, 33, 4), np.float32); lm[..., 3] = 1
    sw = off + np.arange(n) / 60.0
    lm[:, 15, 1] = lm[:, 16, 1] = tv(sw)
    th = t0 + np.arange(0, 3.0, 1 / 30.0)
    hands_px = np.column_stack([th, np.zeros_like(th), tv(th - t0)]).astype(np.float32)
    t = np.arange(0, (n - 1) / 60.0, 0.01)
    J = np.zeros((len(t), 11)); J[:, 2] = np.where(t + off < 1.0, 0.0, 100.0)    # step at swing-time 1.0 s (video-relative)
    np.savez(os.path.join(tmp, name), time=t, joints=J, dt=0.01, landmarks=lm, hands_px=hands_px,
             t_start_in_video=t0, t_takeaway=t0 + 0.3, t_top=t0 + 0.8, t_impact=t0 + 1.0, **{
             k: v for k, v in dict(recommended=True, commercial_ok=True, partial=False, handedness="left",
                                   native_footage=True, mirrored=False, quality_score=0.5, valid_frac=0.8,
                                   handedness_verified=True, view="down_the_line").items()})


def test_event_time_offset_regression(tmp_path):
    off = 0.4
    _offset_file(str(tmp_path), off)
    d = np.load(tmp_path / "mason_v2_off.npz", allow_pickle=True)
    assert m.mason_time_offset(d) == pytest.approx(off, abs=0.02)
    f = m.features(d, "mason")
    # events are on the joint time axis: video-relative minus offset; durations unchanged
    assert f["impact_s"] == pytest.approx(1.0 - off, abs=0.02)
    assert f["backswing_s"] == pytest.approx(0.5) and f["downswing_s"] == pytest.approx(0.2)
    assert f["tempo_ratio"] == pytest.approx(2.5)
    assert f["joint_time_offset_s"] == pytest.approx(off, abs=0.02)


def test_offset_falls_back_to_zero_without_landmarks(tmp_path):
    _synth(str(tmp_path), "mason_v2_x.npz")
    d = np.load(tmp_path / "mason_v2_x.npz", allow_pickle=True)
    assert m.mason_time_offset(d) == 0.0


@needs
def test_real_files_offset_applied_and_tempo_intact():
    p = os.path.join(REFS, "mason_v2_p1_s01.npz")
    if not os.path.exists(p):
        pytest.skip("no p1_s01")
    d = np.load(p, allow_pickle=True)
    off = m.mason_time_offset(d)
    assert 0.3 < off < 0.6
    f = m.features(d, "mason")
    assert f["impact_s"] == pytest.approx(float(d["t_impact"]) - float(d["t_start_in_video"]) - off)
    assert f["tempo_ratio"] == pytest.approx(float(d["tempo_ratio"]), rel=0.1)
