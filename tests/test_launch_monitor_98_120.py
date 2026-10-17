import json
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/launch_monitor_98_120_tables.json"))

def test_schema_and_honesty():
    assert d["schema_version"] == 1 and "NONE EXIST" in d["mason_own_numbers"]
    for s in d["sources"]:
        assert s["url"].startswith("http") and s["verification"] and "type" in s and isinstance(s["unverified"], bool)
    assert set(d["tables"]) == {"98", "120"}

def test_rows_physical_and_consistent():
    for sp, t in d["tables"].items():
        v = float(sp)
        for k, r in t.items():
            if k == "range_summary" or not isinstance(r, dict) or "smash" not in r: continue
            assert 1.38 <= r["smash"] <= 1.50, (sp, k)
            assert abs(r["ball_mph"] / r.get("club_mph", v) - r["smash"]) < 0.01
            assert 4 <= r["launch_deg"] <= 16 and 1500 <= r["spin_rpm"] <= 3800
        assert "interpolation" in t["trackman_optimizer_carry_AoA0"]
    assert "linear" in d["tables"]["98"]["trackman_optimizer_carry_AoA0"]["interpolation"]
    assert d["tables"]["120"]["usga_ball_test"]["spin_rpm"] == 2520

def test_model_comparison():
    assert len(d["model_runs"]) >= 8
    c = d["model_comparison"]
    for sp in ("98", "120"):
        assert 3.5 < c[sp]["K_that_matches_target_spin"] < 4.5
        assert c[sp]["spin_ratio_patched_over_target"] < 1 < c[sp]["spin_ratio_default_over_target"]
    assert len(c["recommendations"]) >= 5
