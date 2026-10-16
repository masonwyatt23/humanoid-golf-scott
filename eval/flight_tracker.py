"""
flight_tracker (MINIMAL EQUIVALENT, written by the evaluator; no pre-existing
flight_tracker.py was found anywhere on the box).

Records the ball trajectory (world frame) every env step and summarizes dispersion.

Conventions (MuJoCo world frame, golfer facing +x, z up, right-handed axes):
  x = down-the-line (forward), +y = LEFT of the target line, -y = RIGHT, z = up.
  Target line = the x axis through the ball's start y (=0).
Lateral miss: final |y| > LATERAL_THRESHOLD_M (default 0.5 m).
  left miss  : final y > +threshold ;  right miss : final y < -threshold.
Impact club speed = |linear velocity| of club_head geom at the first club-ball contact step (env info).
Peak club speed = max over every physics substep (club speed = world-frame linear part v[3:] of mj_objectVelocity for the club_head geom; samples >100 m/s or non-finite are NON-PHYSICAL: such episodes are flagged and excluded from peak stats, never clipped) of the whole episode of club_head linear speed (m/s; x2.23694 = mph); target 120 mph = 53.64 m/s.
Smash factor = peak ball speed (m/s over the episode) / impact club speed, per contact shot with club speed > MIN_CLUB_SPEED, then averaged.
Distance = final ball x (total/rolled), carry from env info (0 if never landed after flight).
"""
from typing import Dict, Sequence
import warnings
import numpy as np

LATERAL_THRESHOLD_M = 0.5
MPS_TO_MPH = 2.23694
TARGET_MPH = 120.0
TARGET_MS = 53.64     # 120 mph
MAX_PLAUSIBLE_CLUB_SPEED = 100.0  # m/s; above this the MuJoCo sim blew up (unstable QACC), not a real speed
FLAT_LAUNCH_DEG = 5.0   # launch elevation below this = flat/negative (flagged): mean < 5 deg or >= 50% of shots < 5 deg
MIN_CLUB_SPEED = 0.05  # m/s; smash factor undefined below this


class FlightTracker:
    def __init__(self, env):
        self.env, self.traj = env, []

    def install(self):
        """Patch mujoco.mj_step to sample club_head speed after EVERY physics substep (peak over whole swing)."""
        import mujoco
        self._mj, self._orig, self.peak_club = mujoco, mujoco.mj_step, 0.0
        self.n_nonphysical, self.raw_max, self.first_bad_t = 0, 0.0, None
        self._sep, self._last_v, self.v_sep = False, None, None
        def wrapped(m, d, *a, **k):
            self._orig(m, d, *a, **k)
            v = self.env._club_speed()
            if not np.isfinite(v) or v > MAX_PLAUSIBLE_CLUB_SPEED:   # validate; never silently clip
                self.n_nonphysical += 1
                self.raw_max = max(self.raw_max, v) if np.isfinite(v) else float("inf")
                if self.first_bad_t is None: self.first_bad_t = float(d.time)
            else:
                self.peak_club = max(self.peak_club, v)
            # launch vector = ball velocity at the end of club-ball contact (first substep without contact after first true contact)
            if self.env.true_contact and not self._sep:
                bv = self.env._ball_lin_vel(); self._last_v = bv
                if not self.env._check_contact():
                    self._sep, self.v_sep = True, bv
        mujoco.mj_step = wrapped
        return self

    def close(self):
        if getattr(self, "_orig", None) is not None:
            self._mj.mj_step = self._orig; self._orig = None

    def reset(self):
        self.peak_club, self.n_nonphysical, self.raw_max, self.first_bad_t = 0.0, 0, 0.0, None
        self._sep, self._last_v, self.v_sep = False, None, None
        self.traj = [self.env.data.xpos[self.env._ball_id].copy()]

    def step(self):
        self.traj.append(self.env.data.xpos[self.env._ball_id].copy())

    def launch_elev_deg(self) -> float:
        """Elevation (deg) of the ball velocity right after contact (separation velocity); NaN if no contact."""
        v = self.v_sep if self.v_sep is not None else self._last_v
        if v is None:
            return float("nan")
        return float(np.degrees(np.arctan2(v[2], np.hypot(v[0], v[1]) + 1e-9)))

    def summary(self, info: Dict) -> Dict[str, float]:
        t = np.asarray(self.traj)
        return {"final_x": float(t[-1, 0]), "final_y": float(t[-1, 1]), "final_z": float(t[-1, 2]),
                "max_height": float(t[:, 2].max()), "max_abs_y": float(np.abs(t[:, 1]).max()),
                "carry": float(info.get("carry", 0.0)), "true_contact": bool(info.get("true_contact", False)),
                "peak_ball_speed": float(info.get("peak_ball_speed", float("nan"))),
                "impact_club_speed": float(info.get("impact_club_speed", float("nan"))),
                "launch_elev_deg": self.launch_elev_deg(),
                "launch_elev_env_peakspeed_deg": float(np.degrees(info.get("launch_elevation", float("nan")))),
                "peak_club_speed": float(getattr(self, "peak_club", float("nan"))),
                "nonphysical_substeps": int(getattr(self, "n_nonphysical", 0)),
                "raw_max_club_speed": float(getattr(self, "raw_max", 0.0)),
                "first_nonphysical_sim_time": getattr(self, "first_bad_t", None)}


def dispersion(shots: Sequence[Dict], thr: float = LATERAL_THRESHOLD_M) -> Dict[str, float]:
    x = np.array([s["final_x"] for s in shots]); y = np.array([s["final_y"] for s in shots])
    tc = np.array([s["true_contact"] for s in shots], bool)
    def rates(m):
        return (float((y[m] > thr).mean()), float((y[m] < -thr).mean())) if m.any() else (float("nan"),) * 2
    l, r = rates(np.ones(len(y), bool)); lc, rc = rates(tc)
    cs = np.array([s.get("impact_club_speed", np.nan) for s in shots]); bs = np.array([s["peak_ball_speed"] for s in shots])
    ok = tc & (cs > MIN_CLUB_SPEED)           # contact shots with a measurable club speed
    smash = bs[ok] / cs[ok]
    pk = np.array([s.get("peak_club_speed", np.nan) for s in shots])
    bad = np.array([s.get("nonphysical_substeps", 0) > 0 for s in shots])
    n_unstable = int(bad.sum())
    raw = np.array([s.get("raw_max_club_speed", 0.0) for s in shots])
    pk = np.where(bad, np.nan, pk)    # episodes with any non-physical substep are EXCLUDED from peak stats (and counted/reported), not clipped
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pkm, pkx = np.nanmean(pk), (np.nanmax(pk) if (~np.isnan(pk)).any() else float("nan"))
    le = np.array([s.get("launch_elev_deg", np.nan) for s in shots])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lem, les = (float(np.nanmean(le)), float(np.nanstd(le))) if (~np.isnan(le)).any() else (float("nan"),) * 2
        leflat = float(np.mean(le[~np.isnan(le)] < FLAT_LAUNCH_DEG)) if (~np.isnan(le)).any() else float("nan")
    return {"launch_elev_mean_deg": lem, "launch_elev_std_deg": les, "launch_flat_frac": leflat,
            "launch_flat_flag": bool(lem == lem and (lem < FLAT_LAUNCH_DEG or leflat >= 0.5)),
            "peak_club_unstable_episodes": n_unstable, "peak_club_raw_max_unstable": float(raw.max()) if bad.any() else None, "peak_club_speed_mean": float(pkm), "peak_club_speed_max": float(pkx),
            "peak_club_mph_mean": float(pkm * MPS_TO_MPH), "peak_club_mph_max": float(pkx * MPS_TO_MPH),
            "peak_club_pct_target_mean": float(pkm / TARGET_MS * 100), "peak_club_pct_target_max": float(pkx / TARGET_MS * 100),
            "impact_club_speed_mean": float(np.nanmean(cs[tc])) if tc.any() else float("nan"),
            "impact_club_speed_max": float(np.nanmax(cs[tc])) if tc.any() else float("nan"),
            "smash_factor_mean": float(smash.mean()) if ok.any() else float("nan"),
            "smash_factor_median": float(np.median(smash)) if ok.any() else float("nan"),
            "smash_factor_n": int(ok.sum()), "episodes": int(len(x)), "contact_rate": float(tc.mean()),
            "mean_distance": float(x.mean()), "std_distance": float(x.std()), "median_distance": float(np.median(x)),
            "max_distance": float(x.max()), "mean_y": float(y.mean()), "lateral_std": float(y.std()),
            "mean_abs_y": float(np.abs(y).mean()), "max_abs_y": float(np.abs(y).max()),
            "left_miss_rate": l, "right_miss_rate": r, "in_corridor_rate": 1 - l - r,
            "left_miss_rate_contact_only": lc, "right_miss_rate_contact_only": rc,
            "mean_carry": float(np.mean([s["carry"] for s in shots])),
            "landed_fraction": float(np.mean([s["carry"] > 0 for s in shots])),
            "mean_peak_ball_speed": float(np.nanmean([s["peak_ball_speed"] for s in shots])),
            "lateral_threshold_m": thr}
