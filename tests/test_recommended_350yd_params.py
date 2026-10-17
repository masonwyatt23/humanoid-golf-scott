import json
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/recommended_350yd_params.json"))

def test_honesty_and_no_private():
    assert any("Instagram" in h for h in d["honesty"]) and d["unverified_items"]
    assert "imit_private" not in json.dumps(d["measured_loft_scan"])

def test_scan_and_fit():
    s = {r["loft_deg"]: r for r in d["measured_loft_scan"]}
    assert s[-27]["launch_deg"] == 9.72 and s[-31]["launch_deg"] > s[-29]["launch_deg"] > s[-27]["launch_deg"] > s[-25]["launch_deg"]
    assert d["scan_fit"]["launch_deg_per_loft_deg"] < 0
    assert 9.7 < d["scan_fit"]["interpolated_launch_by_loft"]["-28"] < 11.2

def test_recommendation():
    r = d["recommended"]
    assert r["loft_deg"] == -28 and r["impact_gain"] <= 1.22 and 9 <= r["elev_target_deg"] <= 11 and r["spin_k"] == 130
    for m in d["model_prediction_130_132"]:
        assert m["smash"] <= 1.50 and m["total_yd"] >= m["carry_yd"] and 9 <= m["launch_deg"] <= 11 and 1800 <= m["env_formula_spin_rpm_k130"] <= 3000

def test_shaping_and_bc_flags():
    assert {t["term"] for t in d["shaping_terms"]} >= {"start_line", "face_angle_at_impact", "club_path", "lateral_miss_yards"}
    tags = {b["source"]: b["license_tag"] for b in d["bc_prior_options"]}
    assert tags["CMU subject 64 (10 swings)"] == "counsel_required" and tags["BONES-SEED"] == "counsel_required"
    assert tags["AMASS / GolfDB / HumanML3D / Motion-X"].startswith("EXCLUDED")
