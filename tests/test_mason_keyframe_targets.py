import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from data import mason_keyframe_targets as K
from data.mason_target_features import events_of

ROOT = Path(__file__).resolve().parents[1]
J = json.loads((ROOT / "data/references/mason_keyframe_targets.json").read_text())


def test_clip_selection_excludes_flagged_slowmo_and_mirrors():
    used = set(J["clips_used"])
    assert used and not used & {"mason_v2_p1_s11", "mason_v2_p2_s10", "mason_v3_p2_s03_slowmo", "mason_v2_p3_s09_unmirrored"}
    assert J["clips_aux_not_in_stats"] == ["mason_v2_p3_s09_unmirrored"]
    for n in used:
        d = np.load(ROOT / f"data/references/{n}.npz", allow_pickle=True)
        assert str(d["handedness"]) == "left" and not bool(d["mirrored"]) and bool(d["native_footage"])
        assert bool(d["handedness_verified"])


def test_json_is_reproducible(tmp_path):
    out = tmp_path / "o.json"
    subprocess.run([sys.executable, "-m", "data.mason_keyframe_targets", "--out", str(out)], cwd=ROOT, check=True, capture_output=True)
    assert json.loads(out.read_text()) == J


def test_keyframe_schema_and_floors():
    assert list(J["keyframes"]) == K.KEYFRAMES
    for k, kf in J["keyframes"].items():
        assert set(kf["joints"]) == set(K.JOINTS)
        for name, v in kf["joints"].items():
            assert v["unverified"] is True
            if v["usable"]:
                assert v["sigma_suggested_deg"] >= K.SIGMA_FLOOR_DEG
                lo, hi = v["tolerance_band_deg"]
                assert lo < v["median_deg"] < hi and v["n"] >= K.MIN_N
        # leg columns never rated above low where leg data is mostly interpolated
        for j in ("right_hip_pitch", "right_knee", "right_ankle", "left_hip_pitch", "left_knee", "left_ankle"):
            assert kf["joints"][j]["confidence"] == "low"


def test_events_ordered_on_joint_axis_and_inside_data():
    for n, ev in J["event_offsets_s"].items():
        assert ev["top"] < ev["impact"] < ev["finish"], n
        d = np.load(ROOT / f"data/references/{n}.npz", allow_pickle=True)
        assert ev["finish"] <= float(d["time"][-1]) + 1e-9 and ev["top"] > 0


def test_templates_shape_and_phase():
    for seg, t in J["templates"].items():
        assert t["n_points"] == K.SEG_N[seg] and t["phase"][0] == 0 and t["phase"][-1] == 1
        for j in K.JOINTS:
            assert len(t["median_deg"][j]) == len(t["sigma_deg"][j]) == t["n_points"]
            assert min(t["sigma_deg"][j]) >= K.SIGMA_FLOOR_DEG


def test_tempo_band_and_not_a_speed_target():
    lo, hi = J["tempo"]["tempo_ratio_recommended_band"]
    assert 1.5 < lo < hi < 5.0
    assert "NOT a speed target" in J["tempo"]["caveat"]
    assert J["x_factor_proxy_at_top"]["confidence"] == "low" and J["x_factor_proxy_at_top"]["unverified"]


def test_env_loader_offset_mismatch_is_real():
    """Documents why the env's Mason shoulder shape is mis-anchored: it indexes events with t_start_in_video only,
    ignoring the ~0.4 s joint-axis offset, so its 'top' lands after impact in most clips."""
    bad = 0
    for n in J["clips_used"]:
        d = np.load(ROOT / f"data/references/{n}.npz", allow_pickle=True)
        t = d["time"]; x = -d["joints"][:, 4]
        env_top = float(d["t_top"]) - float(d["t_start_in_video"])
        true_top = events_of(d, "mason")[1]
        i = lambda q: int(np.argmin(abs(t - q)))
        if abs(x[i(env_top)] - x[i(true_top)]) > 30:
            bad += 1
    assert bad >= 5


def test_reward_form_documented():
    r = J["reward_recommendation"]
    assert "exp(" in r["sparse_keyframe"]["form"] and "windowed" in " ".join(r["windowed_dense"]).lower() or r["windowed_dense"]
    assert "never by env step" in r["time_indexing"]
