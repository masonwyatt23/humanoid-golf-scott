import numpy as np
from sim.golf_simulator import shot_from_launch, shot_from_club, MPS_TO_MPH
from sim import course as C


def test_trackman_row_flight_within_tolerance():   # published: 167 mph, 10.9 deg, 2686 rpm -> 275 yd carry, 32 yd apex, 38 deg landing
    s = shot_from_launch(167, 10.9, 2686, club_mph=113)
    assert abs(s.carry_yd - 275) / 275 < 0.05 and abs(s.apex_yd - 32) / 32 < 0.10 and abs(s.land_angle_deg - 38) < 3
    assert abs(s.smash - 1.478) < 0.01 and s.total_yd > s.carry_yd


def test_impact_smash_and_ball_speed():
    s = shot_from_club(113, -1.3, 13)
    assert 1.40 < s.smash < 1.50 and abs(s.ball_mph - s.smash * 113) < 1e-6


def test_directions_left_positive_and_symmetry():
    l = shot_from_club(113, face_deg=3, path_deg=0); r = shot_from_club(113, face_deg=-3, path_deg=0)
    assert l.lateral_total_yd > 10 and r.lateral_total_yd < -10 and abs(l.lateral_total_yd + r.lateral_total_yd) < 0.5
    assert shot_from_club(113).lateral_total_yd == 0.0


def test_monotonic_speed_and_units():
    a, b = shot_from_launch(150, 11, 2600), shot_from_launch(170, 11, 2600)
    assert b.carry_yd > a.carry_yd and abs(a.ball_mph - 150) < 1e-6


def test_course_example_is_par72_18_holes():
    c = C.example_course()
    assert len(c) == 18 and sum(h.par for h in c) == 72 and C.LABEL.startswith("model-based estimate, not a real round")


def test_course_perfect_tour_player_beats_par_and_short_hitter_worse():
    c = C.example_course()
    tour = C.Profile("t", 275.0, 1.0, 0.5, 0.07, "x"); short = C.Profile("s", 120.0, 5.0, 1.0, 0.0, "x")
    a, b = C.simulate(c, tour, 100, 1), C.simulate(c, short, 100, 1)
    assert a["mean_score"] < 72 and b["mean_score"] > a["mean_score"] + 15


def test_course_reproducible_and_penalty_hazard():
    c = C.example_course(); p = C.Profile("t", 250.0, 15.0, 8.0, 0.05, "x")
    assert C.simulate(c, p, 50, 7)["mean_score"] == C.simulate(c, p, 50, 7)["mean_score"]
    h = c[0]; assert C.lie_at(h, 100, 80, C.DEFAULTS) == "ob" and C.lie_at(h, h.yards, 0, C.DEFAULTS) == "green"


def test_spin_scale_reduces_backspin_and_keeps_ball_speed():
    from sim.golf_simulator import shot_from_club, SPIN_SCALE_TOUR_CAL
    raw = shot_from_club(113, -1.3, 14.0); cal = shot_from_club(113, -1.3, 14.0, spin_scale=SPIN_SCALE_TOUR_CAL)
    assert abs(cal.ball_mph - raw.ball_mph) < 1e-6 and raw.spin_scale == 1.0 and cal.spin_scale == SPIN_SCALE_TOUR_CAL
    assert abs(cal.backspin_rpm / raw.backspin_rpm - SPIN_SCALE_TOUR_CAL) < 0.02
    assert abs(cal.backspin_rpm - 2686) / 2686 < 0.10        # Data Agent R1: calibrated spin within the validation tolerance at the TrackMan row
    assert abs(raw.backspin_rpm - 2686) / 2686 > 0.10        # raw model is the ~60% high one


def test_course_gate_pooled_profile_labels_hypothetical():
    from sim.course import profile_from_gates
    p = profile_from_gates("ppo_v4power_s61")
    assert p is not None and "hypothetical-strength" in p.note and p.driver_carry_yd > 250 and p.lateral_sd_yd > 10   # seed-9000 outlier inflates pooled lateral sd
