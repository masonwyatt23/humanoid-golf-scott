import json, os, subprocess, sys, tempfile
import pytest
from data import compare_mason_to_profile as C

ROOT = os.path.join(os.path.dirname(__file__), "..")
PJ = os.path.join(ROOT, "data", "references", "pro_swing_profiles.json")
CONF = {"high", "medium", "low", "none"}
VERIFIED = {"fetched", "fetched_pdf", "search_snippet", "read_locally"}
NEEDED = ["bryson_dechambeau_style", "tiger_woods_style", "adam_scott_style", "chris_gotterup_style",
          "scottie_scheffler_style", "rory_mcilroy_style", "tour_average"]


@pytest.fixture(scope="module")
def prof():
    return json.load(open(PJ))


@pytest.fixture(scope="module")
def mason():
    return json.load(open(C.MASON))


def test_profiles_present_and_cautions(prof):
    for k in NEEDED:
        assert k in prof["profiles"]
    assert len(prof["legal_likeness_cautions"]) >= 4
    assert any("counsel" in c for c in prof["legal_likeness_cautions"])


def test_sources_and_features_wellformed(prof):
    for sid, s in prof["sources"].items():
        assert s["verified"] in VERIFIED and s["url"].startswith(("https://", "http://", "repo:")), sid
    for pid, p in prof["profiles"].items():
        for fn, ft in p["features"].items():
            assert ft["confidence"] in CONF, (pid, fn)
            for sid in ft["source_ids"]:
                assert sid in prof["sources"], (pid, fn, sid)
            if ft["target"] is None:
                assert ft["unverified"] is True, (pid, fn)  # never a silent null
            if ft["min"] is not None and ft["max"] is not None:
                assert ft["min"] <= ft["max"], (pid, fn)
            if ft["target"] is not None and ft["min"] is not None and ft["max"] is not None:
                assert ft["min"] <= ft["target"] <= ft["max"], (pid, fn)
            if ft["confidence"] == "none":
                assert ft["unverified"] and ft["target"] is None


def test_synthetic_assumptions_flagged(prof):
    for pid in ("scottie_scheffler_style", "rory_mcilroy_style"):
        t = prof["profiles"][pid]["features"]["tempo_ratio"]
        assert t["unverified"] is True


def test_compare_logic(mason, prof):
    res = C.build(mason, prof)
    assert set(res["mason_features"]) == {"tempo_ratio", "backswing_s", "downswing_s", "club_head_speed_mph"}
    sc = {p["profile"]: p for p in res["per_profile"]}
    chs = [r for r in sc["bryson_dechambeau_style"]["items"] if r["feature"] == "club_head_speed_mph"][0]
    assert chs["delta"] == pytest.approx(-8.0) and chs["direction"] == "below"
    assert "SELF-REPORTED" in chs["advice"]
    for p in res["per_profile"]:
        pr = [r["priority"] for r in p["items"]]
        assert pr == sorted(pr, reverse=True)
        for r in p["items"]:
            assert r["profile_band"][0] < r["profile_band"][1]
            assert r["priority"] >= 0
    assert any("30 fps" in c for c in res["caveats"]) and any("self-reported" in c.lower() for c in res["caveats"])
    assert res["measure_next"]


def test_unverified_downweighted_and_unavailable_not_scored(mason, prof):
    res = C.build(mason, prof)
    for p in res["per_profile"]:
        for r in p["items"]:
            assert r["feature"] in C.PLAIN  # no x-factor / peak-speed scoring for Mason
    # synthetic unverified tempo gets half weight vs an identical verified one
    pf = {"target": 3.0, "min": 2.5, "max": 3.5, "confidence": "medium", "unverified": False, "unit": "ratio", "source_ids": []}
    pu = dict(pf, unverified=True)
    mk = lambda f: {"profiles": {"x": {"label": "X", "kind": "style_profile", "features": {"tempo_ratio": f}}}}
    a = C.build(mason, mk(dict(pf, target=2.0, min=1.5, max=2.5)))["per_profile"][0]["items"][0]["priority"]
    b = C.build(mason, mk(dict(pu, target=2.0, min=1.5, max=2.5)))["per_profile"][0]["items"][0]["priority"]
    assert b == pytest.approx(a / 2, abs=0.002)


def test_cli_deterministic(mason):
    with tempfile.TemporaryDirectory() as d:
        outs = []
        for i in range(2):
            j, m = os.path.join(d, "j%d.json" % i), os.path.join(d, "m%d.md" % i)
            C.main(["--out-json", j, "--out-md", m])
            outs.append((open(j).read(), open(m).read()))
        assert outs[0] == outs[1]
    # committed outputs are current
    assert open(C.OUT_JSON).read() == json.dumps(C.build(mason, json.load(open(PJ))), indent=1, sort_keys=True) + "\n"
