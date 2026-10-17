"""Schema + consistency checks for data/references/mocap_dataset_licenses.json (not legal advice)."""
import json, os, re
import pytest
from data import provenance as P

PJ = os.path.join(os.path.dirname(__file__), "..", "data", "references", "mocap_dataset_licenses.json")
REQ = ["id", "name", "domain", "golf_relevance", "license_name", "license_url", "license_evidence_quote",
       "commercial_ok", "commercial_note", "attribution_requirement", "ml_training_note", "size", "format",
       "access", "verification", "recommended_tag", "counsel_needed", "counsel_reason", "citation_url"]
VER = {"primary_fetched", "secondary_search_snippet", "unverified"}
MUST = ["cmu_mocap", "amass", "multisensegolf", "caddieset", "golfdb", "golfpose", "sportspose", "human36m",
        "aistpp", "style100", "lafan1", "unitree_lafan1_retarget", "mixamo", "kit_whole_body", "motionx",
        "humanml3d", "bedlam", "3dpw", "cmu_panoptic", "opencap_service", "opencap_datasets", "smpl_model"]


@pytest.fixture(scope="module")
def doc():
    return json.load(open(PJ))


def test_top_level(doc):
    assert "NOT legal advice" in doc["disclaimer"]
    assert set(doc["commercial_ok_values"]) == {"yes", "no", "needs_counsel"}
    assert set(doc["recommended_tag_classes"]["existing"]) == set(P.LICENSE_CLASSES)


def test_required_datasets_and_unique_ids(doc):
    ids = [d["id"] for d in doc["datasets"]]
    assert len(ids) == len(set(ids))
    for m in MUST:
        assert m in ids, m


def test_entry_schema(doc):
    allowed_tags = set(P.LICENSE_CLASSES) | set(doc["recommended_tag_classes"]["proposed_new"])
    for d in doc["datasets"]:
        for k in REQ:
            assert k in d, (d.get("id"), k)
        assert d["commercial_ok"] in doc["commercial_ok_values"], d["id"]
        assert d["verification"] in VER, d["id"]
        assert d["recommended_tag"] in allowed_tags, d["id"]
        assert isinstance(d["counsel_needed"], bool)
        assert re.match(r"https?://", d["license_url"]) and re.match(r"https?://", d["citation_url"])
        assert d["license_evidence_quote"].strip() and d["commercial_note"].strip()


def test_consistency_with_provenance_presets(doc):
    for d in doc["datasets"]:
        t, ok = d["recommended_tag"], d["commercial_ok"]
        if ok == "needs_counsel":
            assert d["counsel_needed"] and d["counsel_reason"].strip(), d["id"]
        if ok == "yes":
            # only fully read licenses may be marked clean-yes
            assert d["verification"] == "primary_fetched" and not d["counsel_needed"], d["id"]
        if t in P.PRESETS:
            if P.PRESETS[t]["commercial_ok"] is False:
                assert ok in ("no", "needs_counsel"), (d["id"], t)
        if t == "noncommercial":
            assert ok != "yes", d["id"]


def test_known_hard_facts(doc):
    by = {d["id"]: d for d in doc["datasets"]}
    for k in ("amass", "lafan1", "human36m", "sportspose", "motionx", "bedlam", "3dpw", "cmu_panoptic", "golfdb"):
        assert by[k]["commercial_ok"] == "no", k
    assert by["cmu_mocap"]["commercial_ok"] == "needs_counsel" and by["cmu_mocap"]["recommended_tag"] == "needs_counsel"  # retagged 2026-10
    assert "mocap.cs.cmu.edu" in by["cmu_mocap"]["attribution_requirement"] or "Acknowledg" in by["cmu_mocap"]["attribution_requirement"]
    assert by["golfpose"]["commercial_ok"] == "needs_counsel"
