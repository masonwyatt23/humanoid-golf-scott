#!/usr/bin/env python3
"""Opt-in model variants derived from env/models/humanoid_golf_v3.xml (v3 itself is never modified).
  humanoid_golf_v4_power.xml  HYPOTHETICAL power tier: wrist damping 0.5, wrist peak torque 120 N m (gear 20 x forcerange 6), chest_yaw range +-60 deg
                              (stand-in for pelvis+spine yaw; a separate pelvis DOF is NOT added: leg/qpos ordering, holds and obs layout depend on the current joint order)
  humanoid_golf_h12wrist.xml  realism contrast: H1-2-like wrist torque 25 N m (forcerange 1.25; Unitree H1-2 wrist roll/pitch/yaw 19-30 N m class), v3 damping, chest range +-45.
"""
import re
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "env" / "models"; src = (D / "humanoid_golf_v3.xml").read_text()
def variant(name, wr_force, wr_damp, chest):
    s = src
    s = s.replace('<joint name="right_wrist" type="hinge" axis="0 1 0" range="-120 120"/>', f'<joint name="right_wrist" type="hinge" axis="0 1 0" range="-120 120"' + (f' damping="{wr_damp}"' if wr_damp is not None else '') + '/>', 1)
    s = s.replace('forcerange="-3.000 3.000" joint="right_wrist" gear="20"', f'forcerange="-{wr_force:.3f} {wr_force:.3f}" joint="right_wrist" gear="20"', 1)
    s = s.replace('range="-45 45" damping="1.0" armature="0.5"', f'range="-{chest} {chest}" damping="1.0" armature="0.5"', 1)
    assert s != src; (D / name).write_text(s); print("wrote", name)
variant("humanoid_golf_v4_power.xml", 6.0, 0.5, 60)
variant("humanoid_golf_h12wrist.xml", 1.25, None, 45)
