import json
from pathlib import Path

import numpy as np

from data import audit_refset_timing as A

ROOT = Path(__file__).resolve().parents[1]


def _swing(n=200, top=0.9, imp=1.2, dt=0.01):
    t = np.arange(n) * dt
    j = np.zeros((n, 11))
    # arm angle moves fastest around impact
    j[:, 0] = 100 * np.tanh((t - imp) / 0.08)
    return {"joints": j, "dt": dt, "time": t, "events": np.array([top, imp]), "takeaway_s": np.array(0.2)}


def test_clean_synthetic_has_no_flags():
    m, f = A.audit_arrays(_swing(), A.joint_limits())
    assert f == [], (m, f)


def test_detects_offset_events():
    d = _swing(); d["events"] = np.array([0.9, 1.2 - 0.4])  # 0.4 s early impact like the old bug
    _, f = A.audit_arrays(d)
    assert "impact_not_at_arm_peak" in f


def test_detects_nan_dt_and_time():
    d = _swing(); d["joints"][5, 2] = np.nan; d["dt"] = 0.02
    _, f = A.audit_arrays(d)
    assert "nan" in f and "dt_mismatch" in f and "time_axis" in f


def test_events_out_of_range_and_order():
    d = _swing(); d["events"] = np.array([1.5, 1.0])
    assert "events_order" in A.audit_arrays(d)[1]
    d["events"] = np.array([0.9, 5.0])
    assert "events_out_of_range" in A.audit_arrays(d)[1]


def test_mason_events_derived_from_video_times():
    d = {"t_top": 10.5, "t_impact": 10.8, "t_start_in_video": 10.0}
    top, imp, src = A.get_events(d)
    assert abs(top - 0.5) < 1e-9 and abs(imp - 0.8) < 1e-9


def test_resample_for_control_halves_frames_and_keeps_duration():
    j = np.stack([np.linspace(0, 100, 201)] * 11, 1)
    r = A.resample_for_control(j, 0.01, 0.02)
    assert len(r) == 101 and abs(r[-1, 0] - 100) < 1e-9 and abs(r[50, 0] - 50) < 1e-9


def test_joint_limits_parsed():
    L = A.joint_limits()
    assert L["right_elbow"] == (0.0, 150.0) and len(L) == 11


def test_real_set_mirror_pairs_and_events_consistent():
    rep = A.run()
    assert rep["n_files"] == 50
    for f in rep["files"]:
        for bad in ("mirror_pair_mismatch", "mirror_on_load_events", "nan", "dt_mismatch", "time_axis", "events_order", "shape", "deg_rad_mismatch"):
            assert bad not in f["flags"], (f["path"], f["flags"])
    assert rep["env_control_dt_check"]["checked"] in (True, False)


def test_committed_json_matches_schema():
    p = ROOT / "data" / "references" / "refset_timing_audit.json"
    r = json.loads(p.read_text())
    assert r["n_files"] == len(r["files"]) == 50 and "flag_counts" in r


def test_protocol_naming_parses_with_ingest():
    from data.ingest_mason_swings import filename_tokens
    assert filename_tokens("mason_20261024_driver_dtl_007") == {"club": "driver", "view": "dtl"}
    assert filename_tokens("mason_20261024_driver_fo_007") == {"club": "driver", "view": "fo"}


def test_session_log_template_has_protocol_columns():
    hdr = (ROOT / "data" / "templates" / "session_log.csv").read_text().splitlines()[0].split(",")
    for c in ("club_speed_mph", "ball_speed_mph", "smash", "launch_deg", "spin_rpm", "attack_angle_deg",
              "club_path_deg", "face_angle_deg", "carry_yd", "tee_height_in", "shaft_flex"):
        assert c in hdr
