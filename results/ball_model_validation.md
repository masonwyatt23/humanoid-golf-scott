# Ball-model validation vs approximate published TrackMan-style driver averages

the evaluator protocol (flight_tracker / leaderboard) uses the MuJoCo-PHYSICS ball: MuJoCo rigid-body ball (m 0.046 kg, r 0.021 m geom) + env._apply_aero()
(quadratic drag Cd=0.26 constant, Magnus lift Cl=min(1.7*S, 0.30), S=r*w/v, rho=1.19, NO spin decay, no Reynolds-dependent Cd) + MuJoCo ground contact
(solref 0.002/1, friction 0.5, env ball_damping for rolling) -> carry = first ground touch, total = final rest/roll position. This script launches THAT ball with controlled
velocity/spin (calling the env's own _apply_aero + mj_step). The 'analytic' model (env/ball_flight_analytic.py, drag with spin-dependent Cd, Cl up to 0.45, spin decay 3%/s,
bounce/roll; its docstring says calibrated to TrackMan PGA driver averages) is used by analytic_ball training runs only; it is run on the same grid for comparison.

Reference: driver ~120 mph club / smash ~1.48 (~178 mph ball) / ~12 deg / ~2400 rpm backspin -> roughly 270-280 yd carry; ~130 mph club -> roughly 300+ yd carry (approximate published TrackMan-style averages, rounded). Tolerance: +-5% of that range.

## Anchor cases

| Case (club mph, smash, launch, rpm) | Model | Carry yd | Reference | Within tolerance |
|---|---|---|---|---|
| (120, 1.48, 12, 2400) | MuJoCo physics (evaluator) | 289 | approx. published TrackMan-style avg: ~270-280 yd carry | YES |
| (120, 1.48, 12, 2400) | analytic | 293 | approx. published TrackMan-style avg: ~270-280 yd carry | YES |
| (130, 1.48, 12, 2400) | MuJoCo physics (evaluator) | 312 | approx. published TrackMan-style avg: ~300+ yd carry | YES |
| (130, 1.48, 12, 2400) | analytic | 319 | approx. published TrackMan-style avg: ~300+ yd carry | YES |

## Sweep (carry / total in yards)

| club mph | smash | ball mph | launch | rpm | physics carry | physics total | physics apex m | analytic carry | analytic total | analytic apex m |
|---|---|---|---|---|---|---|---|---|---|---|
| 100 | 1.0 | 100 | 10 | 2000 | 110 | 785 | 5.7 | 104 | 142 | 5.5 |
| 100 | 1.0 | 100 | 10 | 2400 | 124 | 726 | 7.0 | 107 | 142 | 5.8 |
| 100 | 1.0 | 100 | 10 | 3000 | 135 | 630 | 9.3 | 109 | 142 | 6.1 |
| 100 | 1.0 | 100 | 12 | 2000 | 121 | 722 | 7.8 | 114 | 145 | 7.4 |
| 100 | 1.0 | 100 | 12 | 2400 | 133 | 648 | 9.4 | 116 | 146 | 7.7 |
| 100 | 1.0 | 100 | 12 | 3000 | 142 | 549 | 11.8 | 117 | 145 | 8.2 |
| 100 | 1.0 | 100 | 14 | 2000 | 130 | 646 | 10.0 | 122 | 150 | 9.5 |
| 100 | 1.0 | 100 | 14 | 2400 | 141 | 569 | 11.9 | 124 | 150 | 9.9 |
| 100 | 1.0 | 100 | 14 | 3000 | 147 | 476 | 14.4 | 124 | 149 | 10.3 |
| 100 | 1.48 | 148 | 10 | 2000 | 209 | 735 | 14.5 | 224 | 255 | 17.8 |
| 100 | 1.48 | 148 | 10 | 2400 | 230 | 600 | 18.7 | 225 | 253 | 19.0 |
| 100 | 1.48 | 148 | 10 | 3000 | 245 | 348 | 26.5 | 224 | 250 | 20.6 |
| 100 | 1.48 | 148 | 12 | 2000 | 220 | 594 | 18.6 | 232 | 261 | 22.2 |
| 100 | 1.48 | 148 | 12 | 2400 | 238 | 493 | 23.3 | 232 | 259 | 23.5 |
| 100 | 1.48 | 148 | 12 | 3000 | 248 | 325 | 31.3 | 230 | 255 | 25.0 |
| 100 | 1.48 | 148 | 14 | 2000 | 229 | 538 | 22.9 | 238 | 266 | 26.7 |
| 100 | 1.48 | 148 | 14 | 2400 | 243 | 431 | 28.0 | 237 | 263 | 28.0 |
| 100 | 1.48 | 148 | 14 | 3000 | 250 | 254 | 36.1 | 233 | 258 | 29.5 |
| 110 | 1.0 | 110 | 10 | 2000 | 131 | 779 | 7.2 | 128 | 164 | 7.2 |
| 110 | 1.0 | 110 | 10 | 2400 | 148 | 715 | 9.0 | 131 | 165 | 7.7 |
| 110 | 1.0 | 110 | 10 | 3000 | 161 | 568 | 12.4 | 133 | 164 | 8.2 |
| 110 | 1.0 | 110 | 12 | 2000 | 142 | 718 | 9.7 | 139 | 169 | 9.7 |
| 110 | 1.0 | 110 | 12 | 2400 | 157 | 641 | 11.9 | 140 | 169 | 10.1 |
| 110 | 1.0 | 110 | 12 | 3000 | 167 | 508 | 15.4 | 141 | 168 | 10.7 |
| 110 | 1.0 | 110 | 14 | 2000 | 152 | 627 | 12.4 | 147 | 174 | 12.2 |
| 110 | 1.0 | 110 | 14 | 2400 | 164 | 564 | 14.8 | 148 | 174 | 12.8 |
| 110 | 1.0 | 110 | 14 | 3000 | 172 | 403 | 18.5 | 148 | 173 | 13.4 |
| 110 | 1.48 | 163 | 10 | 2000 | 236 | 675 | 17.7 | 259 | 288 | 23.4 |
| 110 | 1.48 | 163 | 10 | 2400 | 258 | 519 | 23.0 | 259 | 287 | 25.1 |
| 110 | 1.48 | 163 | 10 | 3000 | 271 | 344 | 32.5 | 256 | 282 | 27.1 |
| 110 | 1.48 | 163 | 12 | 2000 | 247 | 572 | 22.4 | 265 | 294 | 28.6 |
| 110 | 1.48 | 163 | 12 | 2400 | 265 | 480 | 28.2 | 264 | 291 | 30.3 |
| 110 | 1.48 | 163 | 12 | 3000 | 273 | 248 | 37.9 | 260 | 285 | 32.3 |
| 110 | 1.48 | 163 | 14 | 2000 | 256 | 438 | 27.3 | 270 | 298 | 33.8 |
| 110 | 1.48 | 163 | 14 | 2400 | 269 | 321 | 33.5 | 267 | 294 | 35.5 |
| 110 | 1.48 | 163 | 14 | 3000 | 275 | 256 | 43.2 | 262 | 287 | 37.4 |
| 120 | 1.0 | 120 | 10 | 2000 | 152 | 789 | 8.9 | 154 | 187 | 9.4 |
| 120 | 1.0 | 120 | 10 | 2400 | 171 | 666 | 11.3 | 156 | 187 | 10.0 |
| 120 | 1.0 | 120 | 10 | 3000 | 185 | 534 | 15.8 | 157 | 185 | 10.8 |
| 120 | 1.0 | 120 | 12 | 2000 | 164 | 684 | 11.8 | 164 | 193 | 12.3 |
| 120 | 1.0 | 120 | 12 | 2400 | 180 | 599 | 14.6 | 165 | 193 | 13.0 |
| 120 | 1.0 | 120 | 12 | 3000 | 191 | 450 | 19.3 | 165 | 191 | 13.8 |
| 120 | 1.0 | 120 | 14 | 2000 | 173 | 620 | 14.9 | 171 | 199 | 15.4 |
| 120 | 1.0 | 120 | 14 | 2400 | 187 | 485 | 18.1 | 172 | 198 | 16.1 |
| 120 | 1.0 | 120 | 14 | 3000 | 195 | 334 | 22.9 | 172 | 196 | 17.0 |
| 120 | 1.48 | 178 | 10 | 2000 | 262 | 645 | 21.1 | 291 | 320 | 29.8 |
| 120 | 1.48 | 178 | 10 | 2400 | 283 | 468 | 27.4 | 289 | 317 | 31.9 |
| 120 | 1.48 | 178 | 10 | 3000 | 294 | 262 | 38.5 | 284 | 310 | 34.4 |
| 120 | 1.48 | 178 | 12 | 2000 | 272 | 568 | 26.4 | 296 | 324 | 35.7 |
| 120 | 1.48 | 178 | 12 | 2400 | 289 | 325 | 33.2 | 293 | 320 | 37.8 |
| 120 | 1.48 | 178 | 12 | 3000 | 296 | 277 | 44.4 | 287 | 313 | 40.1 |
| 120 | 1.48 | 178 | 14 | 2000 | 280 | 455 | 31.9 | 299 | 327 | 41.6 |
| 120 | 1.48 | 178 | 14 | 2400 | 293 | 335 | 39.1 | 295 | 322 | 43.6 |
| 120 | 1.48 | 178 | 14 | 3000 | 297 | 285 | 50.2 | 288 | 314 | 45.9 |
| 130 | 1.0 | 130 | 10 | 2000 | 173 | 751 | 10.8 | 179 | 211 | 12.0 |
| 130 | 1.0 | 130 | 10 | 2400 | 193 | 655 | 13.8 | 181 | 211 | 12.8 |
| 130 | 1.0 | 130 | 10 | 3000 | 208 | 475 | 19.5 | 182 | 209 | 13.9 |
| 130 | 1.0 | 130 | 12 | 2000 | 185 | 668 | 14.1 | 189 | 218 | 15.5 |
| 130 | 1.0 | 130 | 12 | 2400 | 202 | 571 | 17.6 | 190 | 217 | 16.3 |
| 130 | 1.0 | 130 | 12 | 3000 | 213 | 426 | 23.5 | 189 | 215 | 17.4 |
| 130 | 1.0 | 130 | 14 | 2000 | 194 | 565 | 17.7 | 196 | 224 | 19.1 |
| 130 | 1.0 | 130 | 14 | 2400 | 208 | 446 | 21.5 | 196 | 223 | 20.0 |
| 130 | 1.0 | 130 | 14 | 3000 | 216 | 289 | 27.5 | 195 | 219 | 21.1 |
| 130 | 1.48 | 192 | 10 | 2000 | 286 | 608 | 24.6 | 320 | 349 | 36.8 |
| 130 | 1.48 | 192 | 10 | 2400 | 307 | 430 | 31.9 | 317 | 345 | 39.3 |
| 130 | 1.48 | 192 | 10 | 3000 | 316 | 288 | 44.4 | 310 | 336 | 42.1 |
| 130 | 1.48 | 192 | 12 | 2000 | 295 | 484 | 30.4 | 323 | 352 | 43.3 |
| 130 | 1.48 | 192 | 12 | 2400 | 312 | 290 | 38.2 | 319 | 347 | 45.7 |
| 130 | 1.48 | 192 | 12 | 3000 | 317 | 296 | 50.8 | 312 | 337 | 48.5 |
| 130 | 1.48 | 192 | 14 | 2000 | 303 | 406 | 36.4 | 325 | 353 | 49.8 |
| 130 | 1.48 | 192 | 14 | 2400 | 315 | 298 | 44.6 | 320 | 347 | 52.2 |
| 130 | 1.48 | 192 | 14 | 3000 | 317 | 306 | 57.0 | 312 | 337 | 54.7 |

## Findings (verified from the table above)

- **Carry at the anchor cases:** MuJoCo-physics ball (the evaluator's) 289 yd at 120 mph / smash 1.48 / 12 deg / 2400 rpm (reference ~270-280 yd: ~3-7% high, inside the +-5% tolerance of the range) and 312 yd at 130 mph (reference ~300+: consistent). The analytic model gives 293 / 319 yd. So drag + Magnus lift reproduce driver-class carry to within a few percent WHEN the ball is launched at a realistic ~178-192 mph.
- **Slightly long:** constant Cd 0.26 (no Reynolds/spin dependence), no spin decay (the physics ball keeps all its spin; the analytic one decays 3%/s) and Cl capped at 0.30 all err toward more carry/apex; apex 33 m (physics) vs 38 m (analytic) at 120 mph - the physics ball is flatter. Not tuned here.
- **Smash 1.0 rows (what this sim's contact model actually produces) carry only 165-202 yd at 120-130 mph** (analytic 165-190): the carry shortfall vs a real drive is the ball-speed problem (see results/smash_anomaly.md), not the flight model.
- **Total distance / roll is NOT validated and is unphysical in the physics ball:** `total` there is 290-785 yd (rolls for the full 60 s; higher for slower, lower-spin shots) because the env has ball_damping 0.0 and the MuJoCo sphere-plane contact has essentially no rolling resistance (no rolling friction), plus bounce uses the contact solref only. The analytic model adds a bounce/roll model (total ~ carry + 27-33 yd at smash 1.48). Do not trust physics 'total' beyond carry.
- **In the leaderboard, episodes end at the first landing** (ResidualGolfEnv: 'episode ends earlier on landing'), so leaderboard total distance = carry (roll 0.0 m for models that landed); only never-landed or bouncing-then-ended shots differ. The yard columns for total are therefore carry-equivalent in this protocol.
- **Not modeled / off:** no sidespin-from-wind, no wind, no altitude/temperature (rho fixed 1.19), no lift dependence on Reynolds number, no rolling friction, no dimple drag crisis.
