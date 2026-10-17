import json, math
from pathlib import Path

import numpy as np

from data import mason_elbow_address_stats as M

ROOT = Path(__file__).resolve().parents[1]
J = json.loads((ROOT / "data/references/mason_elbow_address_stats.json").read_text())


def test_mapping_matches_env_xml():
    xml = (ROOT / "env/models/humanoid_golf_v4_power.xml").read_text()
    assert 'name="right_elbow" type="hinge" axis="0 1 0" range="0 150"' in xml
    assert J["mapping"]["env_limit_deg"] == [0.0, 150.0]
    kf = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())
    assert kf["joint_columns"][M.ELBOW_COL] == "right_elbow"


def test_rad_matches_deg_and_pooled_within_limits():
    for g, v in J["pooled"].items():
        d, r = v["address_deg"]["deg"], v["address_deg"]["rad"]
        for k in ("median", "min", "max", "std"):
            if d[k] is not None:
                assert abs(r[k] - math.radians(d[k])) < 1e-9
        assert 0 <= d["min"] <= d["median"] <= d["max"] <= 150


def test_pooled_mason_matches_per_clip():
    kf = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())
    vals = [J["per_clip"][n]["address_deg"] for n in kf["clips_used"]]
    assert len(vals) == 8
    assert abs(np.median(vals) - J["pooled"]["mason_native_left_kf_clips"]["address_deg"]["deg"]["median"]) < 1e-9


def test_recommendation_respects_failure_threshold_and_limits():
    for c in J["recommendation"]["candidates"].values():
        assert c["low_rad"] >= M.FAIL_THRESHOLD_RAD + M.MARGIN_RAD - 1e-9
        assert c["high_deg"] <= 150
        assert c["low_rad"] < c["high_rad"]
        assert abs(c["equiv_env_base_rad"] - (c["low_rad"] + c["high_rad"]) / 2) < 1e-9


def test_excluded_clips_absent_and_reproducible(tmp_path):
    assert "mason_v2_p1_s11" not in J["per_clip"] and "mason_v2_p2_s10" not in J["per_clip"]
    out = tmp_path / "o.json"
    M.main(out)
    assert json.loads(out.read_text()) == J
