import json
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/launch_targets_120_132_limits.json"))

def test_honesty_and_sources():
    assert "NONE EXIST" in d["mason_own_numbers"]
    ids = {s["id"] for s in d["sources"]}
    for s in d["sources"]:
        assert s["url"].startswith("http") and isinstance(s["unverified"], bool) and s["verification"]
    assert {"tm_optimizer_2010", "foresight_ref_tables", "tm_smash_blog"} <= ids

def test_targets_tagged_and_physical():
    assert set(d["targets"]) == {"120", "130", "132"}
    for v, t in d["targets"].items():
        p = t["point_target_trackman_AoA0"]
        assert p["basis"] == ("published" if v == "120" else "extrapolated")
        assert abs(p["ball_mph"] / int(v) - p["smash"]) < 0.002 and p["smash"] <= 1.50
        assert 6 <= p["launch_deg"] <= 12 and 2000 <= p["spin_rpm"] <= 3200
        w = t["foresight_window"]
        assert w["carry_range_yd"][0] < w["carry_range_yd"][1] and w["total_range_yd"][0] > w["carry_range_yd"][0]
    assert d["targets"]["130"]["total_yd"]["value"] is None and d["targets"]["120"]["total_yd"]["value"] == 340
    assert d["targets"]["132"]["point_target_trackman_AoA0"]["carry_yd"] > d["targets"]["130"]["point_target_trackman_AoA0"]["carry_yd"]

def test_limits_and_models():
    L = d["limits"]
    assert L["smash"]["driver"]["hard_ceiling"] == 1.50 and L["smash"]["pitching_wedge"]["typical"][0] < 1.3
    assert L["spin_rpm"]["driver"]["usga_ball_test"] == 2520
    assert all("model" in r["basis"] for r in d["model_runs_130_132"]) and len(d["model_runs_130_132"]) == 8
    assert all(r["smash"] <= 1.50 for r in d["model_runs_130_132"])
