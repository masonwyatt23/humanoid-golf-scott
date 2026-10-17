import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from data import mason_elbow_camera_bias as B
from data import mason_keyframe_targets_extra as X

ROOT = Path(__file__).resolve().parents[1]
J = json.loads((ROOT / "data/references/mason_elbow_camera_bias.json").read_text())
E_ = json.loads((ROOT / "data/references/mason_keyframe_targets_extra.json").read_text())
MAIN = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())


def test_zero_yaw_projection_is_identity_and_2d_underreads():
    for th in (15, 25, 35):
        assert abs(B.projected_flexion(th, 0.0, 10.0) - th) < 1e-6
        assert B.projected_flexion(th, 45.0, 10.0) < th


def test_noise_fold_bias_is_positive_and_decreases_with_angle():
    nf = J["simulation"]["noise_fold_bias_3d"]["sigma_0.02m"]
    assert nf["10"]["bias"] > nf["25"]["bias"] > nf["45"]["bias"] > 0
    assert all(v["bias"] == 0 for v in J["simulation"]["noise_fold_bias_3d"]["sigma_0.00m"].values())


def test_pipeline_elbow_matches_landmark_recompute():
    d = np.load(ROOT / "data/references/mason_v2_p1_s03.npz", allow_pickle=True)
    L = d["landmarks"].astype(float)
    e3 = B.flex(L[0, 12, :3], L[0, 14, :3], L[0, 16, :3])
    assert abs(e3 - d["joints"][0, 2]) < 2.0


def test_recommendation_consistent_and_flagged_unverified():
    r = J["recommendation"]; lo, hi = r["bias_corrected_range_deg"]
    assert J["unverified"] is True and "low" in r["confidence"]
    assert lo < r["bias_corrected_center_deg"] < hi
    assert abs(r["raw_median_deg"] - 29.14) < 0.1
    assert abs(r["bias_corrected_range_rad"][0] - np.radians(lo)) < 1e-3
    assert r["bias_corrected_center_deg"] < r["raw_median_deg"]
    assert -6.0 <= r["takeaway_in_motion_correction_deg"] <= 0.0


def test_view_table_flags_small_n_and_no_clean_faceon():
    assert J["per_view"]["face_on"]["unflagged_all"]["address_deg"] is None
    assert J["per_view"]["oblique"]["unflagged_all"]["address_deg"]["n"] == 1
    for n in J["per_view"]["down_the_line"]["unflagged_all"]["clips"]:
        assert not J["per_clip"][n]["flags"]


def test_camera_bias_json_reproducible(tmp_path):
    out = tmp_path / "o.json"
    subprocess.run([sys.executable, "-m", "data.mason_elbow_camera_bias", "--out", str(out)], cwd=ROOT, check=True, capture_output=True)
    assert json.loads(out.read_text()) == J


# ---- extra keyframe targets ----
def test_extra_disjoint_from_main_and_all_excluded_from_pooling():
    main = set(MAIN["clips_used"]) | set(MAIN["clips_aux_not_in_stats"])
    assert not main & set(E_["clips"])
    assert E_["n_clips"] == len(E_["clips"]) > 20
    assert all(c["excluded_from_pooling"] and c["unverified"] for c in E_["clips"].values())


def test_extra_flags_preserved():
    c = E_["clips"]
    assert "handedness_unverified" in c["mason_v2_p1_s11"]["flags"] and "excluded_in_unified_v2" in c["mason_v2_p1_s11"]["flags"]
    assert "partial" in c["mason_v2_p1_s02_partial"]["flags"]
    assert "mirrored_copy_of_swing" in c["mason_v2_p3_s09"]["flags"] or "detected_or_stated_right_handed" in c["mason_v2_p3_s09"]["flags"]
    sm = c["mason_v3_p2_s03_slowmo"]
    assert "slowmo_time_stretched" in sm["flags"] and sm["time_stretch"]["slowdown_factor_est"] > 2


def test_extra_main_file_untouched_and_reproducible(tmp_path):
    assert "mason_v3_p2_s03_slowmo" in MAIN["clips_excluded"]
    out = tmp_path / "e.json"
    subprocess.run([sys.executable, "-m", "data.mason_keyframe_targets_extra", "--out", str(out)], cwd=ROOT, check=True, capture_output=True)
    assert json.loads(out.read_text()) == E_


def test_extra_keyframe_values_finite_where_reported():
    for n, c in E_["clips"].items():
        if c.get("keyframes"):
            for k, kf in c["keyframes"].items():
                if kf:
                    assert set(kf["joints_deg"]) == set(X.JOINTS)


def test_one_page_guide_length_and_content():
    t = (ROOT / "docs/FILMING_GUIDE_ONE_PAGE.md").read_text()
    assert 330 <= len(t.split()) <= 460
    for w in ("240 fps", "Down-the-line", "Face-on", "tee height", "left-handed", "mason_<YYYYMMDD>"):
        assert w.lower() in t.lower()
