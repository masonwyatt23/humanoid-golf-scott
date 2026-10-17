# Tracking reward: reference gaps for a script-free swing

Read-only review of `env/residual_golf_env.py` (`_load_track_shapes`, `_track_score`) and the committed references; nothing in `env/`, `eval/`, `train/` was changed. Code reading only, not run. Items marked [unverified] are inferences.

## What the tracking reward uses today
`track_set="unified_v1"` builds, from train-split entries only, three **normalised 1-D shapes** (shoulder pitch for Mason, thorax yaw and wrist hinge for MultiSense/CMU), resampled between takeaway and impact with the top as an anchor, and scores the policy with `exp(-MSE/0.15)`. The window boundaries come from the **script** (`t_hold`, `t_back`, `t_pause`, `t_down`) on the policy side, so the reward is not script-free: it assumes a scripted event timeline. No club, ball, force, or full-body-pose term is tracked. (The sim steps at 0.02 s vs reference dt 0.01 s; see `docs/REFSET_TIMING_AUDIT.md`.)

## Gaps and what closes each

| Gap | Where it stands | What closes it |
|---|---|---|
| **Club-head trajectory in CMU** | CMU `.npz` have `has_club_head` false and no `club_head`; MultiSense likewise; Mason has `club: unknown`. Only synthetic references carry a club path. | CMU subject 64 has no club marker in the converted files; derive a *hand-based* proxy only. A real club path needs optical mocap with club markers (own capture) or sim-side club kinematics from the humanoid itself. Do not fabricate a club path. |
| **Events keys** | CMU/MultiSense: `events=[top, impact]` plus `takeaway_s`, `finish_s`. Mason: no `events` or `takeaway_s`; uses `t_takeaway/t_top/t_impact` in video time with a per-file `t_start_in_video` offset. The env loader branches by source. Mason impact is landmark-inferred and early vs hand low point (+0.07 s median). | Add a common `events` (+`takeaway_s`) to Mason files (in sim time, offset-corrected) and a schema test; adopt the hand-low-point-relative impact; ~30 fps limits to +-0.05 s. 240 fps data (below) fixes the resolution. |
| **Impact face/path** | Unavailable (`docs/IMPACT_FACE_PATH_AVAILABILITY.md`). | Launch monitor per swing. |
| **Club speed** | Mason's 120+ mph is self-reported and not derivable from video; MultiSense has launch-monitor club speed (89-103 mph) per swing but only for P19/P20/P22 and not at tour speed. Peak hand speed in torso lengths/s is not mph. | Launch-monitor club speed for Mason swings; MultiSense P10/P14 (not yet converted) for a wider speed range. The 130-150 mph ladder remains our own extrapolation (`docs/research_350yd_profile.md`). |
| **Ground reaction** | None in any reference. MultiSense has foot-pressure sensors (the converter uses joint positions only) [unverified whether usable]. CMU has no force data. | Convert MultiSense foot pressure if licensing (counsel_required) clears; otherwise force plates/pressure insoles in Mason's own session. |
| **Ball launch** | Only MultiSense scalar launch-monitor values (club/ball speed, carry). No launch angle, spin, or face data in any reference; the sim ball model is uncalibrated (`docs/research_impact_physics.md`). | Launch-monitor logging per swing; apply the impact-physics calibration. |
| **Left-handed fast swings** | Mason val/train swings are left-handed but video-derived at an unmeasured speed. MultiSense/CMU are right-handed originals mirrored; CMU is slow recreational (tempo ~1.8). No measured fast left-handed mocap exists. | Mason 240 fps capture with launch monitor. Mirroring is a stopgap and `mason_v2_p1_s11` handedness is unconfirmed (`docs/P1_S11_HANDEDNESS_CHECK.md`). |
| **Mason pelvis/thorax, X-factor, sequencing** | Unavailable from the current video (`mason_target_features.json` caveats); the yaw and wrist shapes come only from MultiSense/CMU, the shoulder shape only from Mason. | Two-view 240 fps capture, or IMUs. |
| **2-view 240 fps data** | Not yet captured. Current video is ~30 unique fps, mostly down-the-line, with monocular depth that is model-driven. | Follow `docs/FILMING_PROTOCOL.md`: 20-50 swings, two synchronised views at 240 fps, a launch monitor, left-handed, club specs logged. Triangulated pose then gives true 3-D joints. |
| **Licensing for the above** | MultiSense is `counsel_required`; CMU has an acknowledgment and a no-standalone-resale clause (see manifest fields and `docs/UNIFIED_V1_LICENSE_AUDIT.md`). | Counsel sign-off; own-capture data is the clean path. |

## Priority for a script-free tracking reward
1. Common events schema across sources and sim-time indexing (cheap, local).
2. Launch-monitor numbers for the next Mason session (closes club speed, face/path, ball launch together).
3. 240 fps two-view capture (closes event timing, sequencing, depth).
4. Ground-force and club-trajectory data are only obtainable from new capture.
