import json, pytest
from pathlib import Path
from data import roll_aoa_addon as r
d = json.load(open(Path(__file__).resolve().parent.parent / "data/references/roll_aoa_addon.json"))

def test_labels_and_no_private():
    assert "MODEL-ONLY" in d["label"] and "MODEL-ONLY" in r.estimate_roll_yd(300, launch_deg=10, spin_rpm=2400)["label"]
    s = json.dumps(d); assert "imit_private" not in s and "mason_swings" not in s

def test_total_ge_carry_and_monotone_firmness():
    t = [r.estimate_roll_yd(300, launch_deg=10.4, spin_rpm=2400, firmness=f)["total_yd"] for f in ("soft", "normal", "firm", "very_firm")]
    assert t == sorted(t) and t[0] >= 300

def test_flatter_and_lower_spin_roll_more():
    a = r.estimate_roll_yd(300, descent_deg=35, spin_rpm=2400)["roll_yd"]; b = r.estimate_roll_yd(300, descent_deg=45, spin_rpm=2400)["roll_yd"]
    c = r.estimate_roll_yd(300, descent_deg=38, spin_rpm=1800)["roll_yd"]; e = r.estimate_roll_yd(300, descent_deg=38, spin_rpm=3200)["roll_yd"]
    assert a > b and c > e

def test_reference_point_is_base_fraction():
    x = r.estimate_roll_yd(275, descent_deg=38, spin_rpm=2686)
    assert x["roll_frac"] == pytest.approx(0.09, abs=1e-4)

def test_normal_firmness_in_published_band_for_tour_like_shots():
    for p in d["validation"]:
        if "Foresight" in p["src"] or "carry-optimizer" in p["src"] or "R&A" in p["src"]:
            assert 1.06 <= p["model_normal"] <= 1.14

def test_metres_helper():
    c = r.estimate_total_from_m(296, launch_deg=10.4, spin_rpm=2400)
    assert c["total_m"] > 296 and abs(c["total_yd"] - c["total_m"] * 1.0936133) < 0.2

def test_errors():
    with pytest.raises(ValueError): r.estimate_roll_yd(0, launch_deg=10)
    with pytest.raises(ValueError): r.estimate_roll_yd(300)
    with pytest.raises(ValueError): r.estimate_roll_yd(300, launch_deg=10, firmness=5)
    with pytest.raises(ValueError): r.aoa_sensitivity([0, 1])

def test_sensitivity_physics():
    s = r.sensitivity_per_deg()
    assert 0 < s["fixed_dynamic_loft"]["launch_deg_per_aoa_deg"] < 0.4 and 0.8 < s["fixed_spin_loft"]["launch_deg_per_aoa_deg"] < 1.1
    assert r.tutelman_launch(4, 7.5) == pytest.approx(10.8, abs=0.05)
