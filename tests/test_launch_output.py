import json
from data import launch_output as lo

def shot(**kw):
    d = dict(carry_yd=300.0, total_dist=270.0, launch_elev_deg=11.0, ball_speed_sep=80.0, impact_club_speed=55.0, final_y=-3.0, true_contact=True); d.update(kw); return d

def test_shot_units_and_smash(tmp_path):
    p = tmp_path / "s.json"; p.write_text(json.dumps([shot(), shot(ball_speed_sep=85.0)]))
    r = lo.rows_from(p, hole_yd=400)
    a = r[0]
    assert a["carry_yd"] == 300.0 and abs(a["total_yd"] - 270 * 1.0936) < 0.1
    assert abs(a["smash"] - 80 / 55) < 1e-3 and abs(a["ball_mph"] - 178.9) < 0.1 and a["spin_rpm"] is None and a["spin_source"] == "absent"
    assert abs(a["remaining_to_pin_yd"] - ((400 - 295.27) ** 2 + (3 * 1.0936) ** 2) ** 0.5) < 0.2
    assert "FAIL smash>1.50" in r[1]["flags"]   # 85/55 = 1.545

def test_gate_aggregate_and_ref_spin(tmp_path):
    g = dict(policy_det=dict(mean_carry=70.0, mean_distance=75.0, launch_elev_mean_deg=7.0, smash_factor_mean=0.9, peak_club_mph_mean=120.0),
             policy_stoch=dict(mean_carry=70.0, mean_distance=75.0, launch_elev_mean_deg=3.0, smash_factor_mean=1.47, peak_club_mph_mean=120.0))
    p = tmp_path / "g.json"; p.write_text(json.dumps(g))
    r = lo.rows_from(p, ref_spin=True)
    assert [x["label"] for x in r] == ["policy_det", "policy_stoch"] and all(x["aggregate"] for x in r)
    assert abs(r[0]["carry_yd"] - 70 * 1.0936) < 0.1 and r[0]["ref_spin_rpm_reference_lookup"] == 2890
    assert any("smash<1.30" in f for f in r[0]["flags"]) and r[0]["notes"]
    assert any("launch" in f for f in r[1]["flags"]) and not any("smash" in f for f in r[1]["flags"])

def test_spin_flags_and_ref():
    assert lo.flags(dict(spin_rpm=900)) == ["FAIL spin"] and lo.flags(dict(spin_rpm=2500)) == []
    assert lo.flags(dict(spin_rpm=3200)) == ["WARN spin"]
    assert lo._ref_spin(130) == 2790 and 2790 < lo._ref_spin(112) < 3040

def test_real_gate_json_readonly():
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    ps = sorted((root / "results").glob("gate_imit*_w000_s51.json")) or sorted((root / "results").glob("gate_*.json"))
    ps = [p for p in ps if "summary" not in p.name]
    if not ps: return
    before = ps[0].read_bytes(); r = lo.rows_from(ps[0]); assert r and ps[0].read_bytes() == before
