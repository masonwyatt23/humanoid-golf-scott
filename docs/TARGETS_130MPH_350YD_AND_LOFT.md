# 130 mph club speed -> 350 yd targets, dynamic-loft guidance, and open-data BC priors (public sources only)

Data: `data/references/targets_130mph_350yd_and_loft.json` (built by `python -m data.targets_130mph_350yd`, ~2 min; test `tests/test_targets_130mph_350yd.py`). Extends `docs/LAUNCH_TARGETS_120_132.md` (reuse; not repeated).
Written 2026-10-17 (America/New_York). No Instagram-derived or Mason-clip data, no video. Mason's 120+ mph is self-reported and **unverified**.
**Basis tags:** published | interpolated | extrapolated | model (repo `env/ball_flight_analytic.py`, read-only, NOT a source) | derived | *unverified* (search snippet).

## 1. Target table, 130 mph club speed
| Row | Ball mph | Smash | Launch | Spin rpm | Carry yd | Total yd | Basis |
|---|---|---|---|---|---|---|---|
| TrackMan-style, AoA 0 | 194.0 | 1.492 | 8.0 | 2790 | 326 | none published | **extrapolated** from TrackMan optimizer 105/120 mph rows; upper bound |
| Foresight optimized window | ~189 | ~1.45 | 10-14 | 2650-1600 | 337-367 | 373-399 | interpolated between published rows (124, 131 mph); vendor-theoretical window |
| Model, AoA 0, SL 8 (K=4.0 / K=5.6) | 193.2 | 1.486 | 6.7 / 7.0 | 2261 / 1615 | 310 / 310 | 340 / 343 | model |
| Model, AoA 0, SL 10 (K=4.0 / K=5.6) | 192.2 | 1.478 | 8.3 / 8.8 | 2821 / 2015 | 310 / 316 | 336 / 346 | model |
| Model, AoA +4, SL 8 (K=4.0 / K=5.6) | 193.2 | 1.486 | 10.7 / 11.0 | 2261 / 1615 | 321 / 325 | 349 / 356 | model |
| Model, AoA +4, SL 10 (K=4.0 / K=5.6) | 192.2 | 1.478 | 12.3 / 12.8 | 2821 / 2015 | 314 / 324 | 340 / 352 | model |
| WLD average (145 mph, not 130) | 214 | 1.48 | 11.2 | 2789 | 352 | - | published, *unverified* (R&A report, snippet) |
SL = spin loft = dynamic loft - AoA. Model rows e=0.845; K=4.0 is the requested interim, K=5.6 is the repo impact doc's recommendation (spin fits the tour point). Full grid (AoA -2..+10, SL 8-14, plus 134-138 mph scan) is in the JSON.

### What combination gives 350 total vs 350 carry at 130 mph
- **350 total:** *not* reached at AoA 0 (model ~336-340; TrackMan-extrapolated carry 326 + ~14 roll). It is reached in the model with **smash ~1.48-1.49, spin loft ~8-10, AoA about +4 or more**, i.e. launch ~11-13 deg and spin ~1600-2300 (K=5.6: 352-356 total) or 2260-2820 (K=4.0: 340-349, borderline). At AoA 0 the model needs ~134 mph (350.5 total, SL 8). Foresight's window (373-399 total at 131 mph) says it is inside vendor-optimal territory.
- **350 carry:** *not* reached at 130 mph by the model (max ~325 carry) or the extrapolated TrackMan row (326). Only the Foresight upper window (342-372, interpolated) covers it. Published real-player evidence of 350+ carry is at 145 mph (WLD, *unverified*). Treat as a stretch: smash >=1.49, AoA >= +4, spin loft <= 8-9, spin ~2000-2400, ball ~193+.
- **8-10 deg launch is not the 350 recipe:** with AoA >= +4, launch 8-10 means spin loft 4-7, where the analytic model's spin collapses (<~1100 rpm, negative at SL 6 / AoA +8) and real balls rarely go below ~1500 rpm (*unverified*, no published floor). 8-10 deg at AoA 0 needs spin loft ~9-11 (see section 2) and gives ~336-346 total. If the humanoid is to launch 8-10 deg, the realistic total at 130 mph is ~335-345.

## 2. Dynamic loft / AoA / spin loft / launch / spin (published relations)
- **Spin loft ~= dynamic loft - AoA** (TrackMan; strictly a 3-D angle, face-to-path small) *unverified snippet*.
- **Launch ~= AoA + SL*(0.96 - 0.0071*SL)** (Tutelman 3-D launch, fetched; he compared to live TrackMan, "very consistent"). TrackMan: dynamic loft matters more than AoA for launch.
- **Spin** is set mainly by spin loft and club speed (TrackMan). Model slope ~280 rpm per deg SL at 130 mph (K=4.0), ~200 at K=5.6. Do **not** use 160*V*sin(SL).
- **Smash** falls with spin loft: ~(1+e)/(1+m/M)*cos(SL); model 1.486 at SL 8, 1.478 at 10, 1.469 at 12, 1.457 at 14.
- **Tour driver** (TrackMan): dynamic loft 12.8 (*snippet*), AoA -0.9, launch 10.4-10.9, spin 2545-2686, smash 1.48-1.49. TrackMan: positive AoA "is a must" for max driver distance.
- **Launch needed (derived, Tutelman relation):**

| Target launch | AoA 0 | AoA +2 | AoA +4 | AoA +6 |
|---|---|---|---|---|
| 8 deg | SL 8.9 (dyn 8.9) | 6.6 (8.6) | 4.3 (8.3) | 2.1 (8.1) |
| 10 deg | SL 11.4 (dyn 11.4) | 8.9 (10.9) | 6.6 (10.6) | 4.3 (10.3) |
(each cell: spin loft (dynamic loft)). Reading: for 8-10 deg launch, dynamic loft only needs to be ~8-11 *whatever the AoA*, but spin loft falls as AoA rises; to cut spin you raise AoA, not cut dynamic loft.
- **Dynamic-loft modifiers (published, mostly *snippets*):** shaft bend adds ~2 (stiff) to ~5 deg (flexible) (Tutelman); delivered loft change with shaft depends on butt-ahead-of-ball and grip twist (MacKenzie 2015, r=.87 for grip twist); a high-face hit adds loft, 10 mm low = ~2 deg less (TrackMan; face roll); cupped/bowed lead wrist adds/removes loft (Tutelman). **No published per-degree conversion from forward shaft lean to driver dynamic loft** (so do not invent one). Coaching sources say driver wants neutral or slightly behind shaft, not forward lean, because the strike must be upward (*unverified*). Lead wrist ~20 deg flexion at driver contact in 12 female pros (Zhang et al., via snippet, *unverified*).

### Implications for the humanoid env
- Env wrist: w=0 is a 90 deg L; w>0 more cocked. Contact target `w ~ 0.173 - 0.564*elbow_rad (+-0.1)` is the earlier repo analysis (not re-derived). More cocked at contact = hands further ahead = less loft; fully released/bowed = more loft. Because the driver needs +AoA, aim for the w_contact band (slightly released) and set loft with the head, rather than forcing forward lean.
- Order of knobs: (1) static `loft_deg` ~8-9 (driver 8-12 per TrackMan help centre, *snippet*); (2) AoA +2..+5 via sequencing and ball position; (3) keep wrist in the w_contact band; (4) measure launch/spin per shot and compare to section 1 before changing rewards.
- Env dynamic loft is not logged: `loft_deg` is a static head-box rotation about y (`env/humanoid_golf_env.py` ~line 120). Dynamic/spin loft need the face normal and club-head velocity at contact (log them). The wrist PD lag (~0.06 s lead fix) shifts effective w at contact; re-measure dynamic loft after that fix.
- Reward ideas (derived, not published): penalise spin loft outside ~7-11 deg and launch outside 8-14; reward AoA +2..+6; keep the smash <=1.50 gate.

## 3. Open-data options for a non-scripted policy (behaviour-cloning prior)
| Source | In repo | License flag | Use / feasibility |
|---|---|---|---|
| **CMU subject 64** (10 swings) | yes, `cmu_64_01..10.npz`, `env/style_prior.py` | **counsel_required** (page text: free for all uses, commercial products OK, "may not resell ... even in converted form", ack required; home vs FAQ wording differ) | One unnamed right-handed subject, no ball/club-head, 120 Hz -> dt 0.01, 11 joint columns, downswing 0.43-0.60 s (tour ~0.25), hand speed 3.5-4.6 m/s. Retarget to the 11-column env model **already done**. 10 demos is too few for BC; use as tracking reference/RSI, sequencing-shape prior (already in style_prior), or residual base clip. Reaching 130 mph needs ~2x downswing time-compression: check actuator limits first. Mirror for a left-hander (HANDEDNESS.md). |
| MultiSenseGolf | yes (28 swings, weight 0.2) | counsel_required | Amateurs, no wrist data; second human prior. |
| BONES-SEED | no | counsel_required (<$1M startup clause, attribution, no public mirrors; never commit) | General humanoid prior, not golf. |
| 100STYLE | no | cc_by | Locomotion only. |
| AMASS / GolfDB / HumanML3D / Motion-X | no | **EXCLUDED** from commercial | Do not use. |
| LAFAN1 / Unitree retarget | no | noncommercial | Do not use. |
| Residual-policy + reference tracking (own code) | yes (`env/residual_golf_env.py`) | none | Recommended over pure BC: DeepMimic/BeyondMimic-style tracking + task reward (research_imitation_rl_methods.md R01-R07). |
**Flag (not changed):** `data/provenance.py` tags `cmu_mocap` as `commercial_ok=True` and the converted CMU `.npz` files are tracked in the public repo. That conflicts with keeping CMU `counsel_required` and with the stricter "no resale of converted data" reading; the Repo Agent/Mason may want to decide.

## 4. Unverified items
All 130/132 mph TrackMan-style values (extrapolated); any 130 mph total as a point; Foresight 130 windows (interpolated, vendor-theoretical); WLD 145 mph and Burke shot (snippets); TrackMan spin-loft/dynamic-loft/club-data pages and Pebble, Tutelman shaft-bend, MacKenzie, coaching-site claims (snippets); shaft-lean-to-loft conversion (none published); model spin below SL ~8 (unphysical); model carry ~5% below the extrapolated TrackMan row; the w_contact formula; Mason's 120+ mph.
Sources (URLs) are in the JSON `sources`.
