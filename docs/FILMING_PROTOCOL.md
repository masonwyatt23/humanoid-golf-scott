# Filming protocol: Mason's 240 fps two-angle session

Goal: 20-50 driver swings with (a) high-frame-rate two-view video and (b) launch-monitor numbers per swing, so pose/tempo/sequencing can be tied to real club speed. Current feed footage is ~30 fps, re-encoded and often edited, so it cannot measure X-factor, sequencing or attack angle (see docs/MASON_VS_PROFILES.md). Camera numbers below are practical defaults, not validated; adjust and record what you used.

## Gear
- 2 phones (iPhone: Camera > Slo-mo > **1080p at 240 fps**; 4K60 is a poor substitute). 2 tripods. Daylight or bright outdoor light; fixed shutter is automatic in slo-mo, so brightness is what protects against blur: avoid shade/dusk, don't film into the sun, wear contrasting clothes (no loose jacket; fitted top, long pants, plain shoes).
- Launch monitor (radar or camera-based) behind/beside the ball; note the model. Tape measure, 1 m rigid stick or 2 pieces of tape exactly 1.00 m apart, painter's tape, a clapper (or loud hand clap).
- Do NOT use Instagram/AirDrop-to-IG/screen recording. Transfer the **original** files (AirDrop to a Mac, USB, or iCloud original). Keep "Most Compatible"/HDR off. No stabilisation, no cinematic mode, no zoom (use 1x lens; move the tripod instead).

## Camera setup (you are left-handed)
| View | Position | Height | Distance | Framing |
|---|---|---|---|---|
| Down-the-line (DTL) | behind the ball on the target line, looking at the target | ~hip/hand height (~1 m) | ~3-4 m behind the ball | Whole body + full club and follow-through visible; ball at lower third |
| Face-on (FO) | square to the target line, facing your chest (you are left-handed, so your lead side is your right; just put the lens square-on) | ~hip height (~1 m) | ~3-4 m | Head to feet, club visible at the top; leave margin so arms never leave the frame |
Keep phones landscape, locked focus/exposure (long-press the screen on you at address), tripod level. Never move cameras during a session. Mark tripod feet and ball spot with tape so a second session matches.

## Calibration and sync (once per session, and again if anything moves)
1. Place the 1 m reference (stick/tape) at the ball position, perpendicular to each camera axis; film 3 s per camera. Note camera distance and height in the log header.
2. Both cameras roll, then **clap once in view of both** (clap sound + hands visible) at the start of every ~10-swing batch; the clap lets frames be aligned to ~1/240 s.
3. Start both cameras before address; keep rolling for the whole swing + 2 s after impact.

## Per-swing launch-monitor log (data/templates/session_log.csv)
Columns: swing_id, video_file_faceon, video_file_dtl, timestamp_local, club, head_loft_deg, club_length_in, shaft_flex, shaft_weight_g, grip, tee_height_in, ball_position, club_speed_mph, ball_speed_mph, smash, launch_deg, spin_rpm, attack_angle_deg, club_path_deg, face_angle_deg, carry_yd, total_yd, monitor_model, strike_quality_1to5, fatigue_1to5, notes.
Log what the monitor reports; leave blank (never guess) if a number is missing. Mark mishits (strike quality 1-2) rather than deleting them.

## Setup constants to write down once
- **Club**: head loft (stamped vs measured), length in inches, shaft flex + weight (g), grip type/size, head model, lie. Same driver for the whole session (a second club = a separate session id).
- **Tee height** (inches to ball centre vs crown) and **ball position** (e.g. "inside lead heel", marked with tape on the mat/ground). Keep both fixed unless that is the experiment.
- Surface (mat vs turf), indoor/outdoor, wind (rough), temperature. Left-handed: say so in the log header (handedness=left).

## Plan: 20-50 swings (suggest 40)
1. Warm-up 10-15 min, off-camera (your normal routine, some full-speed swings). Note what you did.
2. Block A (10 swings): ~90% effort, then rest 60-90 s between swings, 2-3 min every 5.
3. Block B (10 swings): max intent (your "120+" swings). Block C (10 swings): normal/commit swing. Block D (optional 10): any drill or feel change; label it in notes.
4. Take clap sync at the start of each block. Rate fatigue 1-5 every 5 swings; stop if it hits 4. Do not film more than ~50 swings (fatigue and quality drift).
5. Keep every swing including bad ones; a "practice swing" gets its own row with club speed blank.

## Naming (matches data/ingest_mason_swings.py)
`mason_<YYYYMMDD>_<club>_<view>_<NNN>.mov`, e.g. `mason_20261024_driver_dtl_007.mov` and `mason_20261024_driver_fo_007.mov`. The ingest script reads tokens `driver|wood|hybrid|iron|wedge|putter` and `dtl|fo|faceon|side` from the filename, the output becomes `data/references/mason_<stem>.npz`, and stems must be unique (duplicates are rejected). Same NNN across both views = same swing. Run with `--capture-fps 240` (or put `capture_fps` in `metadata.csv`); also set `handedness=left` there. Cut one clip per swing; raw videos stay out of git.

## Consent and license
All footage is of you, filmed by you (or a helper who agrees in writing that you own it), no bystanders, music or branded overlays. Tag as `license_class=self_owned`, `commercial_ok=True`, `provenance_source=mason_self_filmed`. If anyone else swings, get a signed release first and tag them separately. Launch-monitor exports are your own measurements; keep the monitor model in the log.

## Open items
Do not publish club-speed claims from video alone; the monitor number is the truth. Whether 240 fps 1080p is enough for MediaPipe at 3-4 m is untested here (unverified).
