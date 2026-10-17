import json, os
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
JSON = os.path.join(ROOT, "data", "references", "impact_physics_calibration.json")
CONF = {"high", "medium", "low", "none"}


@pytest.fixture(scope="module")
def d():
    with open(JSON) as f:
        return json.load(f)


def test_top_level(d):
    for k in ("schema_version", "sources", "values", "formulas", "model_comparison", "recommendations", "unverified_ids", "caveats"):
        assert k in d


def test_sources_and_values_schema(d):
    ids = {s["id"] for s in d["sources"]}
    assert len(ids) == len(d["sources"])
    for s in d["sources"]:
        assert s["url"].startswith("http") and s["verification"] in {"fetched", "search_snippet", "not_fetched"}
    seen = set()
    for v in d["values"]:
        assert v["id"] not in seen
        seen.add(v["id"])
        assert v["confidence"] in CONF and isinstance(v["unverified"], bool)
        assert v["source_ids"] and set(v["source_ids"]) <= ids
        if not v["unverified"]:
            assert v["confidence"] in {"high", "medium"}
    for f in d["formulas"] + d["recommendations"]:
        assert f["confidence"] in CONF or f["confidence"].startswith(("medium", "n/a"))


def test_unverified_ids_resolve(d):
    vids = {v["id"] for v in d["values"]}
    mets = {c["metric"] for c in d["model_comparison"]["comparison"]}
    for u in d["unverified_ids"]:
        assert u in vids or u in mets


def test_sanity_values(d):
    v = {x["id"]: x for x in d["values"]}
    assert v["usga_ct_limit"]["value"] == 239
    assert 0.82 <= v["usga_cor_legacy"]["value"] <= 0.83
    assert 1.4 < v["smash_tour_2023"]["value"] < 1.51
    assert v["gear_horizontal"]["value"] == 16.4 and v["gear_vertical"]["value"] == 25
    assert v["spin_formula_tutelman"]["unverified"] is True


def test_model_snapshot_consistent(d):
    runs = d["model_comparison"]["model_runs"]
    for r in runs["grid_default_runs"]:
        assert abs(r["ball_mph"] / r["mph"] - r["smash"]) < 0.02
        assert 1.3 < r["smash"] < 1.52 and 1500 < r["spin"] < 6000
    # carry rises with club speed at fixed geometry
    base = [r for r in runs["grid_default_runs"] if r["att"] == 2 and r["dyn_loft"] == 12.5]
    carries = [r["carry_yd"] for r in sorted(base, key=lambda r: r["mph"])]
    assert carries == sorted(carries)
    # documented finding: mu is inactive -> spin identical across mu sweep
    sweep = [r for r in runs["e_mu_sweep_tour"] if r["e"] == 0.83]
    assert len({r["spin"] for r in sweep}) == 1


def test_recommendation_direction(d):
    runs = d["model_comparison"]["model_runs"]["patched_copy_sweep"]
    k56 = [r for r in runs if r.get("K") == 5.6 and r.get("e") == 0.83][0]
    assert abs(k56["spin"] - 2545) < 100


def test_model_unchanged_readonly():
    import subprocess
    out = subprocess.run(["git", "diff", "--stat", "--", "env"], cwd=ROOT, capture_output=True, text=True)
    assert out.stdout.strip() == ""
