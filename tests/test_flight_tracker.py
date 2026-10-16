import numpy as np
from eval.flight_tracker import dispersion, MPS_TO_MPH, TARGET_MS


def _shot(peak, bad=0, raw=0.0):
    return dict(final_x=1.0, final_y=0.0, carry=0.0, true_contact=True, peak_ball_speed=1.0,
                impact_club_speed=1.0, peak_club_speed=peak, nonphysical_substeps=bad, raw_max_club_speed=raw)


def test_nonphysical_episodes_excluded_not_clipped():
    d = dispersion([_shot(20.0), _shot(30.0), _shot(40.0, bad=3, raw=706966.0)])
    assert d["peak_club_unstable_episodes"] == 1
    assert d["peak_club_raw_max_unstable"] == 706966.0
    assert d["peak_club_speed_max"] == 30.0 and abs(d["peak_club_speed_mean"] - 25.0) < 1e-9
    assert abs(d["peak_club_mph_max"] - 30.0 * MPS_TO_MPH) < 1e-9
    assert abs(d["peak_club_pct_target_max"] - 30.0 / TARGET_MS * 100) < 1e-9


def test_all_unstable_gives_nan_not_crash():
    d = dispersion([_shot(5.0, bad=1, raw=1e5)])
    assert np.isnan(d["peak_club_speed_mean"]) and d["peak_club_unstable_episodes"] == 1
