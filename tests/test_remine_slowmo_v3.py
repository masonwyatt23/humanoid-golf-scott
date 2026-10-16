import glob
import json
import os

import numpy as np

from data import remine_slowmo_v3 as m

REFS = os.path.join(os.path.dirname(__file__), "..", "data", "references")


def _synthetic(k):
    """address 1 s, backswing 0.5k s up to +0.5 torso above shoulder, downswing 0.17k s, finish; 30 fps."""
    t = np.arange(0, 1 + 0.5 * k + 0.17 * k + 1.0, 1 / 30)
    hy = np.full_like(t, -1.2)
    a, top, imp = 1.0, 1.0 + 0.5 * k, 1.0 + 0.67 * k
    up = (t >= a) & (t <= top)
    hy[up] = -1.2 + 1.7 * np.sin(0.5 * np.pi * (t[up] - a) / (top - a)) ** 2
    dn = (t > top) & (t <= imp + 0.3)
    hy[dn] = 0.5 - 1.7 * np.clip((t[dn] - top) / (imp + 0.3 - top), 0, 1)
    sp = np.abs(np.gradient(hy, t)) * 2.0
    return t, hy, sp, (a, top, imp)


def test_find_swings_scale_invariant_tempo():
    r = []
    for k in (1.0, 5.0):
        t, hy, sp, (a, top, imp) = _synthetic(k)
        sw = m.find_swings(t, hy, sp)
        assert len(sw) == 1
        s = sw[0]
        assert abs(s["top"] - top) < 0.1 * k + 0.05
        r.append((s["top"] - s["takeaway"]) / max(1e-6, s["impact"] - s["top"]))
    assert 1.0 < r[0] < 4.0 and 1.5 < r[1] < 4.5  # synthetic truth 2.94; coarse (1-frame takeaway/impact error at k=1)


def test_v3_files_tagged_and_slowmo_metadata():
    files = sorted(glob.glob(os.path.join(REFS, "mason_v3_*_slowmo.npz")))
    assert files
    for f in files:
        d = np.load(f, allow_pickle=True)
        assert str(d["license_class"]) in ("self_owned", "unknown")
        assert bool(d["slow_motion"]) and float(d["slowdown_factor_min"]) <= float(d["slowdown_factor_est"]) <= float(d["slowdown_factor_max"])
        assert int(d["downswing_unique_frames"]) >= m.MIN_DOWN_FRAMES
        assert not bool(d["mirrored"]) and str(d["view"]) in ("down_the_line", "face_on", "oblique")
        assert abs(float(d["unique_fps"]) - 30) < 3
        assert len(d["time_real_est"]) == len(d["time"])


def test_cadence_audit_json():
    j = json.load(open(os.path.join(REFS, "mason_cadence_audit.json")))
    assert j["swings"]
    assert max(s["unique_fps"] for s in j["swings"]) < 45  # nothing close to 60 unique fps
