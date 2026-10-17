import glob, json, os
import numpy as np
import pytest
from data import mason_impact_geometry as g

REFS = os.path.join(os.path.dirname(__file__), "..", "data", "references")
JSON = os.path.join(REFS, "mason_impact_geometry_targets.json")
needs = pytest.mark.skipif(not glob.glob(os.path.join(REFS, "mason_v2_*.npz")), reason="no refs")


def _scene(n=240, fps=60.0, tk=0.5, top=1.1, imp=1.5, lowdelay=0.05):
    """Synthetic upright golfer: hips fixed, hands rise to top then drop to a low point `lowdelay` after impact."""
    t = np.arange(n) / fps
    hip = np.zeros((n, 3)); sh = hip + np.array([0, 1.0, 0])      # up = +y here
    up = np.where(t < tk, 0.0, np.where(t < top, (t - tk) / (top - tk), np.where(t < imp + lowdelay, 1 - (t - top) / (imp + lowdelay - top), 0.0)))
    hand = np.stack([-0.3 * up + 0.1, 0.1 + 1.0 * up - 0.0, np.zeros(n)], 1)
    hand[:, 1] = 0.1 + 1.0 * up
    lsh = sh + np.array([0.2, 0, 0]); lwr = hand.copy()
    return t, hand, hip, sh, lsh, lwr


def test_low_point_and_heights_and_unavailable():
    t, hand, hip, sh, lsh, lwr = _scene()
    f = g.geometry_features(t, hand, hip, sh, lsh, lwr, np.array([1.0, 0, 0]), (0.5, 1.1, 1.5),
                            up_axis=np.array([0, 1.0, 0]), address_n=20)
    assert f["low_point_t_minus_impact_s"] == pytest.approx(0.05, abs=0.02)
    assert f["hand_up_at_top"] > f["hand_up_at_impact"]
    assert f["hand_up_at_address"] == pytest.approx(0.1, abs=1e-6)
    assert len(f["hand_path"]["up"]) == g.NPATH
    assert f["hand_path"]["up"][0] == pytest.approx(0.0, abs=1e-6)       # relative to address
    f2 = g.geometry_features(t, hand, hip, sh, lsh, lwr, np.array([1.0, 0, 0]), (0.5, 1.1, 1.5),
                             up_axis=np.array([0, 1.0, 0]), address_n=2)
    assert f2["hand_forward_vs_address_at_impact"] == g.UNAVAIL
    assert f2["lead_arm_lean_delta_deg"] == g.UNAVAIL


def test_scale_invariance_and_determinism():
    t, hand, hip, sh, lsh, lwr = _scene()
    a = g.geometry_features(t, hand, hip, sh, lsh, lwr, np.array([1.0, 0, 0]), (0.5, 1.1, 1.5), up_axis=np.array([0, 1.0, 0]), address_n=20)
    k = 2.7
    b = g.geometry_features(t, hand * k, hip * k, sh * k, lsh * k, lwr * k, np.array([1.0, 0, 0]), (0.5, 1.1, 1.5), up_axis=np.array([0, 1.0, 0]), address_n=20)
    for key in ("hand_up_at_top", "hand_up_at_impact", "hand_tgt_at_impact", "lead_arm_lean_at_impact_deg"):
        assert a[key] == pytest.approx(b[key], abs=1e-9)
    assert json.dumps(a, sort_keys=True) == json.dumps(
        g.geometry_features(t, hand, hip, sh, lsh, lwr, np.array([1.0, 0, 0]), (0.5, 1.1, 1.5), up_axis=np.array([0, 1.0, 0]), address_n=20), sort_keys=True)


def test_stat_weighted_and_unavailable_strings():
    s = g._stat([1.0, 2.0, 3.0, "unavailable", None], [1, 1, 5, 1, 1])
    assert s["n"] == 3 and s["weighted_median"] == 3.0
    assert g._stat(["unavailable"])["median"] == g.UNAVAIL


def test_no_launch_angle_claim_in_json():
    out = g.build(REFS, "/nonexistent") if glob.glob(os.path.join(REFS, "mason_v2_*.npz")) else None
    if out is None:
        pytest.skip("no refs")
    for k in ("shaft_lean_deg", "launch_angle_deg", "dynamic_loft_deg", "attack_angle_deg"):
        assert out["unavailable"][k] == g.UNAVAIL
    assert "launch monitor" in out["unavailable"]["reason"]


@needs
def test_build_deterministic_and_license_filter():
    a = g.build(REFS, "/nonexistent"); b = g.build(REFS, "/nonexistent")
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    files = [p["file"] for p in a["mason"]["per_swing_v2"]]
    assert files and all("mirrored" not in f or f.endswith("_unmirrored.npz") for f in files)
    for f in files:
        assert bool(np.load(os.path.join(REFS, f), allow_pickle=True)["commercial_ok"])
    assert a["mason"]["n_swings_used_v2"] == len(files)
    # aggregate excludes slow-mo
    assert all(not p["slow_motion"] for p in a["mason"]["per_swing_v2"])


def test_commercial_filter_excludes(tmp_path):
    np.savez(tmp_path / "mason_v3_x_slowmo.npz", recommended=True, commercial_ok=False, handedness="left",
             native_footage=True, mirrored=False, partial=False)
    sel, v3 = g.select(str(tmp_path))
    assert v3 == []


@needs
@pytest.mark.skipif(not os.path.exists(JSON), reason="json not generated")
def test_committed_json_schema():
    j = json.load(open(JSON))
    assert j["schema"].startswith("mason_impact_geometry_targets")
    m = j["mason"]
    assert m["n_swings_used_v2"] >= 5
    assert j["unavailable"]["launch_angle_deg"] == "unavailable"
    assert m["aggregate_v2"]["low_point_t_minus_impact_s"]["n"] >= 5
    assert j["provenance"]["raw_video_in_json"] is False
    assert "launch monitor" in " ".join(j["caveats"])
