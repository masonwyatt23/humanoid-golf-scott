# Handedness / mirroring convention

Default `handedness="right"` (all existing runs). `handedness="left"` mirrors the simulation about the target-line
vertical plane (x-z plane; x = target direction, z = up, y = lateral):

| Quantity | Right (default) | Left (mirror) |
|---|---|---|
| Joint naming | `right_*` = TRAIL arm/leg (club arm), `left_*` = LEAD arm/leg | unchanged: `right_*` still means trail |
| Pitch joints (axis y: shoulder pitch, elbow, wrist, hips, knees, ankles) | as is | **no sign change** (rotation about y is invariant under y-mirror up to nothing in the swing plane) |
| Roll / yaw joints (axis x or z: `right_shoulder_roll`, `left_shoulder_roll`, `chest_yaw`) | as is | **sign flips** (`chest_yaw` target * -1 is implemented in `ResidualGolfEnv`) |
| Ball y offset on reset randomisation | +y | sign flipped |
| Reported `ball_lateral`, `launch_direction` | + = +y | multiplied by -1 so + is the same golfer-relative side for both hands |
| Pelvis/thorax yaw angles in references (`pelvis_rot_deg`, `thorax_rot_deg`) | backswing negative | backswing positive for a mirrored golfer; the Data Agent's references use trail/lead roles (CMU converter: right_* = trail), so for a left-hander build them with trail/lead assigned and DO NOT swap columns; the env flips yaw sign |

Reference mapping rule for the Data Agent: express every reference in golfer roles (trail/lead), not physical left/right.
For a left-handed player the physical right limbs are the LEAD limbs; store them in the `left_*` (lead) columns.
Only yaw/roll/lateral signs differ between handedness; the physical simulation is otherwise identical because the
model is a single-plane swing about the y axis.

Not implemented: a physically mirrored XML (the geometry is already symmetric about y except the arm being on +y side
of the torso at shoulder x offset, which does not affect the planar swing); the left-hand option only adjusts signs above.
