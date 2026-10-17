import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data import speed_gap_100_120 as sg

def test_ratios_and_targets():
    assert abs(sg.target_deg_s("club", 109) - 2254) < 1e-6
    for seg in sg.ORDER:
        assert 1.15 < sg.ratio(seg) < 1.26
    assert sg.target_deg_s("pelvis", 120) < sg.target_deg_s("thorax", 120) < sg.target_deg_s("lead_arm", 120) < sg.target_deg_s("club", 120)

def test_json_matches_module():
    d = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "references", "speed_gap_100_120_published.json")))
    assert d["_meta"]["contains_instagram_or_mason_derived_data"] is False
    for seg in sg.ORDER:
        assert abs(d["derived_power_law_fit"]["peak_deg_s_at_120_mph"][seg] - sg.target_deg_s(seg, 120)) < 1.5
        assert abs(d["derived_power_law_fit"]["peak_deg_s_at_100_mph"][seg] - sg.target_deg_s(seg, 100)) < 1.5

def test_terms():
    ok = {s: sg.target_deg_s(s, 120) for s in sg.ORDER}
    assert sg.peak_term(ok, 120) == 0.0
    assert sg.peak_term({s: 0.5 * v for s, v in ok.items()}, 120) < -1
    assert sg.sequence_bonus({"pelvis": .1, "thorax": .12, "lead_arm": .13, "club": .2}) == 1.0
    assert sg.gap_penalty(120, 120) == 0.0 and sg.gap_penalty(100, 120) < 0
