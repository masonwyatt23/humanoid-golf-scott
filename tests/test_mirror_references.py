import glob
import pytest
import os
import numpy as np
from data.mirror_references import mirror_dict, mirror_file

REF = "data/references/mason_swing_part1_s05_refined.npz"


def _load(p):
    return {k: v for k, v in np.load(p).items()}


def test_double_mirror_is_identity():
    d = _load(REF)
    m = mirror_dict(d, "x.npz")
    mm = mirror_dict(m)
    assert np.allclose(mm["joints"], d["joints"], atol=1e-9)
    assert np.allclose(mm["landmarks"], d["landmarks"], equal_nan=True, atol=1e-6)
    assert bool(mm["mirrored"]) is False


def test_sign_flips_and_swaps():
    d = _load(REF)
    m = mirror_dict(d, "src.npz")
    assert np.allclose(m["joints"][:, 1], -d["joints"][:, 1])
    assert np.allclose(m["joints"][:, 5], d["joints"][:, 8])
    assert np.allclose(m["joints"][:, 10], d["joints"][:, 7])
    assert np.allclose(m["joints"][:, 2], d["joints"][:, 2])
    assert np.allclose(m["landmarks"][:, 11, 0], -d["landmarks"][:, 12, 0], equal_nan=True)


def test_synthetic_fields_and_metadata():
    d = _load("data/references/scott_swing.npz")
    m = mirror_dict(d, "scott_swing.npz")
    for k in ["pelvis_rot_deg", "thorax_rot_deg", "x_factor_deg", "lateral_sway_m"]:
        assert np.allclose(m[k], -d[k])
    assert np.allclose(m["club_head"][:, 0], -d["club_head"][:, 0])
    assert np.allclose(m["club_head"][:, 2], d["club_head"][:, 2])
    assert np.allclose(m["joints_rad"], np.deg2rad(m["joints"]))
    assert np.array_equal(m["events"], d["events"])
    assert bool(m["mirrored"]) and str(m["mirrored_from"]) == "scott_swing.npz"
    assert str(m["original_handedness"]) == str(d.get("handedness", "right"))
    assert str(m["player_stated_handedness"]) == "left"


def test_written_files_keep_provenance_and_originals():
    # first-pass originals (mason_swing_partN_sNN.npz) are gitignored, so only check mirrors whose original exists
    files = [f for f in glob.glob("data/references/mason_*_mirrored.npz")
             if os.path.exists(f.replace("_mirrored.npz", ".npz"))]
    if not files:
        pytest.skip("no mirrored Mason file with its (gitignored) original present")
    for f in files:
        m = _load(f)
        o = _load(f.replace("_mirrored.npz", ".npz"))
        for k in ["license_class", "commercial_ok", "provenance_source", "acknowledgment_required"]:
            assert m[k] == o[k]
        assert str(m["handedness"]) == "left" and str(m["assumed_handedness"]) == "right"
        assert bool(m["mirrored"]) and not bool(o.get("mirrored", False))


MS = "data/references/multisense_P19_s20.npz"


def test_multisense_mirror_semantics(tmp_path):
    d = _load(MS)
    out = mirror_file(MS, tmp_path / "m.npz")
    m = _load(out)
    assert bool(m["mirrored"]) and str(m["mirrored_from"]) == "multisense_P19_s20.npz"
    assert str(m["original_handedness"]) == "right" and str(m["handedness"]) == "left"
    assert str(m["license_class"]) == "cc0" and bool(m["commercial_ok"])
    assert "player_stated_handedness" not in m  # not Mason
    assert m["joints"].shape == d["joints"].shape
    assert np.allclose(m["joints"][:, 1], -d["joints"][:, 1])
    assert np.allclose(m["joints"][:, 5:8], d["joints"][:, 8:11])
    assert np.allclose(m["joints"][:, 8:11], d["joints"][:, 5:8])
    assert np.allclose(m["joints"][:, [0, 2, 3, 4]], d["joints"][:, [0, 2, 3, 4]])
    assert np.allclose(m["pelvis_rot_deg"], -d["pelvis_rot_deg"])
    assert np.allclose(m["joints_rad"], np.deg2rad(m["joints"]))
    assert np.allclose(m["time"], d["time"]) and np.allclose(m["events"], d["events"])
    assert float(m["club_speed_mph_launch_monitor"]) == float(d["club_speed_mph_launch_monitor"])
    # unmeasured wrist/ankle stay zero after mirroring
    assert np.all(m["joints"][:, [3, 7, 10]] == 0)
    back = mirror_dict(m)
    assert np.allclose(back["joints"], d["joints"]) and str(back["handedness"]) == "right"


def test_all_multisense_mirrors_exist_and_tagged():
    srcs = [f for f in glob.glob("data/references/multisense_P*_s[0-9]*.npz") if "_mirrored" not in f]
    assert srcs
    for f in srcs:
        m = _load(f.replace(".npz", "_mirrored.npz"))
        assert bool(m["mirrored"]) and str(m["license_class"]) == "cc0" and bool(m["commercial_ok"])
        assert str(m["original_handedness"]) == "right"
