# Dynamic loft as env parameters, and a cited lateral-dispersion reference (public sources only)

Data: `data/references/loft_env_params_dispersion.json` (build: `python -m data.loft_env_params_dispersion`, ~3 min, then `--assemble`; test `tests/test_loft_env_params_dispersion.py`). Extends `docs/TARGETS_130MPH_350YD_AND_LOFT.md` (not repeated).
Written 2026-10-17 (America/New_York). No Instagram-derived or Mason-clip data, no video. Mason's 120+ mph is self-reported, **unverified**.
Tags: **model** (repo `env/ball_flight_analytic.py`, read-only import; NOT a source) | **code** (read from env source) | published | *unverified* (snippet/secondhand). No MuJoCo rollout was run: the loft_deg -> env launch mapping still needs a policy rollout.

## 1. Env parameters that set launch / spin (code reading)
| Param | Where | What it does | Suggestion |
|---|---|---|---|
| `loft_deg` | `HumanoidGolfEnv.__init__` (humanoid_golf_env.py ~L117) | rotates the head box about y (static face tilt); None keeps the XML euler (3 deg) | launch moves ~0.85 deg per deg of dynamic loft at fixed AoA (**model**). Dynamic loft = loft_deg + shaft/wrist offset (no published conversion, so unknown). To go 12.6 -> ~8 deg: cut ~5-6 deg, then re-measure by rollout |
| AoA (no direct param) | scripted swing (q_fin, timing, wrist release), `ball_x`, `ball_x_noise` | launch ~ AoA + 0.85-0.9 x spin loft | AoA +2..+4 at 130 mph. Arc geometry: moving the ball dx shifts AoA ~ dx/R (R pivot-to-head ~1.6-1.8 m **assumed**): 0.05 m ~ 1.7 deg; `ball_x_noise` 0.03 m ~ +-1 deg (derived, *unverified*) |
| `ball_dz`, `tee_height` | L376, L400: ball z = 0.021 + tee + ball_dz | where on face/arc the strike lands; `impact_model.dz0` (-0.019) centres the strike-height term | do not use as a loft knob; keep strike within ~0.02 m of dz0 |
| `impact_model` {gain, k_off, dz0, spin_k, k_side} | ~L475-485 | launch DIRECTION comes from MuJoCo contact (not overwritten); gain scales ball speed; spin rpm = spin_k x ball speed x sin(launch+2 deg), clip 0-6000; sidespin = k_side x dy | spin_k 130 (v4yaw) gives ~1500-2000 rpm at 8-9 deg launch (table); for ~2200-2500 use spin_k ~150-165 (arithmetic). Lower launch lowers env spin by itself: re-check the 1800-3000 rpm gate |
| `elev_target_deg`, `elev_weight` | residual_golf_env.py L30, L336, L373 | reward bump centred at **12.5 deg** (default); fallback rpm 1500+70 x elev | **Most likely why the power tier sits at 12.6.** Set `elev_target_deg` ~8-9 to pull launch down (model carry optimum at 130 mph is 10-11 deg, so 9-10 is the no-cost zone) |
| wrist lead (`style_lead`, `wr_lead` ~0.06 s) | residual_golf_env.py L65, L127 | PD lag shifts effective wrist w at contact; more cocked (w>0) = hands ahead = less loft | keep w in the contact band 0.173-0.564 x elbow_rad +-0.1 (earlier repo analysis, not re-derived); do not force forward lean (driver needs +AoA). Re-measure dynamic loft after the lead fix |
| face angle | no param; falls out of club path/forearm rotation | start line ~76% face / 24% path (published) | log face angle and path at contact |
| K, e | analytic model / `impact_k` | K 5.6 lowers spin ~30% and adds 3-6 yd carry; e caps smash <= 1.50 | K=5.6 (repo impact doc), e=0.845 |

## 2. Param -> launch / spin / carry / total (model, e=0.845, K=4.0; spin shown as analytic / env-formula spin_k=130)
A = baseline power tier (AoA +5, DL 14.5). DL = dynamic loft. All rows **model**. K=5.6 rows are in the JSON.
| mph | Config | Launch | Spin rpm | Smash | Carry | Total |
|---|---|---|---|---|---|---|
| 100 | A AoA+5 DL14.5 | 12.9 | 2063 / 2213 | 1.481 | 235 | 263 |
| 100 | D AoA+3 DL10.5 | 9.2 | 1631 / 1680 | 1.488 | 219 | 253 |
| 100 | F AoA+2 DL9.5 | 8.2 | 1631 / 1531 | 1.488 | 213 | 248 |
| 100 | E AoA 0 DL9.0 | 7.5 | 1955 / 1422 | 1.483 | 210 | 244 |
| 120 | A | 12.9 | 2475 / 2655 | 1.481 | 294 | 320 |
| 120 | B AoA+5 DL12.5 | 11.2 | 1957 / 2370 | 1.488 | 296 | 325 |
| 120 | D | 9.2 | 1957 / 2016 | 1.488 | 290 | 320 |
| 120 | F | 8.2 | 1957 / 1838 | 1.488 | 286 | 317 |
| 120 | E | 7.5 | 2346 / 1706 | 1.483 | 282 | 311 |
| 130 | A | 12.9 | 2681 / 2877 | 1.481 | 317 | 343 |
| 130 | C AoA+5 DL11.0 | 10.0 | 1698 / 2344 | 1.493 | 324 | 354 |
| 130 | D | 9.2 | 2121 / 2184 | 1.488 | 319 | 348 |
| 130 | F AoA+2 DL9.5 | 8.2 | 2121 / 1991 | 1.488 | 317 | 346 |
| 130 | G AoA+4 DL9.0 | 8.2 | 1416 / 2001 | 1.495 | 317 | 350 |
| 130 | E AoA 0 DL9.0 | 7.5 | 2541 / 1848 | 1.483 | 311 | 339 |
Full grid (B..G, both K, all three speeds) is in the JSON.
**Answer to "7.8 deg without losing carry":** carry-neutral only at about 130 mph with K=4.0 and AoA +2..+4 with DL ~9-9.5 (F, G: 0 yd vs A; E at AoA 0 loses 6). At K=5.6 those rows lose 8-16 yd, at 120 mph 7-12 yd, at 100 mph 22-32 yd. Launch 9-10 (C, D) at 130 mph is free (+3..+8 yd) and 10-11 is the model optimum. Recommend: first target 9-10 deg (elev_target_deg ~9.5, DL ~10.5-11, AoA +3..+5), treat 7.8 as a 130 mph-only stretch. G's spin (1416 analytic) is near the unphysical floor (*unverified*, see targets doc).
Published cross-check: PING (Wood et al. 2018) driver vertical launch ~83% +-8% toward dynamic loft (*unverified* excerpt), consistent with the 0.85 slope above.

## 3. Lateral dispersion reference (driver; nothing published is specific to 100-120 mph)
| Number | Value | Source (URL) | Status |
|---|---|---|---|
| Direction sigma, long tee shots, Pro | **4.0 deg** (d0.75 297 yd) = ~21 yd 1-sigma at 300 yd | Broadie, Columbia, https://business.columbia.edu/sites/default/files-efs/pubfiles/2851/broadie_wscg_v_200802.pdf | fetched. All long tee shots (not only driver), includes curve and roll, c. 2008 |
| same, amateurs by scoring avg | Am1 (70-83) **5.4**, Am2 6.4, Am3 8.1 deg; fit sigma = -0.0315 d0.75 + 13.223 | same | fetched |
| Start line | ball starts **76% +-8%** toward face angle (driver; 7-iron 69, wedge 61); vertical 83% +-8% toward dynamic loft | Wood et al. (PING) 2018, https://www.mdpi.com/2504-3900/2/6/249 | excerpt read (*unverified* full text) |
| Curve | PGA driver 275 yd carry: face-to-path 2 deg ~ 19 yd, 5 deg ~ 44 yd; 1 deg ~ 12 yd at 300 yd | TrackMan, https://www.trackman.com/blog/face-to-path | *unverified* (snippet) |
| 1 deg target-line error | ~4 yd side dispersion at 250 yd | Bliss & Langdown, https://oro.open.ac.uk/107777/ (via Pebble summary) | *unverified* |
| Width, 3/5/7 hcp, GCQuad | ~70 yd total (+-35) | https://www.australiangolfdigest.com.au/what-this-fascinating-consistency-test-revealed-about-single-digit-handicaps/ | *unverified*, 3 golfers |
| Width, ~scratch | 68.6 yd (n=20 mat), "65-70" attributed to DECADE | https://practical-golf.com/golf-ball-control | *unverified*, secondhand |
| Tour/scratch 18-22 / 25-30 yd "spread" | - | https://t5golf.com/what-is-a-good-driver-dispersion/ | **LOW CONFIDENCE, do not use** (no data, conflicts with the rows above) |
| Fairways | men 0-4.9 hcp 49.3% hit, 12.0% wayward | Arccos via Golfweek, https://golfweek.usatoday.com/story/sports/golf/equipment/2025/05/10/arccos-driving-distance-report-no-change-in-yards-for-club-golfers/83534228007/ | *unverified* |
Not found: any published face-angle sigma or club-path sigma in degrees for scratch/+3 or tour drivers (TrackMan publishes none; the Korean TrackMan study of 15 pros reports only CVs). **Do not cite a face/path sigma as published.**

### Stock scatter push (model, calibrated; usable)
Start = 0.76 face + 0.24 path; curve = 9.0/275 yd per deg face-to-path per yd of carry; face and path independent, equal sigma s; s calibrated so lateral 1-sigma = D tan(Broadie sigma) at 297 yd. Carry D from config F, K=4.0.
| Group | s (face = path, deg) | start-line sigma | 100 mph (D 213) 1-sigma / 95% width | 120 mph (D 286) | 130 mph (D 317) |
|---|---|---|---|---|---|
| Pro (Broadie 4.0 deg) | 1.29 | 1.03 deg | 14.9 yd / 59 yd | 20.0 / 80 | 22.1 / 89 |
| Low-handicap amateur (Am1 5.4 deg; nearest published to +3) | 1.75 | 1.39 deg | 20.1 / 80 | 27.1 / 108 | 29.9 / 120 |
Use: for a +3 stock scatter start with face sigma ~1.5 deg and path sigma ~1.5 deg (between the rows), lateral 1-sigma ~20-25 yd at 120-130 mph. 95% width = 4 sigma (normal assumption; real misses are heavier-tailed, the published widths of 65-70 yd agree with 3-4 sigma of ~20 yd). Caveats (*unverified*): equal/independent split is assumed; real face and path are positively correlated, so true face/path sigmas are larger than calibrated; Broadie's sigma includes roll and non-driver tee shots; Mason (+3) mapped to Am1 by judgement. Scale with carry: lateral yd ~ proportional to D at fixed angles.

## 4. Open-data BC prior options (reused; nothing new)
Unchanged from `docs/TARGETS_130MPH_350YD_AND_LOFT.md` section 3: CMU subject 64 = **counsel_required**, MultiSenseGolf = **counsel_required**, BONES-SEED = **counsel_required** (not in repo, never commit), 100STYLE cc_by (locomotion only), AMASS/GolfDB/HumanML3D/Motion-X **EXCLUDED** from commercial, LAFAN1 noncommercial. Recommended: reference tracking + residual policy over BC from 10 slow demos. Standing flag: `data/provenance.py` still tags `cmu_mocap` commercial_ok=True and converted CMU npz are in the public repo (needs Mason/counsel decision).

## 5. Unverified items
All model rows; the loft_deg-to-dynamic-loft offset; AoA-vs-ball_x geometry (R assumed); spin_k 150-165 suggestion; the face/path sigma split; TrackMan curve yards, PING 76/83% (excerpts), Bliss-Langdown 4 yd/deg, GCQuad 70 yd, DECADE 65-70 yd; Broadie sigma applicability to 100-120 mph driver carry; Mason = Am1 mapping; Mason's 120+ mph. Sources and caveats in the JSON.
