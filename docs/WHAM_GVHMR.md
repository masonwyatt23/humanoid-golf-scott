# Swapping MediaPipe for WHAM / GVHMR

`data/process_video.py` is a *proxy*: single-view MediaPipe landmarks -> crude joint
angles. WHAM and GVHMR recover **world-grounded SMPL body motion** (global orientation,
root translation, foot contact), which is what an imitation pipeline really wants.

| | MediaPipe (current) | WHAM | GVHMR |
|---|---|---|---|
| Output | 33 landmarks (image/world-ish) | SMPL pose+shape, world traj., contact | SMPL-X/SMPL, gravity-view world frame |
| Camera motion | not handled | handled (SLAM) | handled |
| Pelvis/thorax rotation (X-factor) | not measurable | yes (SMPL joint rotations) | yes |
| Licence | Apache-2.0 | research licence; **SMPL licence is non-commercial** | research; SMPL licence |
| GPU | optional | yes | yes |

Check each repo's current licence and the SMPL/SMPL-X licence before any commercial use.
Upstream repos: `yohanshin/WHAM`, `zju3dv/GVHMR`. Follow their install READMEs (they
need CUDA, SMPL model files you register for, and their checkpoints) -- not vendored here.

## Contract your replacement must satisfy

Write `data/references/<name>_processed.npz` (the loader globs `*_processed.npz`) with:

| key | shape | notes |
|---|---|---|
| `joints` | (n, 11) | **degrees**, column order in `data/generate_synthetic_scott.py` docstring |
| `dt` | scalar | seconds per row (real time; resample to 0.01 to match synthetic) |
| `time` | (n,) | optional |
| `club_head` | (n, 3) | optional (WHAM/GVHMR don't give it either) |
| `pelvis_rot_deg`, `thorax_rot_deg`, `x_factor_deg`, `lateral_sway_m` | (n,) | optional but recommended; same meaning as in the synthetic generator so `compute_swing_metrics` works |

## Steps

1. Run WHAM/GVHMR on the clip (set the true capture fps for slow-mo footage, then
   resample to real time; see `--capture-fps` in `process_video.py`). Save its
   `.pt`/`.npz` of SMPL `global_orient`, `body_pose` (axis-angle, 21 joints), `trans`.
2. Convert SMPL axis-angle -> rotation matrices (`scipy.spatial.transform.Rotation`).
3. Map to the 11 humanoid joints. SMPL joint indices: pelvis 0, L/R hip 1/2, L/R knee
   4/5, L/R ankle 7/8, spine 3/6/9, L/R shoulder 16/17, L/R elbow 18/19, L/R wrist 20/21.
   - elbow/knee: flexion angle of the hinge axis; hips/shoulders: project the relative
     rotation onto the MuJoCo hinge axes in `env/models/humanoid_golf.xml`;
   - pelvis yaw = yaw of `global_orient`; thorax yaw = yaw of the spine-3 chain (joint 9)
     composed with the pelvis; `x_factor_deg = |thorax_yaw - pelvis_yaw|` relative to
     address; `lateral_sway_m` = root `trans` along the target line minus address pose.
4. Smooth/resample with `process_video.smooth` / `process_video.resample` (reuse them).
5. Save the `.npz` per the contract; `ReferenceDataset` picks it up unchanged.
6. Run `compute_swing_metrics`-style checks: tempo ratio ~2.3-3.5, X-factor 40-65 deg,
   etc. Reject clips that fail (bad pose, camera cuts).

A minimal adapter should live in `data/process_wham.py` exposing the same
`process_landmarks`-like function (`smpl_to_reference(...) -> dict`); keep `process_video.py`
as the fallback when no GPU is available.

Retargeting caveat: the MuJoCo humanoid has no torso/pelvis yaw joint and only 11 DoF,
so rotation channels are kept as *extra rewards/metrics*, not direct joint targets,
until the model gains a spine.
