from pathlib import Path

import numpy as np
import pytest

from data import convert_cmu_mocap as C

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "references"
RAW = ROOT / "data" / "raw_mocap" / "cmu"

TINY = """HIERARCHY
ROOT Hips
{
\tOFFSET 0 0 0
\tCHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
\tJOINT Child
\t{
\t\tOFFSET 1 0 0
\t\tCHANNELS 3 Zrotation Yrotation Xrotation
\t\tEnd Site
\t\t{
\t\t\tOFFSET 1 0 0
\t\t}
\t}
}
MOTION
Frames: 3
Frame Time: .0083333
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 90 0 0 0 0 0
"""


def _write(tmp_path, text=TINY, name="64_99.bvh"):
    p = tmp_path / name
    p.write_text(text)
    return p


def test_parse_and_fk_scale_and_euler_order(tmp_path):
    b = C.parse_bvh(_write(tmp_path))
    assert b.names == ["Hips", "Child", "Child_end"]
    assert b.motion.shape == (3, 9)
    pos = C.forward_kinematics(b, slice(0, None))
    s = C.ASF_TO_M
    np.testing.assert_allclose(pos[0, 1], [1 * s, 0, 0], atol=1e-9)        # ASF units -> metres
    np.testing.assert_allclose(pos[0, 2], [2 * s, 0, 0], atol=1e-9)
    # root Z rotation of 90 deg turns +X child to +Y
    np.testing.assert_allclose(pos[2, 1], [0, 1 * s, 0], atol=1e-9)
    np.testing.assert_allclose(pos[2, 2], [0, 2 * s, 0], atol=1e-9)


def test_fk_default_drops_tpose_frame(tmp_path):
    b = C.parse_bvh(_write(tmp_path))
    assert C.forward_kinematics(b).shape[0] == 2


@pytest.mark.parametrize("bad", ["garbage", TINY.replace("Frames: 3", "Frames: 4")])
def test_bad_bvh_raises(tmp_path, bad):
    with pytest.raises(C.CmuConvertError):
        C.parse_bvh(_write(tmp_path, bad))


def test_bad_name_and_fps(tmp_path):
    with pytest.raises(C.CmuConvertError):
        C.convert_bvh(_write(tmp_path, name="swing.bvh"))
    with pytest.raises(C.CmuConvertError):          # 120 Hz required
        C.convert_bvh(_write(tmp_path, TINY.replace(".0083333", ".0333333")))


def test_missing_trial_reports_failure(tmp_path):
    rc = C.main(["--raw-dir", str(tmp_path), "--out-dir", str(tmp_path / "o"), "--trials", "64_01"])
    assert rc == 1


def _synthetic_hands(fps=120):
    """rest 1.0 s, backswing up 1.0 s (with a pause at the top), fast downswing 0.4 s, rest."""
    t = np.arange(0, 4.0, 1 / fps)
    addr = np.array([0.0, 0.85, 0.0])
    h = np.tile(addr, (len(t), 1))
    up = (t >= 1.0) & (t < 2.0)
    u = (t[up] - 1.0)
    h[up, 1] = 0.85 + 0.65 * (3 * u**2 - 2 * u**3)
    h[(t >= 2.0), 1] = 1.5
    dn = (t >= 2.1) & (t < 2.5)
    v = (t[dn] - 2.1) / 0.4
    h[dn, 1] = 1.5 - 0.65 * v**2.5
    h[(t >= 2.5), 1] = 0.85
    h[(t >= 2.5), 0] = 0.0
    return t, h


def test_event_detection_on_synthetic_hand_path():
    t, h = _synthetic_hands()
    ev = C.detect_events(h, 120)
    assert abs(t[ev["takeaway"]] - 1.0) < 0.15
    assert abs(t[ev["top"]] - 2.0) < 0.12
    assert abs(t[ev["impact"]] - 2.5) < 0.12
    assert ev["takeaway"] < ev["top"] < ev["impact"] < ev["finish"] + 1


def test_event_detection_rejects_still_hands():
    h = np.tile([0.0, 0.85, 0.0], (400, 1)) + np.random.default_rng(0).normal(0, 1e-4, (400, 3))
    with pytest.raises(C.CmuConvertError):
        C.detect_events(h, 120)


def test_handedness_detection_from_finish():
    n = 100
    P = {k: np.zeros((n, 3)) for k in ["RightArm", "LeftArm", "RightHand", "LeftHand"]}
    P["LeftArm"][:, 0] = 0.2; P["RightArm"][:, 0] = -0.2
    P["RightHand"][:] = [0.15, 1.5, 0.0]; P["LeftHand"][:] = [0.15, 1.5, 0.0]   # over left shoulder
    assert C.detect_handedness(None, P) == "right"
    P["RightHand"][:] = [-0.15, 1.5, 0.0]; P["LeftHand"][:] = [-0.15, 1.5, 0.0]
    assert C.detect_handedness(None, P) == "left"


# ---------------------------------------------------------------- committed reference outputs
CMU_FILES = sorted(REF.glob("cmu_64_*.npz"))


@pytest.mark.skipif(not CMU_FILES, reason="cmu references not generated")
@pytest.mark.parametrize("path", CMU_FILES, ids=lambda p: p.stem)
def test_reference_schema_and_labels(path):
    d = np.load(path)
    n = len(d["time"])
    assert d["joints"].shape == (n, 11) and d["joints_rad"].shape == (n, 11)
    np.testing.assert_allclose(np.rad2deg(d["joints_rad"]), d["joints"], atol=1e-9)
    assert float(d["dt"]) == pytest.approx(0.01)
    np.testing.assert_allclose(np.diff(d["time"]), 0.01, atol=1e-9)
    assert np.isfinite(d["joints"]).all() and np.abs(d["joints"]).max() < 250
    assert str(d["source"]) == "cmu_mocap" and not bool(d["is_synthetic"])
    assert not bool(d["has_club_head"]) and "club_head" not in d.files
    assert int(d["subject"]) == 64 and str(d["trial_id"]).startswith("64_")
    top, imp = d["events"]
    assert 0 < top < imp < d["time"][-1]
    assert 1.0 < float(d["tempo_ratio"]) < 3.5
    i_top = int(round(top / 0.01))
    assert d["pelvis_rot_deg"][i_top] < -20 and d["thorax_rot_deg"][i_top] < d["pelvis_rot_deg"][i_top]
    assert d["x_factor_deg"][i_top] > 15
    assert d["lateral_sway_m"][:i_top].min() < 0 < d["lateral_sway_m"].max()   # trail then target


@pytest.mark.skipif(not CMU_FILES, reason="cmu references not generated")
def test_reference_dataset_loads_cmu():
    from imitation.reference_dataset import ReferenceDataset
    ds = ReferenceDataset(REF)
    cmu = [r for r in ds.references if r["name"].startswith("cmu_64_")]
    assert len(cmu) == len(CMU_FILES)
    assert all(r["club_head"] is None and r["dt"] == pytest.approx(0.01) for r in cmu)


@pytest.mark.skipif(not (RAW / "64_02.bvh").exists(), reason="raw CMU BVH not downloaded")
def test_end_to_end_matches_committed_reference(tmp_path):
    d = C.convert_bvh(RAW / "64_02.bvh")
    old = np.load(REF / "cmu_64_02.npz")
    np.testing.assert_allclose(d["joints"], old["joints"])
    assert d["events"] == pytest.approx(old["events"])
