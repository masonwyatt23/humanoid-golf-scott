import json
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/targets_130mph_350yd_and_loft.json"))

def test_sources_and_honesty():
    for s in d["sources"]:
        assert s["url"].startswith("http") and isinstance(s["unverified"], bool) and s["verification"]
    assert any("Instagram" in h and "no" in h.lower() for h in d["honesty"])
    assert d["target_130_mph"]["trackman_style_point_AoA0"]["basis"].startswith("extrapolated")
    assert d["target_130_mph"]["trackman_style_point_AoA0"]["total_yd"] is None
    assert d["unverified_items"]

def test_model_grids_physical():
    for key in ("model_grid_130mph_K4_e0845", "model_grid_130mph_K5p6_e0845", "model_club_speed_scan"):
        for r in d[key]:
            assert "model" in r["basis"] and r["smash"] <= 1.50 and r["total_yd"] >= r["carry_yd"] - 1
            assert r["spin_loft_deg"] == r["dynamic_loft_deg"] - r["aoa_deg"]
    g = [r for r in d["model_grid_130mph_K4_e0845"] if r["spin_loft_deg"] >= 8]
    assert max(r["total_yd"] for r in g) < 360 and max(r["carry_yd"] for r in g) < 340   # 350 carry NOT reached at 130 mph in the model
    a = {(r["aoa_deg"], r["spin_loft_deg"]): r for r in g}
    assert a[(0, 10)]["spin_rpm"] > a[(0, 8)]["spin_rpm"] and a[(0, 10)]["smash"] < a[(0, 8)]["smash"]

def test_launch_relation():
    for r in d["launch_from_aoa_and_spin_loft"]:
        sl = r["spin_loft_deg"]
        assert abs(r["aoa_deg"] + sl * (0.96 - 0.0071 * sl) - r["target_launch_deg"]) < 0.15
        assert abs(r["dynamic_loft_deg"] - sl - r["aoa_deg"]) < 0.11

def test_bc_license_flags():
    b = {o["id"]: o for o in d["bc_prior_options"]}
    assert "counsel_required" in b["cmu_subject64"]["license_flag"] and "counsel_required" in b["multisensegolf"]["license_flag"]
    assert "EXCLUDED" in b["amass_golfdb_humanml"]["license_flag"]
