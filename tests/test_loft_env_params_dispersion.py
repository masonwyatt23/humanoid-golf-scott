import json
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/loft_env_params_dispersion.json"))

def test_sources_and_honesty():
    for s in d["dispersion"]["sources_numbers"]:
        assert s["url"].startswith("http") and isinstance(s["unverified"], bool) and s["verification"]
    assert any("Instagram" in h and "no" in h.lower() for h in d["honesty"])
    assert d["unverified_items"]
    assert any(s["id"] == "t5golf_blog" and "LOW CONFIDENCE" in s["caveat"] for s in d["dispersion"]["sources_numbers"])

def test_model_rows_physical():
    for r in d["launch_options_table"]:
        assert "model" in r["basis"] and r["smash"] <= 1.50 and r["total_yd"] >= r["carry_yd"] - 1
        assert r["spin_loft_deg"] == r["dynamic_loft_deg"] - r["aoa_deg"]
    a = {(r["club_mph"], r["config"][0], r["K"]): r for r in d["launch_options_table"]}
    for m in (100, 120, 130):   # lower dynamic loft at same AoA lowers launch
        assert a[(m, "A", 4.0)]["launch_deg"] > a[(m, "B", 4.0)]["launch_deg"] > a[(m, "C", 4.0)]["launch_deg"]
        assert a[(m, "E", 4.0)]["launch_deg"] < 8.0

def test_dispersion_monotone_and_calibrated():
    s = d["dispersion"]["stock_scatter_push"]
    for g in {r["group"] for r in s}:
        rr = sorted([r for r in s if r["group"] == g], key=lambda r: r["club_mph"])
        assert [r["lateral_sigma_yd_1sigma"] for r in rr] == sorted(r["lateral_sigma_yd_1sigma"] for r in rr)
    pro = [r for r in s if r["sigma_alpha_deg_published"] == 4.0]
    assert all(0.5 < r["face_sigma_deg_calibrated"] < 3 for r in pro)
    assert max(r["lateral_sigma_yd_1sigma"] for r in s) < 40

def test_bc_license_flags():
    b = {o["id"]: o for o in d["bc_prior_options"]}
    for k in ("cmu_subject64", "multisensegolf", "bones_seed"):
        assert "counsel_required" in b[k]["license_flag"]
    assert "EXCLUDED" in b["amass_golfdb_humanml"]["license_flag"]
