"""Published-biomechanics speed-gap targets for the stock ~100 -> ~120 mph club-speed gap.

Model-only. Source: Cheetham et al. (Science & Golf V, ch.4) Table 1, 88 mph amateurs vs 109 mph pros
(fetched). 100 mph values are interpolated, 120 mph values are EXTRAPOLATED (unverified).
Contains no Mason / Instagram-derived data. See docs/SPEED_GAP_100_120_SPEC.md.
"""
import math

CHS = {"amateur": 88.0, "pro": 109.0}
PEAK = {  # deg/s, Cheetham Table 1
    "pelvis": {"amateur": 395.0, "pro": 477.0},
    "thorax": {"amateur": 583.0, "pro": 727.0},
    "lead_arm": {"amateur": 763.0, "pro": 980.0},
    "club": {"amateur": 1790.0, "pro": 2254.0},
}
ORDER = ("pelvis", "thorax", "lead_arm", "club")
# env joints (g1_golf_env actuator names); thorax = pelvis_yaw + waist_yaw_joint rates
ENV_JOINTS = {
    "pelvis": ("pelvis_yaw",),
    "thorax": ("pelvis_yaw", "waist_yaw_joint"),
    "lead_arm": ("left_shoulder_pitch_joint", "left_shoulder_roll_joint", "left_shoulder_yaw_joint"),
    "club": ("left_wrist_pitch_joint", "right_wrist_pitch_joint"),
}
PRO_PEAK_BEFORE_IMPACT_MS = {"pelvis": 87.0, "thorax": 68.0, "lead_arm": 65.0, "club": 0.0}
UNVERIFIED = True  # extrapolated beyond 109 mph


def exponent(seg):
    return math.log(PEAK[seg]["pro"] / PEAK[seg]["amateur"]) / math.log(CHS["pro"] / CHS["amateur"])


def target_deg_s(seg, chs_mph):
    """Peak rotational speed target (deg/s) at a club-head speed; extrapolated above 109 mph."""
    return PEAK[seg]["pro"] * (chs_mph / CHS["pro"]) ** exponent(seg)


def ratio(seg, chs_to=120.0, chs_from=100.0):
    return (chs_to / chs_from) ** exponent(seg)


def peak_term(peaks_deg_s, chs_target, w=0.5, scale=0.15, over_weight=0.25):
    """Per-segment peak-speed reward in [-4, 0]; shortfall counts fully, overshoot x over_weight."""
    r = 0.0
    for seg in ORDER:
        t = target_deg_s(seg, chs_target)
        e = (peaks_deg_s[seg] - t) / (scale * t)
        r += -(e * e) * (1.0 if e < 0 else over_weight)
    return max(-4.0, w * r)


def sequence_bonus(peak_times_s, w=1.0, min_gap_s=0.005, pelvis_decel=None):
    """peak_times_s: dict seg -> time of peak. 1/3 credit per correctly ordered adjacent pair (gap>=min_gap)."""
    ok = sum((peak_times_s[b] - peak_times_s[a]) >= min_gap_s for a, b in zip(ORDER[:-1], ORDER[1:]))
    bonus = w * ok / 3.0
    if pelvis_decel:
        bonus += 0.5
    return bonus


def gap_penalty(chs_now, chs_target, w=0.1):
    return -w * max(0.0, chs_target - chs_now) / chs_target
