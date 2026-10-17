# Smash-factor anomaly (verified here; for the Trainer)

Setup: scripted v3 (zero residual), evaluator env, 10 episodes seeds 4000+, `eval/smash_anomaly.py`, per-shot data from `eval/flight_tracker.py`.

## Smash computed two ways

- A (leaderboard definition): peak ball speed / club speed at first-contact step (env.impact_club_speed): **1.003** (ball 53.91 m/s / club 53.77 m/s).
- B: ball speed just after separation (first substep without contact) / club speed at the substep before the first contact substep: **1.008** (ball 54.13 m/s / club 53.70 m/s).
- Both ~1.0: not a metric artefact (the numerator/denominator choice moves it by <~1%).

## Contact model (env/models/humanoid_golf_v3.xml)

- Head mass 0.300 kg (club_head geom 0.20 kg + shaft 0.10 kg ride on lower arm body; mass of the geom's body shown: 0.300), ball 0.046 kg. Head solref [0.002, 1.0], ball solref [0.002, 1.0], solimp [0.95, 0.99, 0.001, 0.5, 2.0], timestep 0.0005, friction head/ball [0.5, 0.01, 0.001]/[0.5, 0.01, 0.001].
- solref = (timeconst 0.002, dampratio 1): dampratio 1 = critically damped contact spring -> coefficient of restitution ~0 (plastic collision); no per-pair override in the XML.
- Effective inertial mass at the head along head->ball at contact (1/(n^T J M^-1 J^T n), unactuated arm chain): **0.32 kg** (vs head geom 0.20 kg). Actuators are stiff position servos so the head also behaves as if driven.
- Implied restitution from B and that mass: e = smash*(M+m)/M - 1 = **0.15** (a real driver face is ~0.80-0.83; smash_max = (1+e)M/(M+m) -> with e=0.83 and the real 0.20 kg head: 1.49; with this sim's effective mass and e=0.83: 1.60).

## Contact-damping sweep (both geoms' solref damping ratio; everything else unchanged)

| damp ratio | smash B | ball sep m/s | club pre m/s | mean carry m (physics) |
|---|---|---|---|---|
| 1.0 | 1.01 | 54.1 | 53.7 | 110.6 |
| 0.5 | 1.11 | 59.7 | 53.7 | 115.5 |
| 0.3 | 1.27 | 68.0 | 53.7 | 143.7 |
| 0.15 | 1.90 | 102.2 | 53.8 | 131.3 |

## Likely cause and what the sim can reach

Likely cause: the head-ball contact is (nearly) inelastic by construction (dampratio 1 on both geoms) and the head is attached to a heavy servo-driven arm, so ball speed ~ head speed (smash ~1). It is a contact-parameter choice, not a bug in the eval code or the cvel indexing.
Reachable physical smash: lowering the damping ratio raises smash monotonically (table above); ~1.4-1.5 needs a damping ratio in the 0.15-0.3 range and then re-verifying stability/penetration, launch, and every carry in the leaderboard (they would all change). The reported carries here are for a ball hit at ~54 m/s, not the ~80 m/s of a real 120 mph drive.
Not applied: no XML/env change was made by this analysis.
