"""
Generate synthetic Adam Scott / Scheffler / Rory style golf swing reference motions.

IMPORTANT HONESTY NOTE
----------------------
These are *parametric kinematic caricatures*, not motion capture. The style numbers
below are rounded values taken from widely published coaching / biomechanics ranges
(e.g. TPI / 3D-motion-capture summaries of Tour players, "3:1" tempo literature) and
from public commentary on each player. They were NOT measured from these players and
should be treated as +/- 10-15 % approximations. Replace with video-derived
(`data/process_video.py`) or licensed mocap-derived values when available.

What changed vs. the first version
----------------------------------
* `tempo_ratio` was previously declared but never used (the backswing was a fixed
  fraction of the cycle). Tempo is now real: backswing_time / downswing_time, with the
  downswing measured from the top of the backswing to impact.
* Added explicit pelvis rotation, thorax (shoulder) rotation and the derived X-factor,
  lateral sway (target-ward slide), wrist hinge (set + release lag) and swing-plane
  channels. They are saved as extra arrays so downstream code can inspect / reward them.
* Downswing now follows the kinetic chain: pelvis peaks first, thorax lags and peaks
  later, wrists release last (the X-factor *stretch* just after transition).
* Noise is seeded and low-pass filtered (white noise on joint targets is not a
  plausible reference and injects jitter into the imitation reward).
* Output keeps the original 11-column `joints` layout (degrees), `club_head`, `time`,
  `dt`, so `ReferenceDataset` / `HumanoidGolfEnv` keep working unchanged.

Joint column layout (matches actuator order in env/models/humanoid_golf.xml):
  0 right_shoulder_pitch  1 right_shoulder_roll  2 right_elbow  3 right_wrist
  4 left_shoulder_pitch   5 right_hip_pitch      6 right_knee   7 right_ankle
  8 left_hip_pitch        9 left_knee           10 left_ankle
The MuJoCo model has no pelvis/torso yaw joint, so pelvis/thorax rotation cannot be
expressed directly in `joints`; it is projected onto hip-pitch / shoulder-roll proxies
and also saved verbatim in the extra channels.

Known issue (not changed here): HumanoidGolfEnv compares `joints` in DEGREES against
`qpos[14:...]` in RADIANS. `joints_rad` is also saved so the env can switch to it.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

import numpy as np
try:
    from data import provenance as _prov
except ImportError:  # run as a script
    import provenance as _prov

# --------------------------------------------------------------------------------------
# Style parameters
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class StyleParams:
    # Tempo: backswing (takeaway->top) vs downswing (top->impact), seconds.
    # Tour average is ~3:1 (backswing ~0.75-0.85 s, downswing ~0.25-0.28 s).
    backswing_time: float
    tempo_ratio: float
    # Peak rotations at the top of the backswing, degrees (relative to address/target line).
    pelvis_top: float      # hip turn; Tour ~ 40-55
    thorax_top: float      # shoulder turn; Tour ~ 85-105
    # Downswing: pelvis opens past square by impact, thorax follows.
    pelvis_impact: float   # open hips at impact; Tour ~ 35-50 open
    thorax_impact: float   # open shoulders at impact; Tour ~ 5-20 open
    # How far the thorax lags the pelvis in the downswing (0..1 of downswing time).
    # Larger = more pronounced X-factor stretch & later release.
    chain_lag: float
    # Lateral motion of pelvis, metres (+ = toward target). Backswing is trail-ward (-).
    sway_back: float       # trail-ward drift in backswing (small is "stable")
    slide_fwd: float       # target-ward slide at impact
    # Wrist hinge (deg, negative = cocked) at top and when release begins (fraction of
    # downswing; higher = later release / more lag).
    wrist_set: float
    wrist_release_start: float
    # Plane: shaft plane angle vs ground at P6/P7 (deg). Upright ~ 60+, flat ~ 50.
    plane_angle: float
    # Arm lift at top (shoulder pitch magnitude, deg) ~ backswing length.
    arm_top: float
    # Lower-body stability 0..1 (1 = quiet knees/ankles, 0 = very active/jumping).
    lower_body_stability: float


STYLES: Dict[str, StyleParams] = {
    # ADAM SCOTT -- textbook, rhythmic, quiet lower body.
    #  * ~3.0:1 tempo, unhurried: long, smooth ~0.80 s backswing.
    #  * Full shoulder turn (~100 deg) with moderate hip turn (~45) -> X-factor ~55,
    #    consistent with a "classic" restricted-hip / big-shoulder look.
    #  * Very little lateral sway (head and pelvis stay centred), modest slide.
    #  * Deep wrist set at the top and late release (lag) -- the "effortless" speed.
    #  * Slightly upright, on-plane shaft (~58-60 deg); long arm swing (~parallel+).
    "scott": StyleParams(
        backswing_time=0.80, tempo_ratio=3.0,
        pelvis_top=45, thorax_top=100,
        pelvis_impact=40, thorax_impact=10,
        chain_lag=0.35,
        sway_back=0.02, slide_fwd=0.06,
        wrist_set=-35, wrist_release_start=0.75,
        plane_angle=59, arm_top=122,
        lower_body_stability=0.85),
    # SCOTTIE SCHEFFLER -- compact, quick, very athletic lower body.
    #  * Faster ~2.4:1 (shorter 0.66 s backswing, same-ish downswing time).
    #  * Shorter backswing, smaller hip turn (~38) and shoulder turn (~92), strong
    #    X-factor via restricted hips; lots of target-ward lateral slide & ground
    #    reaction (his well-known bump / active right foot).
    #  * Flatter, more shallow plane in the downswing, earlier-ish release with a bowed
    #    lead wrist (less set, ~-28).
    "scheffler": StyleParams(
        backswing_time=0.66, tempo_ratio=2.4,
        pelvis_top=38, thorax_top=92,
        pelvis_impact=45, thorax_impact=15,
        chain_lag=0.30,
        sway_back=0.03, slide_fwd=0.13,
        wrist_set=-28, wrist_release_start=0.68,
        plane_angle=54, arm_top=108,
        lower_body_stability=0.40),
    # RORY McILROY -- powerful, athletic, big hip turn, strong chain.
    #  * ~2.8:1: 0.74 s backswing, brisk downswing.
    #  * Big hip turn (~52) and full shoulder turn (~100) -> X-factor ~48 but with
    #    very fast pelvis-first sequencing & high pelvis speed.
    #  * Moderate lateral movement; strong, late release (power lag).
    #  * Fairly upright plane (~58) and full-length swing.
    "rory": StyleParams(
        backswing_time=0.74, tempo_ratio=2.8,
        pelvis_top=52, thorax_top=100,
        pelvis_impact=48, thorax_impact=12,
        chain_lag=0.40,
        sway_back=0.03, slide_fwd=0.09,
        wrist_set=-33, wrist_release_start=0.72,
        plane_angle=58, arm_top=120,
        lower_body_stability=0.65),
    # Generic Tour-average baseline (TPI-style averages).
    "average": StyleParams(
        backswing_time=0.75, tempo_ratio=3.0,
        pelvis_top=45, thorax_top=95,
        pelvis_impact=42, thorax_impact=12,
        chain_lag=0.30,
        sway_back=0.04, slide_fwd=0.08,
        wrist_set=-32, wrist_release_start=0.65,
        plane_angle=57, arm_top=115,
        lower_body_stability=0.60),
}

ADDRESS_HOLD = 0.10   # seconds of quiet address before takeaway
FOLLOW_THROUGH = 0.30  # seconds from impact to finish


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def _smoothstep(u: np.ndarray) -> np.ndarray:
    u = np.clip(u, 0.0, 1.0)
    return u * u * u * (u * (6 * u - 15) + 10)  # quintic: zero vel & accel at ends


def _lowpass_noise(rng: np.random.Generator, shape, sigma: float, k: int = 9) -> np.ndarray:
    """Smooth, zero-mean noise with std ~= sigma."""
    if sigma <= 0:
        return np.zeros(shape)
    raw = rng.standard_normal(shape)
    kernel = np.hanning(k + 2)[1:-1]
    kernel /= kernel.sum()
    out = np.apply_along_axis(lambda x: np.convolve(x, kernel, mode="same"), 0, raw)
    std = out.std(axis=0, keepdims=True)
    std[std == 0] = 1
    return out / std * sigma


def _timeline(p: StyleParams, t: np.ndarray):
    """Return per-sample segment progress values."""
    t_takeaway = ADDRESS_HOLD
    t_top = t_takeaway + p.backswing_time
    ds_time = p.backswing_time / p.tempo_ratio
    t_impact = t_top + ds_time
    t_finish = t_impact + FOLLOW_THROUGH
    bs = _smoothstep((t - t_takeaway) / p.backswing_time)          # 0->1 backswing
    # Downswing: accelerating profile peaking at impact (speed max at impact).
    du = np.clip((t - t_top) / ds_time, 0, 1)
    ds = du ** 1.7
    ft = _smoothstep((t - t_impact) / FOLLOW_THROUGH)               # 0->1 follow-through
    return dict(t_top=t_top, t_impact=t_impact, t_finish=t_finish, ds_time=ds_time,
                bs=bs, du=du, ds=ds, ft=ft)


# --------------------------------------------------------------------------------------
# Main generator
# --------------------------------------------------------------------------------------

def generate_scott_style_swing(duration: Optional[float] = None, dt: float = 0.01,
                               style: str = "scott", seed: Optional[int] = 0,
                               noise_deg: float = 0.6) -> Dict[str, np.ndarray]:
    """
    Generate a full swing trajectory.

    style: "scott", "scheffler", "rory", "average"
    duration: seconds; default = address hold + swing + follow-through (+ small pad).
    seed: RNG seed (None = nondeterministic). noise_deg: std of smooth joint noise.
    """
    key = style if style in STYLES else "average"
    p = STYLES[key]
    tl0 = _timeline(p, np.array([0.0]))
    natural = tl0["t_finish"] + 0.05
    duration = natural if duration is None else duration
    t = np.arange(0, duration, dt)
    n = len(t)
    tl = _timeline(p, t)
    bs, du, ds, ft = tl["bs"], tl["du"], tl["ds"], tl["ft"]
    in_back = t < tl["t_top"]
    rng = np.random.default_rng(seed)

    # ---- rotations (deg) -------------------------------------------------------------
    # Backswing: pelvis turns toward trail side (-), thorax turns more (-) -> X-factor builds.
    # Downswing: pelvis leads and opens; thorax lags by `chain_lag` of the downswing.
    pelvis = np.where(in_back, -p.pelvis_top * bs, 0.0)
    thorax = np.where(in_back, -p.thorax_top * bs, 0.0)
    pel_u = _smoothstep(du)                      # pelvis phase
    tho_u = _smoothstep((du - p.chain_lag * 0.5) / (1 - p.chain_lag * 0.5))  # thorax later
    pelvis_dn = -p.pelvis_top + (p.pelvis_top + p.pelvis_impact) * pel_u
    thorax_dn = -p.thorax_top + (p.thorax_top + p.thorax_impact) * tho_u
    after_top = t >= tl["t_top"]
    pelvis = np.where(after_top, pelvis_dn, pelvis)
    thorax = np.where(after_top, thorax_dn, thorax)
    # Follow-through: both continue to a finish position.
    pelvis = pelvis + 25 * ft
    thorax = thorax + 70 * ft
    # X-factor = thorax turn minus pelvis turn (magnitudes, deg). It *grows* just after
    # transition because the pelvis unwinds first while the thorax is still loaded (stretch).
    x_factor = -thorax - (-pelvis)

    # ---- lateral sway / slide (m, + toward target) ------------------------------------
    sway = np.where(in_back, -p.sway_back * bs, 0.0)
    sway = np.where(after_top, -p.sway_back + (p.sway_back + p.slide_fwd) * _smoothstep(du * 1.3), sway)
    sway = sway + 0.02 * ft

    # ---- wrist hinge (deg; negative = cocked) -----------------------------------------
    # Set during backswing (reaches full set early ~70 % of backswing), held (lag) until
    # release_start fraction of the downswing, then released through impact.
    set_prog = _smoothstep(bs / 0.7)
    wrist = np.where(in_back, p.wrist_set * set_prog, p.wrist_set)
    release = np.clip((du - p.wrist_release_start) / (1 - p.wrist_release_start), 0, 1)
    wrist = np.where(after_top, p.wrist_set + (60 - p.wrist_set) * _smoothstep(release), wrist)
    wrist = wrist + 20 * ft

    # ---- arm swing -> shoulder pitch, elbow ---------------------------------------------
    arm = np.where(in_back, -p.arm_top * bs, 0.0)
    arm = np.where(after_top, -p.arm_top + (p.arm_top + 10) * ds, arm)
    arm = arm + 70 * ft
    elbow = np.where(in_back, 80 * bs, 80 - 60 * ds)
    elbow = np.where(t >= tl["t_impact"], 20 + 20 * ft, elbow)

    # ---- plane (deg): shaft plane angle; flatter in the downswing ("shallowing") ------
    plane = p.plane_angle - np.where(after_top, 4.0 * _smoothstep(du), 0.0)

    # ---- lower body -------------------------------------------------------------------
    instab = 1.0 - p.lower_body_stability
    hip_pitch_r = (-25 * instab * bs * in_back
                   + np.where(after_top, -25 * instab + 50 * ds * (1.2 - p.lower_body_stability), 0.0)
                   + 100 * sway * 0.5)           # slide proxy
    knee_r = 20 * bs * in_back + np.where(after_top, 20 + 40 * ds, 0.0)
    ankle_r = 6 * instab * np.sin(np.pi * np.clip(bs * in_back + ds * after_top, 0, 2) / 2)
    hip_pitch_l = 0.5 * hip_pitch_r
    knee_l = 12 * bs * in_back + np.where(after_top, 12 + 18 * ds, 0.0)
    ankle_l = -ankle_r

    joints = np.zeros((n, 11))
    joints[:, 0] = arm
    joints[:, 1] = 0.3 * (p.plane_angle - 55) * np.where(in_back, bs, 1 - ds * after_top) \
        + 0.1 * (-pelvis)                                  # plane + body-turn proxy
    joints[:, 2] = elbow
    joints[:, 3] = wrist
    joints[:, 4] = 0.6 * arm
    joints[:, 5] = hip_pitch_r
    joints[:, 6] = knee_r
    joints[:, 7] = ankle_r
    joints[:, 8] = hip_pitch_l
    joints[:, 9] = knee_l
    joints[:, 10] = ankle_l
    joints += _lowpass_noise(rng, joints.shape, noise_deg)

    # Club head: same arm-chain proxy as v1 (kept so env club-target rewards are comparable).
    sh = np.deg2rad(joints[:, 0]); el = np.deg2rad(joints[:, 2]); wr = np.deg2rad(joints[:, 3])
    club_head = np.zeros((n, 3))
    club_head[:, 0] = 0.3 + 0.58 * np.sin(sh + el) + 1.12 * np.sin(sh + el + wr)
    club_head[:, 2] = 1.0 + 0.58 * np.cos(sh + el) + 1.12 * np.cos(sh + el + wr)

    return {
        "time": t,
        "joints": joints,
        "joints_rad": np.deg2rad(joints),
        "club_head": club_head,
        "pelvis_rot_deg": pelvis,
        "thorax_rot_deg": thorax,
        "x_factor_deg": x_factor,
        "lateral_sway_m": sway,
        "wrist_hinge_deg": wrist,
        "plane_angle_deg": plane,
        "events": np.array([tl["t_top"], tl["t_impact"]]),  # [top, impact] seconds
        "tempo_ratio": np.array(p.tempo_ratio),
        "style": style,
        "duration": duration,
        "dt": np.array(dt),
    }


def compute_swing_metrics(data: Dict) -> Dict[str, float]:
    """Measured (not declared) metrics, used by tests and for documentation."""
    t = data["time"]; dt = float(data["dt"])
    top, imp = data["events"]
    takeaway = ADDRESS_HOLD
    pel, tho = data["pelvis_rot_deg"], data["thorax_rot_deg"]
    i_top = int(np.argmin(np.abs(t - top)))
    i_imp = int(np.argmin(np.abs(t - imp)))
    # X-factor stretch: max (|thorax| - |pelvis|) over the transition window.
    xf = data["x_factor_deg"][: i_imp + 1]
    return {
        "tempo_ratio": (top - takeaway) / (imp - top),
        "backswing_s": top - takeaway,
        "downswing_s": imp - top,
        "pelvis_top_deg": float(-pel[i_top]),
        "thorax_top_deg": float(-tho[i_top]),
        "x_factor_top_deg": float(-tho[i_top] - -pel[i_top]),
        "x_factor_max_deg": float(xf.max()),
        "max_sway_back_m": float(-data["lateral_sway_m"].min()),
        "max_slide_fwd_m": float(data["lateral_sway_m"][: i_imp + 1].max()),
        "wrist_set_deg": float(data["wrist_hinge_deg"][i_top]),
        "plane_angle_deg": float(data["plane_angle_deg"][i_top]),
        "n_frames": int(len(t)),
    }


def save_reference(data: Dict, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: v for k, v in data.items() if isinstance(v, np.ndarray)}
    arrays["style"] = np.array(str(data.get("style", "")))
    arrays["dt"] = np.array(float(data["dt"]))
    _prov.tag(arrays, "synthetic")
    np.savez(path, **arrays)
    print(f"Saved reference motion to {path}")


if __name__ == "__main__":
    out_dir = Path(__file__).parent / "references"
    for style in STYLES:
        data = generate_scott_style_swing(style=style)
        save_reference(data, out_dir / f"{style}_swing.npz")
        m = compute_swing_metrics(data)
        print("  " + ", ".join(f"{k}={v:.2f}" for k, v in m.items()))
    print("Synthetic reference motions generated.")
