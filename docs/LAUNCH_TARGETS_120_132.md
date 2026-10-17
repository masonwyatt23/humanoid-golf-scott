# Driver targets at 120 / 130 / 132 mph club speed, and published smash/spin limits (public sources only)

Data: `data/references/launch_targets_120_132_limits.json` (built by `python -m data.launch_targets_120_132`; test `tests/test_launch_targets_120_132.py`).
Nothing here measures Mason (120+ mph is self-reported, unverified). No Instagram-derived or Mason-clip data; no video used.
**Basis tags:** published = read from a source; interpolated/extrapolated = computed here; model = repo analytic ball model (not a source); *unverified* = rests on a search snippet.

## Target table (centre strike, AoA 0, optimizer-type)
| Club mph | Ball mph | Smash | Launch deg | Spin rpm | Carry yd | Total yd | Basis |
|---|---|---|---|---|---|---|---|
| 120 | 178 | 1.483 | 9.3 | 2890 | 296 | 340 (TrackMan total-optimizer row; Foresight window 327-365) | published (TrackMan optimizer PDF, fetched) |
| 130 | 194.0 | 1.492 | 8.0 | 2790 | 326 | none as a point; Foresight window 373-399 (interpolated) | **extrapolated** from TrackMan 105 & 120 mph rows (chart ends at 120) |
| 132 | 197.2 | 1.494 | 7.8 | 2770 | 332 | none as a point; Foresight window 378-403 (interpolated) | **extrapolated** |

Foresight optimized-driver table (fetched; windows): 124 mph: ball 180, launch 10-14, spin 2700-1700, carry 320-349, total 340-386. 131 mph: ball 190 (smash 1.45), launch 10-14, spin 2600-1600, carry 342-372, total 378-401. 138 mph: ball 200, spin 2500-1500, carry 360-389, total 381-418. At 130/132 interpolated: ball ~189/191, carry 337-367 / 344-374 (see JSON).
Vendors disagree by ~4-5% in ball speed at 130 mph (194 vs 189). The extrapolated smash 1.49 sits at the physical ceiling, so treat 194/197 as upper bounds.

Measured evidence above 113 mph (**unverified, search snippets**): R&A report on TrackMan World Long Drive men's average: 145 mph, ball 214, smash 1.48, launch 11.2, spin 2789, carry 352 yd. Single practice shot (Burke, 2016): 141.3 mph, ball 211, smash 1.50, AoA +8, spin 1850, 409 yd total. PGA Tour (fetched): 113 mph / 167 / 1.48 / 10.9 / 2686 / 275 yd carry.

Model (env `ball_flight_analytic`, assumed dynamic loft 9-10, NOT a source): K=4.0, e=0.845 gives 130 mph: ball 192-193, smash 1.48, launch 7.5-8.3, spin 2540-2820, carry 310-311, total 336-339; 132 mph: carry 314-316, total 341-344. Env default (K=3.5, e=0.83) is ~1.47 smash, spin 2900-3270, carry 302-310. So model carry is ~5% below the extrapolated TrackMan 326/332.

## Limits for the gate
Smash (published): driver hard ceiling **1.50**, expected centre-strike max 1.49 (TrackMan: "near 1.50"; tour 1.49; scratch amateurs 1.49; 5/10 HCP 1.45; average 1.44; bogey 1.43). Physics (Tutelman, unverified snippet): (1+COR)/(1+m/M), COR 0.83, 200 g head, 46 g ball -> 1.482 at 5 deg loft, ~1.465 at 10 deg. Other clubs (tour averages, not caps): 3W 1.48, hybrid ~1.46, 6i 1.39, 7i 1.33, 9i 1.28, PW 1.23-1.25. Max by club type is NOT published as a rule; a non-driver ceiling is derived (average +0.03-0.05).
Spin, driver: tour 2545-2686, long-drive average 2789, USGA ball test 2520, optimizer/Foresight window ~1600-2900 at 120-132 mph, amateur Combine ~2990-3190. Other clubs: 3W 3655-3801, 7i 6585-7097, 9i 8647-9018, PW 9304-10399. Gate suggestion for driver at 120-132 mph (derived, not published): PASS 1800-3000, WARN 1500-1800 / 3000-3500, FAIL <1200 or >4000; smash FAIL >1.50, WARN >1.49 or <1.30.

Sources: see `sources` in the JSON (TrackMan optimizer PDF, Foresight help-centre tables, TrackMan smash-factor blog, TrackMan PGA Tour PDF, R&A WLD report, golf.com Burke, Tutelman smash pages, USGA TPX3006). Unverified ones are flagged there.
