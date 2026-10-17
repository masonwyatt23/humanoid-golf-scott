import json, os
import pytest
ROOT = os.path.join(os.path.dirname(__file__), "..")
P = os.path.join(ROOT, "data", "references", "humanoid_actuator_specs.json")
CONF = {"high", "medium", "low", "none"}

@pytest.fixture(scope="module")
def d():
    return json.load(open(P))

def test_top(d):
    for k in ("schema_version", "sources", "platforms", "model_requirements", "plausibility_assessment", "notes"):
        assert k in d
    assert {"unitree_g1", "unitree_h1", "unitree_h1_2", "boston_dynamics_atlas_electric", "tesla_optimus", "figure_02", "figure_03"} <= set(d["platforms"])

def test_sources(d):
    for sid, s in d["sources"].items():
        assert s["url"].startswith(("https://", "repo:")), sid
        assert s["source_type"] and s["title"], sid

def test_records_cited(d):
    n = 0
    for pid, p in d["platforms"].items():
        for rec in p["general"]:
            n += 1
            for k in ("field", "value", "source_id", "source_type", "confidence", "unverified"):
                assert k in rec, (pid, rec)
            assert rec["source_id"] in d["sources"], (pid, rec["field"])
            assert rec["confidence"] in CONF
            if rec["value"] is None:  # no number without a source / no fabricated value
                assert rec["unverified"] is True and rec["confidence"] == "none", (pid, rec["field"])
            if rec["confidence"] in ("low", "none"):
                assert rec["unverified"] is True, (pid, rec["field"])
        for j in p["joints"]:
            assert j["source_id"] in d["sources"] and isinstance(j["peak_torque_nm"], (int, float))
            assert j["range_deg"][0] < j["range_deg"][1] and j["max_speed_rad_s"] > 0
    assert n > 40

def test_key_values(d):
    h12 = {j["joint"]: j for j in d["platforms"]["unitree_h1_2"]["joints"]}
    assert h12["torso (waist yaw)"]["peak_torque_nm"] == 200
    assert h12["wrist_roll"]["peak_torque_nm"] == 19
    g1 = {j["joint"]: j for j in d["platforms"]["unitree_g1"]["joints"]}
    assert g1["waist_yaw"]["peak_torque_nm"] == 88
    atlas = {r["field"]: r for r in d["platforms"]["boston_dynamics_atlas_electric"]["general"]}
    assert atlas["peak_torque_any_joint"]["value"] is None and atlas["dof_total"]["value"] == 56

def test_assessment_covers_platforms(d):
    assert len(d["plausibility_assessment"]) >= 6
    for a in d["plausibility_assessment"]:
        assert a["wrist_120nm"] and a["pelvis_yaw"] and a["overall"]
