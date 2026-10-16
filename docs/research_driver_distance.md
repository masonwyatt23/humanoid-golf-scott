# Research: from "nudge" contact to driver-level strikes (MuJoCo humanoid golf + PPO)

Written 2026-10-16 (research only; nothing committed/pushed, no video downloaded).
Confidence tags: **[V]** verified in a cited source this session, **[C]** computed here (script in §1.5), **[?]** uncertain / from memory / needs checking.

## 0. Executive findings (read first)

1. **Target sanity check.** Club 110-125 mph / ball 165-180 mph gives roughly **250-300 yd carry** (tour average: 113 mph club, 167 mph ball, 275 yd carry [V][T1]). A **350-yd** drive needs **long-drive-level speed**: World Long Drive Trackman data average ~145 mph club, ~214 mph ball, smash 1.48, ~352 yd *carry* [V][L1]; a 409-yd champion shot was 141 mph club / 211 mph ball [V][L2]. So "110-125 mph" is the right *first milestone*; 350 yd *total* realistically needs ~130+ mph club (roll adds maybe 20-40 yd [?]); 350 *carry* needs ~145 mph.
2. **The current model cannot get there yet, independent of RL.** Findings from `env/models/humanoid_golf.xml` (inspected, not modified):
   - **Club mass is wrong.** Shaft is a 1.1 m capsule of radius 0.015 with default density 1000 kg/m3 (`inertiafromgeom=true`) = **~0.78 kg** shaft (pi*0.015^2*1.1*1000) + ~0.16 kg head box. Real driver is ~0.30-0.33 kg total [?] (head ~0.20 kg). The sim club is ~3x too heavy, and its mass is mostly in the shaft, so swing-weight is wrong. Set masses explicitly.
   - **Tunnelling / contact resolution.** `timestep=0.002`. At 50 m/s club and 80 m/s ball, the club moves 0.10 m/step and the ball 0.16 m/step; the ball is 0.043 m in diameter and the head box is 0.04 m thick. Contact is penetration-based, so strikes at driver speed will be missed or resolved erratically. This alone can produce "nudge" outcomes. Use ~0.0002-0.0005 s timestep, or an analytic impact model (§1.4).
   - **One-handed swing.** Only the right arm reaches the club; `left_shoulder` is a stub capsule with no elbow/wrist/grip. Two-handed grip (weld/connect equality between left hand and shaft) is needed for realistic speed and face control.
   - **Weak/unscaled actuators.** Motors use `gear` 20-80 with no `ctrlrange`/`forcerange` in the file excerpt I read; torso has a free root joint with no pelvis/spine/rotation DOF (only hip *pitch*, no hip/torso yaw). Real swing power comes from pelvis-thorax rotation, which this body cannot do. Need hip/torso yaw (and spine) DOFs.
   - No ball restitution/spin: ball is a plain sphere, default contact; no aero (§1.3).
3. **Recommended order of work:** fix the physics (club mass, timestep or analytic impact, two hands, rotation DOFs) -> add ball aero + a calibrated flight tracker -> then reward shaping/curriculum -> then style (imitation/AMP) -> then real data. Doing RL on top of the current physics will mostly optimise exploits.

---

## 1. Physics targets

### 1.1 Driver reference numbers

| Metric | PGA Tour avg (Trackman) [V][T1] | World Long Drive avg [V][L1] | 409-yd WLD shot [V][L2] | Suggested sim milestones |
|---|---|---|---|---|
| Club head speed | 113 mph (50.5 m/s) | ~145 mph (65 m/s) | 141.3 mph | M1 60 mph -> M2 90 -> M3 113 -> M4 130+ |
| Ball speed | 167 mph (74.7 m/s) | ~214 mph (95.7 m/s) | 211 mph | = smash x club speed |
| Smash factor | 1.48 | 1.48 | 1.50 | 1.45-1.50 (centered); drops off-centre |
| Launch angle | 10.9 deg | ~ (not extracted) | - | 10-15 deg |
| Attack angle | -1.3 deg | positive (up) [?] | - | 0 to +4 deg is distance-optimal [?] |
| Backspin | 2686 rpm | ~lower for max carry [?] | - | 2200-2800 rpm |
| Carry | 251 m / 275 yd | 352 yd | - | - |

Sources: T1 Trackman PGA Tour averages PDF; L1 RANDA/R&A "Analysis of Trackman data gathered at World Long Drive"; L2 golf.com (see §Sources). Trackman's 2024 update says speeds went up and spin down vs the PDF values [V][T3]. Ball-speed formula: ball speed ~= smash x club speed; smash ~= (1+e)/(1+m/M) with ball 0.0459 kg, effective head mass ~0.2 kg, e ~0.83 gives ~1.49 [C] (e value is from memory [?]; the rules actually regulate *characteristic time* <= 239 us (+18 us tolerance), not COR [V][R1]).
Equipment limits [V][R1]: head <= 460 cc; club length <= 48 in (1.22 m); typical driver 45-46 in (1.14-1.17 m) [?]. Loft 9-12 deg [?]. Ball: 45.93 g max mass, 42.67 mm min diameter [?].

Unit conversions: 1 mph = 0.44704 m/s; 100 yd = 91.44 m. 350 yd = 320 m.

### 1.2 What the current numbers mean
Club ~0.2 m/s and ball ~1 m/s are ~250x below driver speed (50 m/s). Even at 1 m/s ball speed the ratio is ~5 (not 1.48), which indicates the contact is a soft push (penetration-resolved) rather than an impact; this is another symptom of §0.2.

### 1.3 Ball aerodynamics (to measure carry)

Model (standard): `F = -0.5 rho A Cd |v| v  +  0.5 rho A Cl |v| (w_hat x v)`, plus spin decay ~4 %/s [V][A1], gravity, rho ~ 1.19-1.225 kg/m3. Ball: r = 0.02135 m (A = 1.432e-3 m2), m = 0.0459 kg. Spin factor S = w r / |v|. Literature: Cd falls from ~0.5 at Re ~ 5e4 to ~0.2-0.25 above Re ~ 1e5 (drag crisis); Cl ~ 2nd-order polynomial in S; ball-to-ball differences in Cd > 0.1 at low speed, < 0.05 at high speed [V][A1]. Reynolds at 75 m/s is ~2e5, i.e. beyond the crisis, so a constant Cd is acceptable for driver speeds but **wrong at low speed** (matters for chips/putts and the low-speed "nudge" regime) [A1].

**Calibrated parameters (this report, [C])**: I integrated the 2-D ODE (RK4-less Euler at 1 ms; script below) and fit constants so a Trackman tour-average driver shot (167 mph, 10.9 deg, 2686 rpm) reproduces tour carry/height (251 m / 29 m [V][T1]):

- **Cd = 0.26, Cl = min(1.7 * S, 0.30), spin decay 4 %/s, rho = 1.19** -> 248.5 m carry, 29.6 m apex (target 251 / 29). [C]
- Sanity: 180 mph, 12 deg, 2500 rpm -> 264 m carry (289 yd); 214 mph, 11 deg, 2400 rpm -> 302 m (330 yd) [C]. The WLD figure (352 yd) is ~7 % higher than this model; WLD conditions (altitude/wind/spin/launch) are not controlled for here, so treat constants as tour-calibrated, not universal. [?]
- Cross-check against Alan Nathan's golf trajectory spreadsheet (uses WSU lift/drag data) before trusting >200 mph shots [V][A2].
- Reference lab protocol: 71.5 m/s, 6 deg, 3000 rpm, 4 %/s decay used in Lyu et al. [V][A1].

**How to model in MuJoCo (two options):**
1. **Recommended: custom force each step** (`data.xfrc_applied[ball_id,:3]` = drag + Magnus using ball linear velocity and angular velocity `qvel[3:6]` of the free joint; note free-joint angular velocity is in the *local* frame in `qvel`, use `data.cvel` or `data.xvelp/xvelr`/`mj_objectVelocity` for world frame). Also apply spin decay by a small angular drag torque (`xfrc_applied[:,3:]`). Most controllable and easy to calibrate.
2. **Built-in ellipsoid fluid model**: `<option density="1.19" viscosity="1.8e-5" wind="0 0 0"/>` and on `ball_geom` `fluidshape="ellipsoid" fluidcoef="Cd_blunt Cd_slender Cd_ang C_Kutta C_Magnus"`; defaults are `0.5 0.25 1.5 1.0 1.0`; Magnus force is `C_M rho V (w x v)` [V][M1]. It is *not* calibrated to dimpled balls (single Cd, Magnus linear in spin with no saturation), and it adds an added-mass term that can't be turned off, so you'd have to fit `fluidcoef[0]` ~0.26 and `fluidcoef[4]` empirically [?]. Fine as a quick check, worse as a measurement instrument.
3. **Impact -> launch model**: MuJoCo soft contacts will not yield correct spin/launch. Either (a) shrink the timestep (<=0.0002 s), set `solref` for the ball/face pair stiff (timeconst ~2*timestep) and give the face a loft + friction (~0.3-0.5 [?]), then *measure* ball velocity 1-2 ms after separation; or (b) detect first contact and replace the ball's post-impact `qvel` with an analytic impulse result (normal: `v_n = (1+e)/(1+m/M_eff) * v_rel_n`; tangential: friction-limited sliding gives backspin, spin ~ proportional to tangential slip/(r) ). (b) is much more stable for RL and lets you randomise face-strike offset (gear effect) later. [?] on exact friction/spin constants.
4. Always measure: ball speed, launch angle (vertical + horizontal), spin vector, carry (first ground contact), total (after roll; roll model needs ground friction/restitution, `condim` 6 for rolling friction [?]), apex, lateral at landing.

Flight script used for calibration (stdlib+numpy, 2-D; extend to 3-D for lateral):

```python
import numpy as np
def carry(v_mph, launch_deg, rpm, cd=0.26, clk=1.7, clmax=0.30, decay=0.04, rho=1.19, dt=1e-3):
    m, r, g = 0.0459, 0.02135, 9.81; A = np.pi*r*r
    th = np.radians(launch_deg); v = v_mph*0.44704*np.array([np.cos(th), np.sin(th)])
    p = np.zeros(2); w = rpm*2*np.pi/60; t = 0.0; apex = 0.0
    while True:
        s = np.hypot(*v); S = w*r/s; cl = min(clk*S, clmax); q = 0.5*rho*A*s
        a = np.array([0, -g]) + (-cd*q*v + cl*q*np.array([-v[1], v[0]]))/m
        v += a*dt; p += v*dt; t += dt; w *= np.exp(-decay*dt); apex = max(apex, p[1])
        if p[1] < 0 and t > 0.1: return p[0], t, apex   # carry m, hang time s, apex m
```

### 1.4 Club / body realism (uncertain items marked)
- Club: total ~0.30-0.33 kg, head ~0.20 kg, shaft ~0.06 kg, grip ~0.05 kg, length 1.14-1.17 m, loft 9-11 deg, head COR via `solref`, face friction. [?]
- Club head speed arises from summed segment contributions (legs/pelvis -> thorax -> arms -> wrist release); a single wrist pivot with a 1.1 m shaft would need ~45 rad/s (~2600 deg/s) of club angular velocity to reach 50 m/s tip speed [C]. Elite wrist/club angular speeds are of that order but achieved mostly through the kinematic chain [?]. => body needs pelvis and thorax yaw, shoulder 3-DOF, elbow, forearm pronation/supination, wrist radial/ulnar + flexion with realistic ranges.
- Delivered ball-speed realism also depends on face-centre strikes (smash falls quickly off-centre) [V][T-ballspeed].

---

## 2. RL approaches for athletic/dexterous swing tasks

What is documented (with caveats) and what we should do:

| Idea | Evidence | How it applies here |
|---|---|---|
| **Imitation reward / DeepMimic** (track reference pose/vel + task reward, reference-state initialisation, early termination) | DeepMimic [V][D1] | Best fit once we have any reference swing (Mason's videos, synthetic Scott). Keep the existing "style" reward but make it a *tracking* term over the swing phase, combined with a task term. |
| **AMP** (GAIL-style discriminator gives style reward, task reward gives goal) | AMP [V][D2] | Style from unlabeled clips without per-frame tracking; needs multiple clips (we have 4.5 min/ a handful of swings). **Known failure mode in golf:** SMPLOlympics reports AMP "optimizes only the task reward and ignores the discriminator" in golf, and PPO alone gives "inhuman motion (kicking the ball with the pelvis block)" [V][S1]. Needs reward-balance tuning. |
| **Motion prior + task (PULSE / PULSE+AMP, PHC)** | SMPLOlympics: PULSE kicks the ball with human-like motion; PULSE+AMP gives the most golf-like style [V][S1] | Strongest published baseline for physics-humanoid golf; it requires an SMPL humanoid (SMPLSim / ProtoMotions, Apache-2.0 [V][P1]) and a pre-trained motion prior from AMASS (non-commercial licence [V][AM1]). Commercial-product caveat. |
| **Contact-gated / phase-gated rewards** | standard practice; tasks in SMPLOlympics use simple task rewards on top of priors [V][S1] | (a) approach reward until club is within ~0.05 m of ball; (b) *impact-window* reward: club head speed (along target line) sampled at the step of first contact; (c) after contact: ball speed along target (m/s), launch-angle band 8-16 deg, lateral error penalty, spin band; (d) smoothness/torque penalty. Don't reward club speed everywhere (policy will spin the club without hitting). |
| **Curriculum** | general RL practice | Stage 1 contact (tee, big/forgiving face, slow), Stage 2 raise `max_torque`/gear and timestep refinement, Stage 3 require ball speed thresholds (ratchet every time success > 80 %), Stage 4 add strike-offset/spin accuracy, Stage 5 randomisation (ball pos +-2 cm, tee height, mass). Use success-based, not time-based, advancement. |
| **Phase variable + residual control** | DeepMimic uses a phase input [V][D1] | Add a normalised swing phase to observation; let policy output residuals around a kinematic reference swing (PD target = reference + action). Typically far more sample-efficient than torque from scratch. [?] |
| **Action space** | humanoid sim-to-real efforts use 200 Hz sim / 50 Hz control with PD position targets and torque limits [V][S1] | Move from direct motor `gear` to position actuators with `kp/kv` and `forcerange` per joint. |
| **Algorithm** | PPO is the baseline used in these works; AMP/PULSE use PPO variants | Keep PPO but run 1024+ parallel envs; SB3 on 1 CPU env at 20-50k steps is far too small (typical AMP/DeepMimic runs are 10^8-10^9 samples [?]). Consider MJX/MuJoCo-Playground or Isaac-based ProtoMotions for throughput. |

**Torque limits / actuator realism:** use per-joint peak torque and speed limits in the range of humans or of the Unitree H1/G1 (SMPLOlympics keeps their real torque/joint limits [V][S1]; I did not find explicit numbers [?]). Practical note: if the bound is too loose, RL will exploit un-human torques; if too tight, speed targets are unreachable, so make the limit a curriculum variable and report the *peak joint torque* alongside club speed. Add armature/damping realistic values (current armature 0.2, damping 2.0 uniformly is crude [?]).

**Anti-exploit checks** (golf-specific, repeatedly seen): ball pushed by pelvis/foot/shaft rather than the club face; contact flag from any body; club speed from spinning the club without a ball. Enforce "first contact must be club-face geom" and compute ball speed from post-separation velocity.

---

## 3. Data, licences and motion recovery

### 3.1 Datasets (as of research date)
| Dataset | What | Licence / terms | Use for us |
|---|---|---|---|
| **GolfDB** (McNally et al., CVPRW 2019) | 1,400 annotated pro/amateur swing clips, 8 event frames, player, club, view, bbox [V][G1][G2] | Repo **code CC BY-NC 4.0**; videos are third-party YouTube content with no stated licence (see existing `docs/GOLFDB_PLAN.md`). Non-commercial only; video use is a legal grey area [V][G1] | Use *annotations* (events, player names) for research; do NOT download video for a commercial product without permission. |
| **Mason's own swings** (4.5 min, Instagram @masonwgolf) | Own IP | Own | Primary clean-IP source. Best for commercial product. |
| **CMU Mocap DB** | Includes golf swings: subject 63 (1 trial), subject 64 (30 trials incl. ~10 "Swing") [V][C1] | **Free for all uses incl. commercial** (cannot resell the data) [V][C2] | Best legal, true 3-D skeleton data: retarget directly (BVH/AMC) as clean reference swings. High priority. |
| **CaddieSet** | Tabular launch-monitor-like data (no video) | MIT [per existing `docs/CADDIESET_INTEGRATION.md`; not re-verified] | Statistical priors (club speed vs. joint features), not motion. |
| **AMASS** | 11k+ motions, no dedicated golf subset found [V][AM1] | MPI non-commercial; commercial NN training prohibited without written permission [V][AM1] | Pretraining a motion prior = research only. |
| **Trackman averages** | Tour & LPGA shot stats [V][T1] | public PDFs | Evaluation targets (table above). |

### 3.2 Pose/motion recovery tools
| Tool | Output | Licence | Notes |
|---|---|---|---|
| **MediaPipe Pose** | 33 2-D/3-D-ish landmarks, one person | **Apache-2.0** [V][MP1] | Already in the Data Agent pipeline; single-view depth is ambiguous, no club tracking. Good first pass. |
| **WHAM** | SMPL motion in world coords | Repo **MIT**, but depends on SMPL, ViTPose, DPVO/DROID-SLAM etc. with their own terms [V][W1] | Good world-grounded motion; SMPL licence gates commercial use [?]. |
| **GVHMR** (SIGGRAPH Asia 2024) | SMPL/SMPL-X, world & camera frame | **Non-commercial research only; derivatives must be open-source; commercial requires permission from the authors** [V][GV1] | Excellent quality but **conflicts with a commercial product** unless licensed. |
| **SMPL / SMPL-X body models** | parametric body | MPI registration-gated, not redistributable [V][GV2] | Needed by WHAM/GVHMR; check commercial terms with MPI. |
| **ProtoMotions** (NVlabs) | Humanoid RL + retargeting, MuJoCo support | **Apache-2.0** [V][P1] | Candidate training/retarget stack. |
| **PHC / SMPLSim** | physics-based refinement of video poses | BSD-3-Clause [?, search result only] | SMPLOlympics shows physics refinement of video-derived poses improves the motion prior [V][S1]. |

### 3.3 Retargeting to our humanoid
1. Recover joints/rotations (MediaPipe 3-D world landmarks, or SMPL from WHAM/GVHMR; or CMU BVH).
2. Convert to a common skeleton; compute per-joint angle time series (our `.npz` joints are in deg; the env reward compares rad vs deg - already flagged by Data Agent, `docs/proposed_env_units_fix.patch`).
3. Scale limb lengths to our body (our model's segments are 0.3 m arm links, 0.4 m legs: fit via per-segment scale), map joints (we lack hip/torso yaw and left arm; add DOFs first).
4. Time-normalise to swing phase by GolfDB-style events (address, takeaway ... impact, finish) so styles can be blended and tempo (backswing:downswing ~3:1 [?]) preserved.
5. Physics clean-up: track the kinematic reference with a PD/imitation policy in our sim (DeepMimic-style) and save the *simulated* result as the reference; SMPLOlympics shows the refinement step matters [V][S1].
6. Club trajectory is not recoverable from MediaPipe (no club tracking) - estimate from hands + known grip, or track a club-end marker/keypoint with a custom detector [?].

---

## 4. Prioritised experiment plan (effort estimates for a single agent-dev; [?] = rough)

| # | Experiment | Why / expected result | Effort |
|---|---|---|---|
| 1 | **Fix club inertia & timestep, add two-handed grip.** Explicit masses (head 0.20, shaft 0.06, grip 0.05), length 1.14 m, timestep 0.0005 (or 0.0002), left forearm/hand + grip equality. Unit test: scripted swing at 40 m/s -> ball speed ~ smash x club. | Removes tunnelling/heavy-club bugs. Expect first *physical* ball speeds. | 0.5-1 day |
| 2 | **Impact validation test (no RL).** Prescribed club trajectory at 20/40/50/60 m/s into the ball; log smash, launch, spin. Tune `solref`/`friction` (or switch to analytic impact). | Establishes smash ~1.45-1.5 and loft->launch before any learning. | 0.5-1 day |
| 3 | **Ball aero + flight tracker.** Add custom drag/Magnus (§1.3), compute carry/total/apex/lateral; unit test vs Trackman tour row (248.5 m / 29.6 m calibrated). Update `eval/flight_tracker.py` to report carry. | Makes "carry" a measurable metric (currently 0 balls land). | 0.5 day |
| 4 | **Add hip/torso yaw (+ spine), left arm; torque limits as `forcerange`; PD position actuators.** | Needed physically for >50 m/s club speed. | 1-2 days |
| 5 | **Replay a hand-built kinematic/CMU swing (retargeted) with PD tracking** and measure the club speed it produces. | Gives an achievable-speed upper bound for the body and a reference swing; tells whether 113 mph is reachable with your torques. | 1-2 days (CMU BVH retarget) |
| 6 | **PPO with phase input + residual on reference, contact-gated impact reward, success-based curriculum.** Reward = club speed along target line at impact window (clipped, scaled by face-contact) + ball speed along target + launch band + lateral penalty - torque/jerk. Run >=1M steps w/ 8-32 parallel envs. | Target milestones M1 -> M3. Track contact %, club mph, ball mph, smash, carry, lateral std. | 2-4 days incl. compute |
| 7 | **Style term:** DeepMimic tracking on Mason/CMU reference, then AMP (watch task/disc reward balance per SMPLOlympics failure mode) [V][S1]. | Recovers human-like swings while keeping speed. | 3-5 days |
| 8 | **Real-data pipeline:** Mason's videos -> MediaPipe (commercial-safe) -> retarget -> sim-refine (PHC-style). Consider GVHMR/WHAM only for research/internal comparison due to licences. | Style references; clean IP. | 3-5 days |
| 9 | **Dispersion & robustness:** strike-offset randomisation (gear effect), tee height, noise; report lateral std, miss rates, carry std over 500 episodes. | Consistency metrics requested earlier. | 1-2 days |
| 10 | **Stretch to 350 yd:** raise torque curriculum toward long-drive regime (130-145 mph club) + loft/launch/spin optimisation (sweep loft 8-12 deg, attack angle 0..+5, spin 2200-2800 rpm with the calibrated flight model). | Reaching WLD numbers is likely torque/body-model limited; report speeds honestly. | open-ended |

Immediate high-value measurements to run first (no training): items 1-3 (about 1-2 days), because they decide whether the current ~0.2 m/s club speed is an RL or a physics problem.

---

## Sources
- T1 Trackman PGA Tour averages PDF: https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf ; help page https://support.trackmangolf.com/hc/en-us/articles/5089752464667-Shot-Analysis-Tour-Averages-On-PGA-LPGA-Tour
- T3 Trackman 2024 updated averages: https://www.trackman.com/blog/introducing-updated-tour-averages ; ball speed article https://www.trackman.com/blog/ball-speed (PGA driver ball speed 171 mph in newer data)
- L1 Analysis of Trackman data at World Long Drive (R&A/RANDA): https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/550ab9f6-5dd3-45b0-b58c-7563d4256c04/R07%20-%20Analysis%20of%20Trackman%20data%20gathered%20at%20World%20Long%20Drive.pdf
- L2 409-yd long-drive Trackman numbers: https://golf.com/instruction/driving/long-drive-champ-golfer-trackman-numbers/
- A1 Lyu et al., Aerodynamics of Golf Balls in Still Air: https://www.mdpi.com/2504-3900/2/6/238
- A2 Alan Nathan golf trajectory calculator: https://baseball.physics.illinois.edu/trajectory-calculator-golf.html
- Stengel (1992) golf trajectory model: https://stengel.mycpanel.princeton.edu/Golf1992.pdf ; Penner, optimum driver loft: http://www.raypenner.com/golf-loft.pdf
- M1 MuJoCo fluid forces: https://mujoco.readthedocs.io/en/stable/computation/fluid.html
- R1 Equipment rules (head volume, length, characteristic time): https://www.randa.org/roe/the-rules-of-equipment/part-2-conformance-of-clubs ; https://www.usga.org/content/dam/usga/pdf/Equipment/TPX3004-procedure-for-measuring-the-flexibility-of-a-golf-clubhead.pdf
- D1 DeepMimic: https://arxiv.org/abs/1804.02717 ; D2 AMP: https://arxiv.org/abs/2104.02180
- S1 SMPLOlympics (golf env, PPO/AMP/PULSE comparison, Unitree H1/G1): https://smplolympics.github.io/SMPLOlympics-Site/
- P1 ProtoMotions (Apache-2.0): https://github.com/NVlabs/ProtoMotions
- G1 GolfDB repo: https://github.com/wmcnally/golfdb ; G2 paper: https://openaccess.thecvf.com/content_CVPRW_2019/papers/CVSports/McNally_GolfDB_A_Video_Database_for_Golf_Swing_Sequencing_CVPRW_2019_paper.pdf
- C1 CMU mocap golf subjects: http://mocap.cs.cmu.edu/search.php?subjectnumber=64 ; C2 CMU FAQ/terms: http://mocap.cs.cmu.edu/faqs.php
- AM1 AMASS licence: https://amass.is.tue.mpg.de/license.html
- MP1 MediaPipe Pose: https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker (Apache-2.0 per repo https://github.com/google/mediapipe)
- W1 WHAM: https://github.com/yohanshin/WHAM (MIT repo licence)
- GV1 GVHMR licence: https://github.com/zju3dv/GVHMR/blob/main/LICENSE ; GV2 SMPL gating: https://pypi.org/project/gvhmr/

## Caveats
- Web search summaries were used; most key numbers (Trackman, WLD, licences, MuJoCo coefficients) were read from the returned source text, but I did not open every PDF in full. Items tagged [?] come from memory or were not confirmed.
- Calibrated Cd/Cl are fit to one Trackman row with a 2-D model; validate in 3-D against Nathan's spreadsheet and vary altitude/temperature before using them as ground truth.
- Licence statements are not legal advice; commercial use of GVHMR, SMPL, AMASS, and GolfDB video needs explicit permission or avoidance.
