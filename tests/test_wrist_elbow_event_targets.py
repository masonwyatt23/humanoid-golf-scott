import json
import math
from pathlib import Path

import numpy as np
import pytest

from data import wrist_elbow_event_targets as W

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "data" / "references" / "wrist_elbow_event_targets.json"


@pytest.fixture(scope="module")
def js():
    return json.load(open(JS))


def test_deterministic(tmp_path):
    p = tmp_path / "o.json"
    W.main(["--out", str(p)])
    assert json.load(open(p)) == json.load(open(JS))


def test_best_clip_is_highest_eligible(js):
    best = js["best_clip"]
    assert best["name"] == "mason_v2_p1_s06"
    ok = []
    for f in sorted((ROOT / "data/references").glob("mason_v2_p*.npz")):
        d = np.load(f, allow_pickle=True)
        if (d["recommended"] and d["native_footage"] and d["handedness_verified"] and not d["partial"]
                and str(d["handedness"]) == "left" and "unmirrored" not in f.name and "p1_s11" not in f.name and "p2_s10" not in f.name):
            ok.append((float(d["quality_score"]), f.stem))
    assert max(ok)[1] == best["name"]
    assert abs(max(ok)[0] - best["quality_score"]) < 1e-3


def test_events_offset_corrected(js):
    c = js["mason_clips"]["mason_v2_p1_s05"]
    assert c["axis_offset_s"] > 0.3
    assert c["events_naive_s"]["top"] - c["events_s"]["top"] == pytest.approx(c["axis_offset_s"], abs=0.002)
    assert js["mason_clips"]["mason_v2_p1_s06"]["events_s"] == js["mason_clips"]["mason_v2_p1_s06"]["events_naive_s"]


def test_roles_and_joint_names(js):
    lims = js["env_limits"]
    for tag in ("v3", "v4_power"):
        for j in ("right_elbow", "right_wrist", "left_elbow"):
            assert j in lims[tag]
    assert lims["v3"]["right_wrist"]["motor_peak_torque_Nm"] == 60.0
    assert lims["v4_power"]["right_wrist"]["damping"] == 0.5
    for row in js["env_targets_best_clip"]:
        assert row["role"] == ("trail" if row["env_joint"].startswith("right") else "lead")


def test_deg_rad_and_limits(js):
    for key in ("env_targets_best_clip", "env_targets_user_default_clip"):
        assert len(js[key]) == 8
        for r in js[key]:
            assert r["value_deg"] is not None
            assert r["value_rad"] == pytest.approx(math.radians(r["value_deg"]), abs=1e-3)
            if r["env_joint"] != "left_wrist" and not r["sign_uncertain"]:
                assert r["in_limits_v3"] and r["in_limits_v4_power"]
    top = [r for r in js["env_targets_best_clip"] if r["env_joint"] == "right_wrist" and r["event"] == "top"][0]
    assert top["env_value_deg_if_cocked_negative"] == -top["value_deg"]
    imp = [r for r in js["env_targets_best_clip"] if r["env_joint"] == "right_wrist" and r["event"] == "impact"][0]
    assert "env_value_deg_if_cocked_negative" not in imp


def test_lead_arm_matches_stored_columns(js):
    """The landmark port must reproduce stored cols 2/3 (lead arm for Mason) at top."""
    for n, c in js["mason_clips"].items():
        t = c["arms"]["lead"]["top"]
        assert t["source"] == "landmarks"
        assert abs(t["elbow_flexion_deg"] - t["stored_col2_elbow_deg"]) < 4.0, n
        assert abs(t["wrist_dev_deg"] - t["stored_col3_wrist_deg"]) < 4.0, n


def test_reference_sets_flags(js):
    rm = js["reference_medians"]
    assert rm["multisense_mirrored_trail_arm"]["license_class"] == "needs_counsel"
    assert rm["multisense_mirrored_trail_arm"]["n_wrist_measured"] == 0
    assert rm["cmu_64_trail_arm"]["n_files"] == 10
    assert rm["cmu_64_trail_arm"]["top"]["wrist_col3_deg"]["median"] < 0   # cocked negative


def test_no_fabricated_published_ranges(js):
    assert js["published_numeric_ranges_for_elbow_or_wrist_angle_at_top_or_impact"].startswith("NONE FOUND")
    assert "UNVERIFIED" in js["status"]
