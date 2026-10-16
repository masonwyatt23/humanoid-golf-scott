"""Sequencing/style prior from CMU mocap golf swings (subject 64, trials 1-10).
Data: mocap.cs.cmu.edu -- "The data used in this project was obtained from mocap.cs.cmu.edu.
The database was created with funding from NSF EIA-0196217."  (converted files stay inside the project; not redistributed)

Only the *shape* of the thorax-yaw and wrist-hinge curves is used (time-normalised per phase: backswing
takeaway->top, downswing top->impact, follow-through). CMU tempo (~1.7:1, slow, no ball) is NOT used as a speed target.
"""
from pathlib import Path
import numpy as np

REF = Path(__file__).resolve().parent.parent / "data" / "references"
_N = 101


def _resample(x, t, t0, t1):
    tt = np.linspace(t0, t1, _N)
    return np.interp(tt, t, x)


def load_profiles(trials=range(1, 11)):
    """returns dict of mean normalised curves for backswing/downswing/follow: thorax yaw (0..1 at top), pelvis yaw, wrist hinge."""
    out = {k: {"back": [], "down": [], "follow": []} for k in ("thorax", "pelvis", "wrist")}
    for i in trials:
        f = REF / f"cmu_64_{i:02d}.npz"
        if not f.exists():
            continue
        d = np.load(f, allow_pickle=True)
        t = d["time"]; top, imp = float(d["events"][0]), float(d["events"][1])
        take, fin = float(d["takeaway_s"]), float(d["finish_s"])
        sig = {"thorax": -d["thorax_rot_deg"], "pelvis": -d["pelvis_rot_deg"], "wrist": np.abs(d["wrist_hinge_deg"])}
        for k, x in sig.items():
            base = np.interp(take, t, x)
            peak = np.interp(top, t, x) - base
            if abs(peak) < 1e-6:
                continue
            xn = (x - base) / peak
            out[k]["back"].append(_resample(xn, t, take, top))
            out[k]["down"].append(_resample(xn, t, top, imp))
            out[k]["follow"].append(_resample(xn, t, imp, fin))
    return {k: {p: np.mean(v, axis=0) for p, v in segs.items() if len(v)} for k, segs in out.items()}


class StylePrior:
    def __init__(self):
        self.p = load_profiles()

    def value(self, name, segment, u):
        c = self.p[name][segment]
        return float(np.interp(np.clip(u, 0, 1), np.linspace(0, 1, len(c)), c))
