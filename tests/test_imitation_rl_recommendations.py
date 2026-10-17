import json, os
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
JSON = os.path.join(ROOT, "data", "references", "imitation_rl_recommendations.json")
DOC = os.path.join(ROOT, "docs", "research_imitation_rl_methods.md")
READ = {"full_text_fetched", "partial_text_fetched", "abstract_only", "search_snippet_only"}
PRI = {"P0", "P1", "P2", "P3"}
LEVELS = {"verified_in_paper", "verified_in_paper+design_inference", "verified_in_paper+code_observation",
          "design_inference"}
REQUIRED_METHODS = ["deepmimic", "amp", "ase", "phc", "pulse", "maskedmimic", "exbody", "exbody2", "h2o",
                    "omnih2o", "humanplus", "twist", "gmt", "beyondmimic", "unitracker", "php", "smplolympics",
                    "physhoi", "tennis", "kungfubot"]


@pytest.fixture(scope="module")
def d():
    with open(JSON) as f:
        return json.load(f)


def test_top_level(d):
    for k in ("schema_version", "sources", "methods", "recommendations", "env_audit", "unverified", "caveats",
              "evidence_levels", "read_levels"):
        assert k in d
    assert d["unverified"] and d["caveats"]


def test_sources_well_formed(d):
    for sid, s in d["sources"].items():
        assert s["read_level"] in READ, sid
        assert s["url"].startswith(("https://", "repo:")), sid
        assert s["title"] and s["code_license"] and s["code_license_note"], sid
        if s["url"].startswith("https://arxiv.org/abs/"):
            assert s["arxiv"] in s["url"], sid


def test_all_required_methods_present_with_sources(d):
    for m in REQUIRED_METHODS:
        assert m in d["methods"], m
        assert m in d["sources"], m
        mm = d["methods"][m]
        assert mm["key_idea"] and mm["relevance"] and mm["reported"], m
        for h in mm["reported"]:
            assert isinstance(h["verified"], bool), (m, h["name"])
            assert h["name"] and h["where"], (m, h)
            if not h["verified"]:
                # unverified entries must be visibly labelled somewhere
                assert h.get("note") or "not" in h["value"].lower() or "snippet" in h["where"].lower() \
                    or h["where"] == "-", (m, h)


def test_unverified_license_never_claimed_open(d):
    # a license marked custom/none/unverified must not be spdx-looking permissive
    for sid, s in d["sources"].items():
        lic = s["code_license"].lower()
        if "custom" in lic or "none" in lic or "unverified" in lic:
            assert not any(x in lic for x in ("mit", "apache")), sid


def test_recommendations(d):
    ids = [r["id"] for r in d["recommendations"]]
    assert len(ids) == len(set(ids)) >= 12
    assert any(r["priority"] == "P0" for r in d["recommendations"])
    areas = {r["area"].split("/")[0] for r in d["recommendations"]}
    for need in ("timing", "rsi", "termination", "reward", "curriculum"):
        assert need in areas, need
    order = [r["priority"] for r in d["recommendations"]]
    assert order == sorted(order), "recommendations must be sorted by priority"
    for r in d["recommendations"]:
        assert r["priority"] in PRI and r["evidence_level"] in LEVELS, r["id"]
        assert r["recommendation"] and r["rationale"], r["id"]
        assert r["source_ids"], r["id"]
        for sid in r["source_ids"]:
            assert sid in d["sources"], (r["id"], sid)
        # any design-inference piece must carry an unverified note
        if "design_inference" in r["evidence_level"]:
            assert r["unverified_notes"], r["id"]
        assert r["acceptance_check"], r["id"]


def test_audit_references_real_recs(d):
    ids = {r["id"] for r in d["recommendations"]}
    for a in d["env_audit"]:
        assert a["rec"] in ids and a["severity"] in {"high", "medium", "low"}
        assert a["file"].split(":")[0].startswith(("env/", "train/"))


def test_doc_covers_everything(d):
    txt = open(DOC, encoding="utf-8").read()
    for r in d["recommendations"]:
        assert f"### {r['id']} [" in txt
    for m in REQUIRED_METHODS:
        assert d["sources"][m]["url"] in txt, m
    assert "Unverified items" in txt and "no video was scraped" in txt.lower()


def test_no_protected_dirs_touched():
    import subprocess
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout
    assert not any(p.startswith(("env/", "eval/", "train/")) for p in out.split())
