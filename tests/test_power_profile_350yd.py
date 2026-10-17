import json, os, subprocess, sys, tempfile
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
JSON = os.path.join(ROOT, "data", "references", "power_profile_350yd_targets.json")
CONF = {"high", "medium", "low", "none"}
VERIFIED = {"fetched", "fetched_pdf", "search_snippet", "run_locally", "read_locally"}


@pytest.fixture(scope="module")
def d():
    with open(JSON) as f:
        return json.load(f)


def test_top_level(d):
    for k in ("schema_version", "sources", "metrics", "ladder", "mason_gap", "humanoid_actuator_audit", "caveats", "notes"):
        assert k in d
    assert d["mason_gap"]["verified"] is False and d["mason_gap"]["handedness"] == "left"


def test_sources_well_formed(d):
    for sid, s in d["sources"].items():
        assert s["verified"] in VERIFIED, sid
        assert s["url"].startswith(("https://", "repo:")), sid
        assert s["terms"] and s["title"], sid


def test_metric_bands_and_refs(d):
    for name, m in d["metrics"].items():
        assert m["confidence"] in CONF, name
        assert isinstance(m["unverified"], bool), name
        for sid in m["source_ids"]:
            assert sid in d["sources"], (name, sid)
        if "min" in m:
            vals = [m[k] for k in ("min", "target", "max") if m[k] is not None]
            assert vals == sorted(vals), name
            assert m["unit"], name
            if m["unverified"]:
                assert m["confidence"] in ("low", "none"), name
            if m["confidence"] != "none" and not m["unverified"]:
                assert m["source_ids"], name       # verified values must cite a source
    for k in ("wrist_hinge_uncock_peak_speed_dps", "ground_reaction_torque_nm"):
        m = d["metrics"][k]
        assert m["unverified"] and m["target"] is None


def test_key_verified_numbers(d):
    m = d["metrics"]
    assert m["club_length_in"]["max"] == 48.0 and "usga_equip_part2" in m["club_length_in"]["source_ids"]
    assert d["sources"]["usga_equip_part2"]["verified"] == "fetched"
    assert m["smash_factor"]["max"] <= 1.50
    assert m["pelvis_peak_speed_dps"]["target"] < m["thorax_peak_speed_dps"]["target"] < m["lead_arm_peak_speed_dps"]["target"] < m["club_shaft_peak_speed_dps"]["target"]
    s = m["seq_peak_time_before_impact_ms"]
    assert s["pelvis"]["mean"] > s["thorax"]["mean"] > s["arm"]["mean"]


def test_ladder_monotonic(d):
    L = d["ladder"]
    assert [s["club_head_speed_mph"] for s in L] == [113, 120, 130, 140, 150]
    for k in ("ball_speed_mph", "sim_total_yd", "sim_carry_yd", "torque_scale_vs_113", "power_scale_vs_113"):
        v = [s[k] for s in L]
        assert v == sorted(v) and len(set(v)) == len(v), k
    st = {s["club_head_speed_mph"]: s for s in L}
    assert 340 <= st[130]["sim_total_yd"] <= 360 and st[120]["sim_total_yd"] < 340


def test_actuator_audit_matches_xml(d):
    a = d["humanoid_actuator_audit"]["actuators"]
    assert a["right_wrist"]["peak_torque_nm"] == 60.0 and a["chest_yaw"]["peak_torque_nm"] == 120.0
    for n, v in a.items():
        assert v["peak_power_w"] == pytest.approx(v["peak_torque_nm"] ** 2 / (4 * v["joint_damping_nm_s_rad"]), rel=0.01), n
    rows = d["humanoid_actuator_audit"]["ladder_requirements"]
    fr = [r["wrist_net_torque_frac"] for r in rows]
    assert fr == sorted(fr, reverse=True)


def test_generator_is_deterministic(d):
    out = os.path.join(tempfile.mkdtemp(), "x.json")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "gen_power_profile_350yd.py"), "--out", out], stdout=subprocess.DEVNULL)
    with open(out) as f:
        assert json.load(f) == d
