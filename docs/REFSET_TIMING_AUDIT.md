# Unified refset timing audit (unified_v1, 50 entries)

Run: `python -m data.audit_refset_timing [--print]` -> `data/references/refset_timing_audit.json` (per-file flags + metrics). Tests: `tests/test_refset_timing_audit.py`. Env/eval/train were only read, never edited. Thresholds are heuristic (unverified rules of thumb), listed in the JSON.

## Result summary
| Check | Result |
|---|---|
| NaNs, shape (n,11), deg/rad consistency, dt==0.01, uniform time axis starting at 0 | **Clean, 50/50** |
| Events order/range (events=[top, impact]; Mason derived as t_*-t_start_in_video, time axis starts at 0 = t_start_in_video, verified) | Clean except the weight-0 slow-mo clip (events in stretched video time, as already documented) |
| Mirrored copies (28 MultiSense `*_mirrored`) keep identical time/events/frame count and joints equal the swapped/negated original | **Clean** |
| CMU mirror-on-load keeps events and length | **Clean** |
| Durations (downswing 0.12-0.60 s, backswing 0.35-1.8 s) | Fine except slow-mo clip. Mason v2 downswings are 0.13-0.33 s, MultiSense ~0.23-0.30 s, CMU 0.43-0.60 s (slow recreational) |
| Impact event vs peak arm angular speed (cols 0,1,2,4; tolerance 0.12 s) | MultiSense: all within 0.08 s. CMU: 4/10 flagged (impact event 0.14-0.16 s *before* arm peak; arm-speed proxy is crude for slow swings). Mason: 6/11 flagged, lag -0.24..+0.21 s, consistent with ~30 fps video and 2D pose noise, not a systematic offset (mean of the signed lags is near zero) |
| Large frame jumps (>25 deg per 0.01 s) | 11 Mason files (all of the video-derived ones with unreliable legs: hip/ankle/shoulder pitch swings from landmark flips/interpolated legs) |
| Joint ranges vs `env/models/humanoid_golf.xml` (parsed read-only, +5 deg tolerance) | 47/50 exceed somewhere. MultiSense: hip pitch up to ~30 deg beyond +-60 in 26 files (a real address forward bend is ~hip flexion 60-90; the env range is narrow). CMU: ankles 19-25 deg over +-40. Mason: ankles up to 35 deg, right_shoulder_pitch 1 file 83 deg, wrists up to 32 deg beyond +-90 in 4 files (video noise). |

## The one real timing risk found (env, not data)
`env/humanoid_golf_env.py` uses a fixed **control dt of 0.02 s** (`substeps = round(0.02/timestep)`), but `ref_idx = min(len-1, episode_steps)` indexes the reference **by step**, and `load_reference` keeps `dt` without resampling. All unified_v1 references are **dt = 0.01 s**. Unless the trainer resamples first, the reference plays at **2x speed** (a 1.5 s swing is tracked in 0.75 s). This is the same family as the earlier ~0.4 s offset bug. Confirmed by a text scan only; I did not run the env, and I don't know whether the Trainer's current script pre-resamples (the JSON has `env_control_dt_check`).

Fix (owned by whoever owns env/): index by time, `ref_idx = round(episode_steps * ctrl_dt / ref_dt)`, or pre-resample with `data.audit_refset_timing.resample_for_control(joints, 0.01, 0.02)` (tested: halves frames, preserves duration). Also `club_head` and any events array must be handled the same way. I did not edit env/.

## Other findings
- `data.unified_refset.load_ref` returns no events, so trainers that want phase/impact alignment must read `events` (or Mason `t_*`) from the npz themselves; `data.audit_refset_timing.get_events(d)` does this uniformly.
- Joint range clipping: references beyond env limits are unreachable targets; consider clipping targets or widening hip/ankle ranges. That is a modelling decision, not a data bug.
- Mason timings come from ~30 fps video: event resolution is ~0.033 s and the v2 downswing (~0.13-0.17 s) is shorter than tour values (~0.25-0.35 s, general knowledge, unverified); likely edited/sped-up feed clips (see MASON_VS_PROFILES.md). Do not treat Mason absolute durations as ground truth until the 240 fps session.
- Caveat: flags are screening heuristics; no flag proves a bug.
