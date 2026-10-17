import json, math
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
J = json.load(open(ROOT / "data/references/wrist_sign_mapping.json"))


def test_env_zero_is_L_not_straight():
    g = J["env_geometry"]["interior_forearm_club_deg_vs_wrist_rad"]
    assert g["+0.000"] == pytest.approx(90.0, abs=0.5)
    assert g["-1.571"] == pytest.approx(180.0, abs=0.5)
    assert g["+1.571"] == pytest.approx(0.0, abs=0.5)
    assert J["env_geometry"]["identical_v3_v4_power"]


def test_stored_0p977_cannot_make_contact():
    assert min(J["stored_impact_0p977"].values()) > 0.3


def test_mapping_signs_and_offset_agreement():
    m = J["mapping"]
    assert m["mason_v2_col3_unsigned"]["sign"] == 1 and m["cmu_col3_cocked_negative"]["sign"] == -1
    f = J["offset_fits_rad"]
    assert abs(f["mason_best_clip_impact"] - f["cmu_median_impact"]) < 0.15


def test_best_clip_impact_in_window_and_not_098():
    c = J["clips"]["mason_v2_p1_s06"]
    assert c["impact_inside_contact_window"] and c["env_impact_rad"] < 0
    assert abs(c["env_impact_rad"] - c["contact_wrist_at_this_elbow_rad"]) < 0.1


def test_contact_wrist_decreases_with_elbow():
    assert J["contact_wrist_vs_elbow_linear_fit"]["slope"] < -0.3


def test_script_reproduces_json():
    pytest.importorskip("mujoco")
    from data.wrist_sign_mapping import contact_wrist, load_env
    w, d, _ = contact_wrist(load_env(), 0.853)
    assert w == pytest.approx(J["contact_sweep"]["elbow_0.853"]["wrist_best_rad"], abs=0.03) and d < 0.06
