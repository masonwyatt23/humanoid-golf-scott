"""Launch-monitor style per-shot output from the analytic ball model (env/ball_flight_analytic.py).

MODEL-BASED: numbers come from the analytic impact + ball-flight model (calibrated by its authors to TrackMan PGA Tour driver averages),
NOT from the MuJoCo-physics ball that eval/flight_tracker.py / the leaderboard use (that ball has the known smash~1.0 artifact, see results/smash_anomaly.md).

Frame (same as eval/flight_tracker.py): +x = target line, +y = LEFT of target line, +z up. Yards/mph for display, SI inside.
  face_deg / path_deg are azimuths in that frame (+ = toward +y = left of target line). face_to_path = face_deg - path_deg.

Two entry points:
  shot_from_launch(ball_mph, launch_deg, backspin_rpm, ...)   flight model only (this is the part validated against TrackMan averages)
  shot_from_club(club_mph, attack_deg, dynamic_loft_deg, ...) impact model + flight. The simple impact model OVER-predicts backspin
                                                              (see results/golf_simulator_validation.md); treat its spin/apex as indicative.
"""
from __future__ import annotations
import importlib.util, os
from dataclasses import dataclass, asdict
import numpy as np

_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "env", "ball_flight_analytic.py")
_s = importlib.util.spec_from_file_location("ball_flight_analytic", _p)
bf = importlib.util.module_from_spec(_s); _s.loader.exec_module(bf)   # loaded by path: avoids importing mujoco via the env package

MPS_TO_MPH = 2.23694
M_TO_YD = 1.09361
TEE_HEIGHT_M = 0.04
MODEL_LABEL = "model-based (analytic ball model), not measured"


@dataclass
class Shot:
    club_mph: float | None
    ball_mph: float
    smash: float | None
    launch_deg: float
    launch_dir_deg: float      # + = left of target line
    backspin_rpm: float
    sidespin_rpm: float        # + = curves LEFT (face closed to path), - = curves right (checked in tests)
    apex_yd: float
    carry_yd: float
    total_yd: float
    lateral_carry_yd: float    # + = left
    lateral_total_yd: float
    land_angle_deg: float | None
    hang_s: float | None
    label: str = MODEL_LABEL

    def as_dict(self): return asdict(self)

    def row(self) -> str:
        s = "-" if self.smash is None else f"{self.smash:.2f}"
        c = "-" if self.club_mph is None else f"{self.club_mph:.1f}"
        return (f"club {c} mph | ball {self.ball_mph:.1f} mph | smash {s} | launch {self.launch_deg:.1f} deg | spin {self.backspin_rpm:.0f} rpm | "
                f"apex {self.apex_yd:.0f} yd | carry {self.carry_yd:.0f} yd | total {self.total_yd:.0f} yd | lateral {self.lateral_total_yd:+.1f} yd (+left)")


def _flight(v0, w0, club_mph, wind, fairway) -> Shot:
    r = bf.simulate([0, 0, TEE_HEIGHT_M], v0, w0, wind=wind, fairway=fairway)
    if r["carry"] is None: raise RuntimeError("ball never landed within t_max")
    bs = r["ball_speed"]
    return Shot(club_mph=club_mph, ball_mph=bs * MPS_TO_MPH, smash=(bs * MPS_TO_MPH / club_mph) if club_mph else None,
                launch_deg=r["launch"], launch_dir_deg=r["launch_dir"], backspin_rpm=r["backspin_rpm"], sidespin_rpm=r["sidespin_rpm"],
                apex_yd=r["apex"] * M_TO_YD, carry_yd=r["carry"] * M_TO_YD, total_yd=r["total"] * M_TO_YD,
                lateral_carry_yd=r["lat_carry"] * M_TO_YD, lateral_total_yd=r["lat_total"] * M_TO_YD,
                land_angle_deg=r["land_angle"], hang_s=r["hang"])


def shot_from_launch(ball_mph, launch_deg, backspin_rpm, launch_dir_deg=0.0, sidespin_rpm=0.0, club_mph=None, wind=(0, 0, 0), fairway=True) -> Shot:
    v = ball_mph / MPS_TO_MPH; el, az = np.radians(launch_deg), np.radians(launch_dir_deg)
    v0 = v * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    w0 = np.array([0.0, -backspin_rpm * 2 * np.pi / 60, sidespin_rpm * 2 * np.pi / 60])   # backspin = -y rotation (matches bf.impact output)
    return _flight(v0, w0, club_mph, wind, fairway)


def shot_from_club(club_mph, attack_deg=-1.3, dynamic_loft_deg=13.0, path_deg=0.0, face_deg=0.0, e=0.83, m_club=0.20, mu=0.22,
                   wind=(0, 0, 0), fairway=True) -> Shot:
    cs = club_mph / MPS_TO_MPH; a, p, l, f = (np.radians(x) for x in (attack_deg, path_deg, dynamic_loft_deg, face_deg))
    vc = cs * np.array([np.cos(a) * np.cos(p), np.cos(a) * np.sin(p), np.sin(a)])
    n = np.array([np.cos(l) * np.cos(f), np.cos(l) * np.sin(f), np.sin(l)])
    v0, w0 = bf.impact(vc, n, m_club=m_club, e=e, mu=mu)
    return _flight(v0, w0, club_mph, wind, fairway)


def monte_carlo(n=200, seed=0, **kw):
    """Shot-to-shot spread around a nominal shot_from_club; kw: nominal inputs plus optional *_sd for club_mph, attack_deg, dynamic_loft_deg, path_deg, face_deg."""
    rng = np.random.default_rng(seed)
    nom = dict(club_mph=113.0, attack_deg=-1.3, dynamic_loft_deg=13.0, path_deg=0.0, face_deg=0.0)
    sd = {k: kw.pop(k + "_sd", 0.0) for k in list(nom)}
    nom.update({k: v for k, v in kw.items() if k in nom}); extra = {k: v for k, v in kw.items() if k not in nom}
    shots = [shot_from_club(**{k: nom[k] + rng.normal(0, sd[k]) for k in nom}, **extra) for _ in range(n)]
    return shots


if __name__ == "__main__":
    print(shot_from_launch(167, 10.9, 2686, club_mph=113).row())
    print(shot_from_club(113, -1.3, 13).row())
