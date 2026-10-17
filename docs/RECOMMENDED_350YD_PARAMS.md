# Recommended parameter set for the 350 yd attempt, 7.8 vs 9.7 deg verdict, low-dispersion shaping (public/scripted data only)

Data: `data/references/recommended_350yd_params.json` (build `python -m data.rec_350yd_params`; test `tests/test_recommended_350yd_params.py`). Extends `docs/LOFT_ENV_PARAMS_AND_DISPERSION.md` and `docs/TARGETS_130MPH_350YD_AND_LOFT.md` (not repeated).
Written 2026-10-17 (America/New_York). No Instagram-derived or Mason-clip data, no video, no `imit_private` files used. Mason's 120+ mph is self-reported, **unverified**.
Tags: **measured** (env run, scripted zero-residual, impact gain 1.20, n=40, club 132.4 mph; `results/power_loft_scan1_s25.json`) | **model** (repo analytic ball model, not a source) | derived | *unverified*.
Env distance/carry are in **metres** (env reward code works in metres; yd = m x 1.0936). The env has no roll: distance = carry.

## 1. Measured loft scan (the "loft -27" gate family)
| loft_deg | launch deg | carry m (yd) | lateral std m |
|---|---|---|---|
| -31 | 12.58 | 298.8 (326.8) | 2.05 |
| -29 | 11.15 | 299.1 (327.1) | 2.05 |
| **-27** | **9.72** | **292.7 (320.1)** | 1.87 |
| -25 | 8.30 | 274.4 (300.1) | 1.52 |
| -23 | 10.02 (std 13.7) | 235.2 | 2.52 (**cliff, mixed mishits**) |
Linear fit over -31..-25: launch = -9.54 - 0.714 x loft_deg (0.71 deg per deg of loft_deg; interpolated -28 -> 10.4, -26 -> 9.0, -24 -> 7.6). The loft -27 gate runs use impact gain 1.20, spin_k 130, `elev_weight` 0.0 (so the 12.5 deg default elev target was inactive there; launch is set by `loft_deg`), and report smash ~1.48-1.50 and backspin ~2360 rpm (Trainer-reported; that gate file is held, not cited here). The env spin formula 130 x v_ball x sin(launch+2 deg) gives ~2340 rpm at 9.7 deg, consistent.

## 2. Verdict: 7.8 deg vs ~9.7 deg
**Target 9.7-10.4 deg, not 7.8.**
- 7.8 deg is loft_deg ~ -24.3 (fit), just beyond the last good measured point (-25: 8.3 deg, carry already 24.7 m / 8% below peak) and next to the -23 failure. Reaching it by loft alone costs carry in the env.
- Model (docs/LOFT_ENV_PARAMS_AND_DISPERSION.md): at 130 mph 7.5-8.2 deg is carry-neutral only with K=4.0 and AoA +2..+4; it loses 8-16 yd at K=5.6; the model optimum is 10-11 deg.
- -27 (9.72 deg) costs only 6.4 m (2%) vs the -29 peak; -28 interpolates to ~10.4 deg for ~3 m.
- To get lower launch without losing carry, the lever is more AoA / less spin loft, not less loft_deg (that needs a swing change, unmeasured).

## 3. ONE recommended set (130-132 mph club speed)
| Param | Value | Basis |
|---|---|---|
| `loft_deg` | **-28** | interpolated between measured -29 and -27 (launch ~10.4, carry ~296 m = 324 yd); **fallback -27 is measured** (9.72 deg, 292.7 m) |
| `impact_gain` | **1.20** | measured gate smash ~1.48-1.50 (Trainer-reported); the 1.50 smash cap leaves no room above ~1.22; do not raise |
| `elev_target_deg` | **10.0** with `elev_weight` 1.0 | replaces the 12.5 default; model optimum 10-11 deg. Only matters if `elev_weight` > 0 |
| `spin_k` | **130** (unchanged) | env spin ~2340-2410 rpm at 10 deg, inside the 1800-3000 gate; no need for the 150-165 suggested earlier (that was for 7-8 deg launch) |
| `ball_x`, `ball_x_noise`, `ball_dz`, `tee_height` | 0.396, 0.003, -0.008, 0.04 | unchanged from the loft -27 runs |
Predicted at 130 / 132 mph, AoA +4, dynamic loft 11.5 (**model**, launch ~10.2-10.6):
| mph | K | ball mph | smash | launch | spin analytic / env formula | carry yd | total yd |
|---|---|---|---|---|---|---|---|
| 130 | 4.0 | 193.2+ | 1.488 | 10.2 | 2121 / 2376 | 321.6 | 350.1 |
| 130 | 5.6 | | 1.488 | 10.6 | 1515 / 2452 | 324.7 | 355.7 |
| 132 | 4.0 | | 1.488 | 10.2 | 2153 / 2412 | 326.8 | 355.1 |
| 132 | 5.6 | | 1.488 | 10.6 | 1538 / 2490 | 330.4 | 361.2 |
**350 yd reading:** 350 yd *total* = 320 m. Measured env carry at 132.4 mph is 293-299 m (320-327 yd carry), so a 350 yd total is plausible if roll of ~25-30 yd is added (model 350-361; roll is **model-only**, the env has none). 350 yd *carry* (320 m) is 21-27 m above the best measured carry and above the model maximum (~333 yd): **stretch, unverified**. Whether "350" in the project means carry or total decides if more is needed.
**Risks / unverified:** loft_deg -28 outcome is interpolated (4-point fit; run one 40-shot scan at -28 before committing); the cliff at -23 means do not go above -25; measured scan is the scripted zero-residual swing, a learned policy will differ; model rows are not a source; smash near 1.50 sits on the gate limit (fails above 1.50); 1.20 vs the older 1.28 gain is the Trainer's own choice.

## 4. Reward shaping for a low-dispersion learned policy
Add per-shot terminal terms, each `-w x min((x/sigma)^2, 9)` (cap at 3 sigma). They add to the existing carry reward (~24 per shot at `carry_cap` 120). All weights and sigmas are **derived starting points, not published**.
| Term | Definition | sigma | w | Anchor |
|---|---|---|---|---|
| start line | ball start azimuth minus target, first 5 ms of ball velocity | 1.0 deg | 1.5 | PING: start = 0.76 face + 0.24 path (snippet); model start-line sigma 1.03 pro, 1.39 Am1 |
| face angle at impact | face yaw minus target line at first contact | 1.5 deg (anneal from 3.0) | 1.0 | stock +3 ~1.5 deg between model rows 1.29 pro / 1.75 Am1; **no published face sigma exists** |
| club path | club-head velocity azimuth at contact minus target | 1.5 deg | 0.5 | as above |
| face-to-path | face - path | 2.0 deg | 0.5 | TrackMan: 2 deg ~19 yd, 5 deg ~44 yd curve at 275 yd (snippet, *unverified*); elite within ~1 deg |
| lateral miss | existing `lat_weight`, set `lat_angular=True` (percent of carry, cap 30) | - | `lat_weight` 1.0 | Broadie pro direction sigma 4.0 deg = 7% of carry = ~21 yd at 300 yd; 1 pro-sigma miss costs ~7 |
| launch | existing `elev_target_deg` 10, `elev_weight` 1.0 | - | 1.0 | model optimum 10-11 deg |
Context: the scripted swing's env lateral std is 1.5-2.5 m (0.3-0.5 deg at 293 m), ~10x tighter than human references (model 1-sigma at 320 yd carry: pro ~22 yd, +3 ~26 yd). The aim of a learned policy is to stay near scripted tightness, so keep `residual_scale` small and tune the terms so one scripted-level miss costs < 0.3. Do not target human scatter.
**Logging gap:** the env does not log face yaw, club path or dynamic loft at contact. The first four terms need the face normal and club-head velocity at first contact added (env/ is read-only for the Data Agent; Trainer to do). Mason's own face/path proxies are Instagram-derived and are not used here.

## 5. BC-prior options (licence tags kept)
| Source | Tag | Use |
|---|---|---|
| scripted zero-residual swing + residual policy (own code) | none | **recommended base**: BC/DAgger-regularise the residual toward zero plus shaping |
| CMU subject 64 | counsel_required | tracking reference/RSI only; `data/provenance.py` now tags it needs_counsel / commercial_ok=False (retagged 2026-10); open item for Mason/counsel: keep or untrack the tracked `cmu_64_*.npz` |
| MultiSenseGolf | counsel_required | low weight, no wrist data |
| BONES-SEED | counsel_required | not in repo; never commit |
| 100STYLE | cc_by | locomotion only |
| AMASS, GolfDB, HumanML3D, Motion-X | EXCLUDED commercial | do not use |
| LAFAN1 | noncommercial | do not use |

## 6. Unverified items
loft_deg -28 result; all model rows and roll; face/path sigmas (not published); shaping weights/scales; TrackMan F2P yards and PING 76% (snippets); learned-vs-scripted scatter; env units = metres (code reading, confirm with Trainer). Sources: Broadie (Columbia pdf, fetched), PING/Wood 2018 (MDPI), TrackMan face-to-path blog; URLs in the JSON.
