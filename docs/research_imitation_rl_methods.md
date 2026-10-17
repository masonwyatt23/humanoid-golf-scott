# Imitation + RL methods for athletic humanoid motion: cited survey and Trainer recommendations

Written 2026-10-17 (America/New_York). Research only: no video was scraped, nothing was pushed. Machine-readable twin: `data/references/imitation_rl_recommendations.json` (schema test: `tests/test_imitation_rl_recommendations.py`). Earlier internal survey this builds on (not re-verified here): `docs/research_methods.md`.

**How to read the evidence.** Every source carries a `read_level`: `full_text_fetched` (whole paper text read this session; long appendices may be truncated), `partial_text_fetched` (relevant sections grepped from the arXiv HTML), `abstract_only`, or `search_snippet_only`. A hyperparameter is listed as verified only when its number appears in text I read; everything else is tagged *unverified*. Numbers tagged **(ours)** are engineering starting points we derived, not paper values. Style-profile language only; the survey uses no player likeness data.

## 0. Bottom line (read this first)

1. **Our env currently cannot learn a time-accurate swing.** Read-only look at `origin/main` (`a5df07b`): `ref_idx = episode_steps` (control step 0.02 s) while the unified reference has `dt = 0.01 s`, and `reference['dt']` is never used, so the reference plays at 2x speed and a 200-step episode covers only 2.0 s of it; `phase = steps/max_steps` is unrelated to clip length; reset starts from the address pose with small noise (no reference-state initialization); termination is only `torso z < 0.4` (never, with `pin_torso`). Trainer's uncommitted edits may already change this (not visible to me). Whether this is the Orchestrator's "0.4 s bug" is **unverified**. See R01-R03.
2. **The literature is consistent on the recipe:** per-term exponential tracking reward including velocity and end-effector terms, phase + reference-state initialization, tracking-error early termination, adaptive sampling of hard segments, PD-target actions, minimal domain randomization (DeepMimic, PHC, GMT, BeyondMimic, KungfuBot).
3. **Imitation alone does not hit the ball.** DeepMimic: imitation-only success 5% (throw) / 19% (strike) vs 75% / 99% with a task term. The only published humanoid golf reward (SMPLOlympics) is contact `exp(-100 d^2)` pre-contact + ball progress + goal + predicted-landing, with early termination for no contact in 2 s. Plain PPO and AMP failed to initiate contact there; only PULSE variants succeeded (SMPL body, GPU scale).
4. **No paper provides a club-speed reward or a 350 yd / 150 mph target.** The speed-ladder reward (120 to 150 mph, `data/references/power_profile_350yd_targets.json`) in R07 is our design and must be validated.
5. **Compute reality:** DeepMimic needed ~60M samples (~2 days, 8 CPU cores) per skill; PHC ~10B samples; GMT ~6.8B. This box has 8 CPU cores and no GPU, so start with single-clip policies on Mason's best clips, then the multi-clip refset.

## 1. Prioritized recommendations for the Trainer

Priority P0 = fix before any long run; P1 = next; P2 = after tracking works; P3 = fallback/later.

### R01 [P0] timing/phase: Index the reference by simulated time, not by step count. Compute ref_idx = min(len-1, round(t_sim / ref_dt)) (ref_dt from the npz 'dt'; unified refset is 0.01 s, env control step is 0.02 s) and define phase = ref_time / clip_duration so phase 1.0 = end of the clip.

- **Why / citations:** DeepMimic defines phase phi in [0,1] as progress through the clip and syncs it to the reference clock; PHC/GMT/BeyondMimic all run reference and policy on the same clock. On origin/main the env sets ref_idx = episode_steps (control step 0.02 s) and ignores reference['dt'], so a 0.01 s reference plays at 2x speed and a 200-step episode covers only 2.0 s of reference; phase = steps/max_steps is unrelated to clip length. This is read-only evidence from a5df07b; Trainer's uncommitted edits may already fix it.
- **Papers:** `deepmimic`, `kungfubot`, `repo_env` (evidence: verified_in_paper+code_observation)
- **Parameters:** `{"ref_dt_s": 0.01, "control_dt_s": 0.02, "ref_idx": "round(t_sim/ref_dt)", "phase": "t_ref/T_clip"}`
- **Unverified:** whether the 0.4 s bug mentioned by the Orchestrator is this issue is not verified here
- **Acceptance check:** unit test: constructing env with a 0.01 s reference, after 50 control steps ref_idx==100 and ref time == sim time

### R02 [P0] rsi: Use reference-state initialization: reset to a state sampled from the clip (pose AND velocity, set club/ball consistent), uniform over phase at first, then adaptive. Keep a fraction (e.g. 20%) of resets at phase 0 so address-position starts are still trained.

- **Why / citations:** DeepMimic Table 5: RSI is vital for dynamic skills with flight/ballistic phases (backflip 0.379 without RSI vs 0.791 with RSI+ET); PHC, KungfuBot and BeyondMimic all use RSI. A golf downswing is a ballistic-like fast phase that is hard to reach from address under exploration noise.
- **Papers:** `deepmimic`, `phc`, `beyondmimic`, `kungfubot` (evidence: verified_in_paper)
- **Parameters:** `{"rsi": "uniform phase then adaptive", "fraction_phase0": 0.2}`
- **Unverified:** the 20% address-start fraction is an engineering choice, not from a paper
- **Acceptance check:** after change, episodes starting at phase >=0.5 reach impact within the first 0.5 s of sim

### R03 [P0] termination: Replace torso-height-only termination with a tracking-error termination that is loose early and tightens: terminate when mean key-body error > E(c) where E goes 0.6 m -> 0.25 m as the clip is completed repeatedly, plus a fall check (base height / gravity projection). Do NOT terminate on club-head error alone; do not terminate after ball contact for the remaining follow-through unless fallen.

- **Why / citations:** GMT tightens the threshold per clip from 0.6 to 0.25 with completion count; BeyondMimic terminates on |z error|>0.25 m or anchor orientation >0.8 rad; H2O terminates at base height<0.3 m, gravity proj>0.7, mean link error>0.5 m; PHC uses 0.5 m with relaxed ankle/toe; DeepMimic ET on torso/head contact is critical. SMPLOlympics golf ET adds: ball moves backward, no contact within 2 s, ball too close to body.
- **Papers:** `gmt`, `beyondmimic`, `h2o`, `phc`, `deepmimic`, `smplolympics` (evidence: verified_in_paper)
- **Parameters:** `{"E_start_m": 0.6, "E_end_m": 0.25, "gate": "completion count c: c0=10, x0.99 per completed clip, min 1 (GMT)", "fall_base_height_m": 0.3, "gravity_proj_max": 0.7, "golf_extra": ["no club contact within 2 s => end", "ball moves backward => end"]}`
- **Unverified:** units of GMT E_i not stated in the text read; thresholds for a G1-scale model unverified; 2 s no-contact window is for SMPLOlympics golf and our swings last ~1.5-2.7 s
- **Acceptance check:** unit test: perturbed reference drives early termination; pin_torso mode still terminates on tracking error

### R04 [P0] reward: Split the imitation reward into separate exponential terms with explicit scales instead of one exp(-mean(err^2)/0.5): joint position, joint velocity, key-body (club head, both hands) position, root/pelvis orientation, optionally COM. Start from DeepMimic weights (0.65 pose, 0.1 vel, 0.15 end-effector, 0.1 COM) with club head as the key end-effector; keep rewards bounded in [0,1].

- **Why / citations:** DeepMimic and PHC both use per-quantity exponentials including velocity terms; GMT and BeyondMimic weight all terms uniformly. Our env currently has one joint-position term (units radians, /0.5) + club_head term (1.5, /0.5) and no velocity term, so it cannot represent a fast-but-wrong-timed swing.
- **Papers:** `deepmimic`, `phc`, `gmt`, `beyondmimic`, `repo_env` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"weights": {"joint_pos": 0.5, "joint_vel": 0.1, "club_head_pos": 0.25, "pelvis_orient": 0.15}, "sigmas_note": "start sigma from BeyondMimic (pos 0.3, ori 0.4, vel 1.0) then adapt (R05)", "form": "exp(-mean_sq_err/sigma^2)"}`
- **Unverified:** the specific weight split above is a starting point derived by us, NOT from a paper; our joint vector is 11-D degrees->rad, not a full-body keypoint set
- **Acceptance check:** ablation on one clip: joint-vel term on vs off, report tracking error and time-to-impact error

### R05 [P1] reward/sigma: Make each tracking sigma adaptive: sigma <- min(sigma, EMA of current tracking error) starting from a large sigma_init, non-increasing.

- **Why / citations:** KungfuBot derives sigma* = mean optimal tracking error and implements a closed-loop EMA rule so reward stays sensitive as the policy improves; avoids hand tuning for noisy video-derived references.
- **Papers:** `kungfubot` (evidence: verified_in_paper)
- **Parameters:** `{"rule": "sigma=min(sigma,ema_err)", "ema_decay_note": "EMA rate not extracted from paper", "sigma_init": "large (e.g. 2x initial error)"}`
- **Unverified:** EMA decay and sigma_init values not extracted; check on a held-out clip before trusting
- **Acceptance check:** sigma monotonic non-increasing in logs; tracking error decreases

### R06 [P1] regularization: Add three light regularizers, ramped in after tracking works: action-rate penalty, joint-limit penalty (soft limit 0.9x), and an energy/power penalty -0.0005*sum|torque*joint_vel|^2 that is switched OFF (or scaled to 0.1) in a window around impact.

- **Why / citations:** BeyondMimic uses exactly action-rate, joint-limit (0.9 soft limit) and self-contact penalties; PHC uses the -0.0005 energy term to remove jitter; OmniH2O introduces its feet-height regularizer via curriculum. The impact-window exemption is our inference: a 130-150 mph target needs near-peak torque (see repo power profile: wrist torque margin).
- **Papers:** `beyondmimic`, `phc`, `omnih2o`, `repo_power` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"action_rate_w": 0.1, "joint_limit_w": 10.0, "joint_limit_soft": 0.9, "energy_w": 0.0005, "impact_window_s": [-0.15, 0.1], "impact_scale": 0.1}`
- **Unverified:** weights from BeyondMimic are for a 29-DoF G1 with PD actions; transfer to our torque-controlled env is unverified; impact window values are ours
- **Acceptance check:** reward component logs show regularizer total < 20% of tracking reward in downswing

### R07 [P1] task-reward: Add the club-ball impact/task reward ON TOP of tracking with a bounded weight (start 0.7 tracking : 0.3 task) and gate it by the reference impact event. Pre-contact: r_c = exp(-100*||p_ball-p_club||^2) (SMPLOlympics golf), post-contact: 1 for contact + predicted-landing/carry term. For power: reward exp(-(v_club_impact - v_target)^2/s^2) with v_target from the 350yd ladder (120->130->140->150 mph).

- **Why / citations:** DeepMimic: imitation-only success 5%/19% vs 75%/99% with the task term (throw/strike), weights 0.7/0.3 for all tasks; AMP uses 0.5/0.5; SMPLOlympics golf reward = position+contact+goal+predicted landing, all weight 1, with the 100x contact kernel; PhysHOI's contact-graph reward and Vid2Player's pre/post contact reward split support timing the contact term to the reference impact event. Our env's contact term exp(-3*dist) is a much wider linear-distance kernel than exp(-100*d^2) and is not gated by contact timing.
- **Papers:** `deepmimic`, `amp`, `smplolympics`, `physhoi`, `tennis`, `repo_power`, `repo_env` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"w_track": 0.7, "w_task": 0.3, "contact_kernel": "exp(-100*d^2)", "predicted_landing": "use env/ball_flight_analytic.py", "speed_target_ladder_mph": [120, 130, 140, 150], "speed_sigma_mph": 5}`
- **Unverified:** speed_sigma 5 mph and the speed-target reward form are ours (no paper reports a club-speed reward); tennis items are snippet-level
- **Acceptance check:** eval on unified refset val split: contact rate and club speed at impact reported per ladder step

### R08 [P1] curriculum: Stage the training and gate stages on success rate, not timesteps: A) pure tracking (task weight 0) until >=80% of val clips complete without termination; B) add contact reward; C) add carry/direction; D) climb the speed ladder 120->130->140->150 mph only after C is stable. Existing set_progress() ramp in the env can implement the gating.

- **Why / citations:** DeepMimic progressive training; Vid2Player tennis three-stage curriculum (approach -> fixed targets -> continuous targets, snippet-level); GMT completion-level curriculum; OmniH2O curriculum for regularizers; SMPLOlympics says contact initiation is the hard sparse-exploration step.
- **Papers:** `deepmimic`, `tennis`, `gmt`, `omnih2o`, `smplolympics` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"stage_gate_success": 0.8, "stages": ["track", "contact", "carry", "speed_ladder"]}`
- **Unverified:** the 80% gate is ours
- **Acceptance check:** stage transitions logged with the success metric that triggered them

### R09 [P1] sampling: Use performance-based adaptive sampling over phase bins and over clips: sample start phase and clip in proportion to recent failure rate (EMA), with a uniform floor so easy segments are not forgotten; use bins of 0.25 s for 1.5-2.7 s swings (BeyondMimic uses 1 s bins for minutes-long motions).

- **Why / citations:** BeyondMimic: without adaptive sampling 3 of 4 motions fail hard segments after 30k iterations; GMT: removing adaptive sampling worsens every metric (Table 2); PHC hard-negative mining.
- **Papers:** `beyondmimic`, `gmt`, `phc` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"bin_s": 0.25, "ema": 0.999, "uniform_floor": "0.1/S", "kernel_rho": 0.8, "lookback_bins": 3, "clip_weights": "unified refset 0.6 Mason / 0.2 MultiSense / 0.2 CMU as prior"}`
- **Unverified:** 0.25 s bin size is ours; the other numbers are BeyondMimic's
- **Acceptance check:** sampling histogram concentrates on downswing/impact bins early, flattens later

### R10 [P1] data-audit: Run a feasibility filter over the unified refset before long training: train/evaluate a quick privileged tracker (no DR) per clip and flag clips it cannot track within the R03 tolerance; down-weight or drop them. Also smooth video-derived references (EMA) and check dt consistency per clip.

- **Why / citations:** H2O 'sim-to-data' keeps ~8.5k of 10k AMASS clips; GMT two-stage curation (rule-based + preliminary policy completion rate); KungfuBot physics-based filter + EMA smoothing; this directly serves the Orchestrator's request to audit for timing errors.
- **Papers:** `h2o`, `gmt`, `kungfubot` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"max_tracking_error_m": 0.25, "min_completion": 0.9}`
- **Unverified:** completion threshold is ours
- **Acceptance check:** report listing clips flagged; per-clip dt and duration table

### R11 [P2] action-space: Move from direct torque (ctrl = action*torque_scale) to PD-target actions at the sim rate, with gains from kp=I*w^2, kd=2*I*zeta*w (zeta=2, w = 2*pi*10 Hz class) using actuator armature, action scale 0.25*tau_max/kp. The env already has a _substep_ctrl hook for per-substep PD.

- **Why / citations:** DeepMimic, AMP, PHC, BeyondMimic, GMT all use PD-target actions; PHC keeps actions absolute (not residual on reference) for robustness to noisy references; BeyondMimic: zero armature causes overswing.
- **Papers:** `deepmimic`, `phc`, `beyondmimic`, `gmt`, `repo_env` (evidence: verified_in_paper)
- **Parameters:** `{"zeta": 2, "natural_freq_hz": 10, "action_scale": "0.25*tau_max/kp"}`
- **Unverified:** BeyondMimic's 10 Hz is for G1 joints; a swing needs much higher wrist bandwidth so tune per joint (unverified); BeyondMimic states natural frequency 10 Hz, not whether in rad/s
- **Acceptance check:** step response test per joint: overshoot < 10%

### R12 [P2] observation: Give the policy phase (progress of clip) plus a short future reference window (next 3-5 frames at 0.04-0.1 s, including club-head target) and the previous action; use 6D rotation for orientations if quaternions are fed.

- **Why / citations:** DeepMimic/KungfuBot include phase; GMT: next-frame-only is worse than next+2 s window, window-only is worst; TWIST: single-frame students are hesitant, privileged-future teachers smoother; BeyondMimic: Rot6D beats quaternion for sim-to-real, history hurt in their setup.
- **Papers:** `deepmimic`, `kungfubot`, `gmt`, `twist`, `beyondmimic` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"future_frames": [1, 2, 3, 5], "frame_dt_s": 0.02, "orientation": "rot6d"}`
- **Unverified:** GMT's window is 2 s; for a 1.5-2.7 s swing we propose a much shorter lookahead - unverified
- **Acceptance check:** ablation: no window vs window, tracking error at impact

### R13 [P2] domain-randomization: Keep randomization minimal and physically grounded: friction (0.3-1.6), joint zero offsets (+-0.01 rad), torso COM (+-0.025/0.05 m), small action delay <=20 ms, push velocities; add club-specific ones (grip slip, club mass +-5%, ball restitution) only for sim-to-sim robustness tests.

- **Why / citations:** BeyondMimic: compact DR preserves agility; GMT table of ranges; both stress that latency matters (BeyondMimic: 10 ms delay fails 2 of 3 hardware trials; GMT randomizes delay 0-20 ms).
- **Papers:** `beyondmimic`, `gmt` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"friction": [0.3, 1.6], "joint_offset_rad": 0.01, "com_m": [0.025, 0.05, 0.05], "action_delay_s": [0, 0.02], "club_mass_frac": 0.05}`
- **Unverified:** club-specific ranges are ours
- **Acceptance check:** policy evaluated at nominal + 3 perturbed settings, success drop reported

### R14 [P2] ppo: Raise PPO batch/parallelism and set gamma 0.95-0.99, GAE lambda 0.95, clip 0.2. Current train_ppo.py: n_envs=4, n_steps=2048, batch_size=64, n_epochs=10, gamma=0.99, lr 3e-4 (SB3 defaults-like).

- **Why / citations:** DeepMimic used batch 4096 / minibatch 256 / gamma 0.95 / lambda 0.95 / clip 0.2 and ~60M samples (2 days, 8 CPU cores); PHC gamma 0.99; GMT 4096 envs. This box has no GPU and 8 CPU cores, so expect DeepMimic-order sample budgets to take days.
- **Papers:** `deepmimic`, `phc`, `gmt`, `repo_env` (evidence: verified_in_paper+design_inference)
- **Parameters:** `{"gamma": 0.95, "gae_lambda": 0.95, "clip": 0.2, "minibatch": 256, "batch": 4096, "n_envs": 8}`
- **Unverified:** no paper verifies these for a MuJoCo CPU env with 11 joints
- **Acceptance check:** learning curves over 3 seeds, mean tracking error

### R15 [P2] per-term-value: Give tracking and impact/task rewards separate value heads (reward vectorization) or at least normalize each term, because the sparse impact reward and dense tracking reward have very different scales.

- **Why / citations:** KungfuBot vectorizes rewards with a value head per term; BeyondMimic uses an asymmetric critic with privileged per-body poses.
- **Papers:** `kungfubot`, `beyondmimic` (evidence: verified_in_paper)
- **Parameters:** `{"heads": ["tracking", "regularization", "impact"]}`
- **Unverified:** SB3 PPO does not support multi-head critics out of the box; would need a custom policy or an RL library change (not verified)
- **Acceptance check:** impact term advantage variance logged

### R16 [P3] fallback: If tracking + task reward cannot create ball contact (sparse exploration), try a latent-space hierarchical policy (PULSE-style) or pretrain a swing-skill prior; do not rely on plain AMP.

- **Why / citations:** SMPLOlympics: only PULSE and PULSE+AMP solved golf consistently; PPO and AMP produced inhuman strategies; AMP can ignore task reward.
- **Papers:** `smplolympics`, `pulse`, `amp`, `ase` (evidence: verified_in_paper)
- **Unverified:** SMPL humanoid + GPU scale, not directly our G1; PULSE repo has no detected license
- **Acceptance check:** n/a

### R17 [P3] sim2real: Defer sim-to-real tricks (teacher->student distillation, latency model, armature identification) until the sim tracker meets success gates; then: privileged teacher with future frames, student single-frame with 5-25 step history, 2-5 ms latency discipline.

- **Why / citations:** TWIST/GMT/OmniH2O teacher-student; BeyondMimic latency ablation; GMT armature = k^2*I.
- **Papers:** `twist`, `gmt`, `omnih2o`, `beyondmimic` (evidence: verified_in_paper)
- **Unverified:** history lengths differ by paper (5, 20, 25) and BeyondMimic found history hurt; unverified for golf
- **Acceptance check:** n/a

## 2. Per-method survey

Each entry: link, read level, key idea, reported hyperparameters / reward terms (verified unless marked), code license, relevance. Code licenses come from the GitHub API `license` field (spdx); `custom` means GitHub could not classify the LICENSE file (NOASSERTION) and I did not read it; `none detected` means no license file, i.e. all rights reserved by default.

### DeepMimic: Example-Guided Deep RL of Physics-Based Character Skills

- **Link:** https://arxiv.org/abs/1804.02717 (2018, ACM TOG 37(4)); arXiv id: 1804.02717
- **Read level:** `full_text_fetched`
- **Key idea:** PPO tracks a reference clip with a per-step exponential imitation reward + optional task reward; phase variable in the observation; reference-state initialization (RSI) and early termination (ET) are the two ingredients that make flight-phase skills learnable.
- **Reported hyperparameters / reward terms:**
  - imitation reward weights (pose,vel,end-effector,COM): 0.65,0.1,0.15,0.1 (Sec 5.3).
  - pose reward: exp[-2 * sum_j ||q_hat_j (-) q_j||^2] (Sec 5.3).
  - velocity reward: exp[-0.1 * sum_j ||qdot_hat_j - qdot_j||^2] (Sec 5.3).
  - end-effector reward (m): exp[-40 * sum_e ||p_hat_e - p_e||^2] (Sec 5.3).
  - COM reward: exp[-10 * ||p_hat_c - p_c||^2] (Sec 5.3).
  - imitation:task weights: 0.7:0.3 for all tasks (Sec 10).
  - policy rate / sim rate: 30 Hz / 1.2 kHz (Bullet), PD targets as actions, stable PD (Sec 5.1, 10).
  - PPO: batch / minibatch / gamma / GAE lambda / clip: 4096 / 256 / 0.95 / 0.95 / 0.2 (App. D).
  - policy step size / value step size / momentum: 5e-5 (humanoid, Atlas) / 1e-2 / 0.9 (SGD) (App. D).
  - network: MLP 1024-512 ReLU, fixed diagonal Gaussian covariance (Sec 5.2).
  - sample budget: about 60M samples, ~2 days on 8 CPU cores per humanoid skill (App. D).
  - ablation normalized return RSI+ET / ET only / RSI only: Backflip .791/.730/.379; Sideflip .823/.717/.355; Spinkick .848/.858/.358; Walk .980/.981/.974 (Table 5).
  - task objective matters: Throw success 75% (imitation+task) vs 5% (imitation only); Strike 99% vs 19% (Table 4).
  - early termination: torso/head (selected links) contact with ground => episode ends; zero reward for remainder (Sec 6.2).
  - phase limitation: phase advances linearly with time; limits timing adaptation (Sec 11).
- **Code:** https://github.com/xbpeng/DeepMimic; license: **MIT** (GitHub API spdx)
- **Relevance to our pipeline:** Direct template for PPO tracking of a swing clip. Our env differs: single mean-squared-joint-error term, no velocity/end-effector/COM terms, ET only on torso height<0.4, phase = steps/max_steps (not clip progress).

### AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control

- **Link:** https://arxiv.org/abs/2104.02180 (2021, ACM TOG 40(4)); arXiv id: 2104.02180
- **Read level:** `full_text_fetched`
- **Key idea:** Discriminator on state transitions gives a style reward from unstructured clips; no phase/clip selection; combined with a task reward.
- **Reported hyperparameters / reward terms:**
  - task:style weights: 0.5:0.5 for all tasks (Sec 8.2).
  - style reward: max[0, 1 - 0.25 (D - 1)^2], least-squares discriminator (Eq. 7).
  - gradient penalty coefficient: w_gp = 10; found the most vital component (Sec 8.1, 8.5).
  - policy rate / sim rate: 30 Hz / 1.2 kHz (Sec 8.1).
  - budget: 100-300M samples, 30-140 h on 16 CPU cores (Sec 8.1).
  - RSI and early termination: used; ET when any body part except feet touches ground (Sec 6.3).
  - limitation: single-clip AMP converges to local optima (e.g. front-flip shuffle) because pose-deviation ET is not applicable without a phase (Sec 8.4).
- **Code:** https://github.com/xbpeng/rl-mimic (not checked); IsaacGym ports exist; license: **unverified** (official AMP code release not license-checked this session)
- **Relevance to our pipeline:** Fallback if tracking over-constrains the policy. Not first choice: we have one swing style per clip and need precise impact timing; SMPLOlympics reports AMP reward can dominate task reward and AMP/PPO failed golf contact.

### ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters

- **Link:** https://arxiv.org/abs/2205.01906 (2022, ACM TOG 41(4)); arXiv id: 2205.01906
- **Read level:** `partial_text_fetched`
- **Key idea:** AMP-style discriminator + unsupervised skill discovery (latent z) + diversity objective, pre-trained on large unstructured data, then reused by a high-level task policy; recovery from random initial states pre-trained.
- **Reported hyperparameters / reward terms:**
  - gradient penalty: same as AMP (Sec (adversarial training)).
  - diversity objective: w_div term: KL between action distributions scaled by distance between latents (Sec 4).
  - hyperparameters (latent dim, rates): not extracted (-) *(unverified/not extracted)*. Note: existing internal doc cites 64-d latent at 6 Hz [V] - not re-verified here.
- **Code:** https://github.com/nv-tlabs/ASE; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE file not read; repo says deprecated, recommends MimicKit (search snippet))
- **Relevance to our pipeline:** Overkill: needs large diverse data and GPU scale ('over a decade of simulated experience'). Useful only as concept for later hierarchical use of a swing-skill latent.

### Perpetual Humanoid Control for Real-time Simulated Avatars (PHC)

- **Link:** https://arxiv.org/abs/2305.06456 (2023, ICCV 2023); arXiv id: 2305.06456
- **Read level:** `full_text_fetched`
- **Key idea:** Single PPO tracker + AMP reward; progressive multiplicative control policy (PMCP) for hard clips; fail-state recovery; relaxed early termination (RET); hard-negative mining.
- **Reported hyperparameters / reward terms:**
  - reward: r = 0.5 r_task + 0.5 r_amp + r_energy (Eq. 1).
  - imitation reward: w_jp exp(-100||p_hat-p||) + w_jr exp(-10||q_hat (-) q||) + w_jv exp(-0.1||v_hat-v||) + w_jw exp(-0.1||w_hat-w||) (Eq. 2).
  - reward weights jp/jr/jv/jw: 0.5/0.3/0.1/0.1 (App. Table 5).
  - energy penalty: -0.0005 * sum_j |mu_j * omega_j|^2 (torque x joint velocity); prevents foot jitter (Sec 3.1).
  - early termination: mean joint distance to reference > 0.5 m; ankle/toe removed from criterion (RET) (Sec 3.1).
  - success definition: mean joint error > 0.5 m at any time = failure (Sec 4 metrics).
  - RSI: random start point in clip (Sec 3.1).
  - control / sim rate: 30 Hz / 60 Hz (Isaac Gym) (Sec 4).
  - PPO batch / sigma / gamma / clip: 1536 envs / 0.05 / 0.99 / 0.2 (App. Table 5).
  - learning rate: printed as '5 x 2^-5' in the HTML rendering (App. Table 5) *(unverified/not extracted)*. Note: almost certainly 5e-5 (rendering/typo); treat as UNVERIFIED.
  - network: MLP [1024, 512] for policy, value and discriminator (Sec 3.1).
  - PMCP effect (noisy video ablation success): 1 primitive 59.4% -> 4 primitives 88.7% (Table 6/3).
  - hard negative mining: re-train on sequences the current policy fails (Sec 3.1).
  - action: PD targets, not residual on reference (robust to noisy references) (Sec 3.1).
  - compute: ~7 days, ~10B samples, 1536 envs, A100 (App. Training Process).
- **Code:** https://github.com/ZhengyiLuo/PHC; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE file not read; do not assume commercial use)
- **Relevance to our pipeline:** Relaxed termination (tolerate non-critical joints) and energy penalty are directly applicable: wrist/club-hand tracking should be relaxed in the impact window, torso/pelvis strict. Video-derived Mason refs are noisy => PD-target action space, not residual.

### Universal Humanoid Motion Representations for Physics-Based Control (PULSE)

- **Link:** https://arxiv.org/abs/2310.04582 (2023, ICLR 2024); arXiv id: 2310.04582
- **Read level:** `abstract_only`
- **Key idea:** Distill PHC-style imitator into a variational latent space + proprioception-conditioned prior; hierarchical RL in the latent space for tasks.
- **Reported hyperparameters / reward terms:**
  - claims: latent space from all-human-motion imitator; used for hierarchical RL on strike, terrain, VR tracking (abstract).
  - success rates quoted by internal doc (99.8% train / 97.1% test): see repo_methods_doc (-) *(unverified/not extracted)*. Note: not re-verified this session.
- **Code:** https://github.com/ZhengyiLuo/PULSE; license: **none detected** (GitHub API returned no license => all rights reserved by default; ask before reuse)
- **Relevance to our pipeline:** SMPLOlympics reports only PULSE/PULSE+AMP solved golf contact reliably; needs SMPL humanoid + GPU (we have 8 CPU cores, no GPU).

### MaskedMimic: Unified Physics-Based Character Control Through Masked Motion Inpainting

- **Link:** https://arxiv.org/abs/2409.14393 (2024, ACM TOG 43(6)); arXiv id: 2409.14393
- **Read level:** `abstract_only`
- **Key idea:** Train full-body tracker, then distill into a masked-inpainting policy conditioned on sparse keyframes/text/scene.
- **Reported hyperparameters / reward terms:**
  - two-stage recipe: 1) full-body tracker (transformer) 2) MaskedMimic distilled from tracker with random masking (ProtoMotions README (search snippet)).
  - public checkpoint scope: SMPL & G1, masked body/time targets, no text control in SMPL card (ProtoMotions model card (search snippet)).
- **Code:** https://github.com/NVlabs/ProtoMotions; license: **Apache-2.0** (ProtoMotions repo license per GitHub API (covers MaskedMimic impl.); model weights/data terms not checked)
- **Relevance to our pipeline:** Later: specify only club-path/impact keyframes and let policy inpaint the rest. Not for first PPO milestone.

### Expressive Whole-Body Control for Humanoid Robots (ExBody)

- **Link:** https://arxiv.org/abs/2402.16796 (2024, RSS 2024); arXiv id: 2402.16796
- **Read level:** `search_snippet_only`
- **Key idea:** Expressive whole-body control; per GMT related work, ExBody decouples upper-body and lower-body control (compromise expressiveness vs balance).
- **Reported hyperparameters / reward terms:**
  - details: not read (-) *(unverified/not extracted)*. Note: only second-hand description from GMT Sec 2.2 and Table 1 (780 clips).
- **Code:** https://github.com/chengxuxin/expressive-humanoid; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE not read)
- **Relevance to our pipeline:** Counter-example for golf: golf is whole-body (pelvis/thorax rotation drives club speed); decoupling would hurt.

### ExBody2: Advanced Expressive Humanoid Whole-Body Control

- **Link:** https://arxiv.org/abs/2412.13196 (2024); arXiv id: 2412.13196
- **Read level:** `partial_text_fetched`
- **Key idea:** Generalist/specialist training, automatic dataset filtering, decoupled keypoint tracking (in local frame) vs velocity control, privileged teacher -> student.
- **Reported hyperparameters / reward terms:**
  - local-frame keypoints: keypoints converted to local frame; velocity tracking guides movement, keypoints do imitation; global keypoint tracking (H2O/OmniH2O) fails when robot cannot align to global keypoints (Intro (iii)).
  - teacher privileged info: real root velocity, accurate body link positions, friction etc. (Intro).
  - reward weights / hyperparameters: not extracted (App. B-C) *(unverified/not extracted)*. Note: section exists (Reward Design) but values not read.
- **Code:** https://github.com/edpsw/exbody2; license: **NVIDIA non-commercial (secondary source: DeepWiki; GitHub: Other)** (secondary source only, verify LICENSE file)
- **Relevance to our pipeline:** Supports using root-relative (local) key-body targets for club/hands; our swing is stationary so global drift is a smaller concern.

### Learning Human-to-Humanoid Real-Time Whole-Body Teleoperation (H2O)

- **Link:** https://arxiv.org/abs/2403.04436 (2024, IROS 2024); arXiv id: 2403.04436
- **Read level:** `partial_text_fetched`
- **Key idea:** 'sim-to-data': train a privileged imitator without DR to filter infeasible retargeted clips (about 8.5k of 10k AMASS retained for H1), then DR-trained real-time imitator.
- **Reported hyperparameters / reward terms:**
  - early termination: base height < 0.3 m; projected gravity x or y > 0.7; mean link distance to reference > 0.5 m (Sec V-D).
  - feasibility filter: privileged imitator (PHC/PULSE recipe) w/o DR; failures = implausible clips (Sec IV).
- **Code:** https://github.com/LeCAR-Lab/human2humanoid; license: **none detected** (GitHub API returned no license)
- **Relevance to our pipeline:** Do the same audit on our unified refset: run a privileged tracker and drop/downweight clips it cannot track (candidate cause of 'timing errors').

### OmniH2O: Universal and Dexterous Human-to-Humanoid Whole-Body Teleoperation and Learning

- **Link:** https://arxiv.org/abs/2406.08858 (2024, CoRL 2024); arXiv id: 2406.08858
- **Read level:** `search_snippet_only`
- **Key idea:** Teacher with privileged state -> student with sparse sensors; 'max feet height per step' reward + curriculum to stop stomping.
- **Reported hyperparameters / reward terms:**
  - student history: 25-step history (search snippet) (-) *(unverified/not extracted)*. Note: snippet-level.
  - key regularizer: max feet height per step reward, introduced via curriculum (Sec 4 (search snippet)).
- **Code:** https://github.com/LeCAR-Lab/human2humanoid; license: **none detected** (same repo as H2O; GitHub API returned no license)
- **Relevance to our pipeline:** Pattern: introduce shaping/regularization terms via curriculum rather than from step 0.

### HumanPlus: Humanoid Shadowing and Imitation from Humans

- **Link:** https://arxiv.org/abs/2406.10454 (2024, CoRL 2024); arXiv id: 2406.10454
- **Read level:** `search_snippet_only`
- **Key idea:** Shadow human (RGB pose) to humanoid; low-level policy trained in sim on large mocap; imitation learning of skills.
- **Reported hyperparameters / reward terms:**
  - data: 10k clips (per GMT Table 1) (GMT Table 1) *(unverified/not extracted)*. Note: second-hand.
  - details: not read (-) *(unverified/not extracted)*.
- **Code:** https://github.com/MarkFzp/humanplus; license: **none detected** (GitHub API returned no license)
- **Relevance to our pipeline:** Context only; no golf-specific lessons extracted.

### TWIST: Teleoperated Whole-Body Imitation System

- **Link:** https://arxiv.org/abs/2505.02833 (2025, CoRL 2025); arXiv id: 2505.02833
- **Read level:** `partial_text_fetched`
- **Key idea:** Real-time whole-body teleop via retargeting + tracking; two-stage teacher (sees future frames) -> student (single current frame); mix of 15K offline clips with 150 online-mocap clips to close offline->online gap.
- **Reported hyperparameters / reward terms:**
  - single-frame observation => hesitant behavior; teacher with privileged future frames gives smoother behavior: qualitative (Intro).
  - training mix: 15K offline clips + 150 online-mocap clips (Intro).
  - retargeting: jointly optimizing 3D joint positions and orientations narrows offline-online gap (Intro).
- **Code:** https://github.com/YanjieZe/TWIST; license: **MIT** (GitHub API spdx)
- **Relevance to our pipeline:** Supports giving our tracker a short future-reference window (impact anticipation) instead of only the current frame.

### GMT: General Motion Tracking for Humanoid Whole-Body Control

- **Link:** https://arxiv.org/abs/2506.14770 (2025); arXiv id: 2506.14770
- **Read level:** `full_text_fetched`
- **Key idea:** Single unified tracker via adaptive sampling (random clipping + performance-based sampling probability) and motion mixture-of-experts; long future window.
- **Reported hyperparameters / reward terms:**
  - reward terms (all exp(-||err||^2) unless noted): joint pos, joint vel, root pose (roll/pitch+height), root vel, key body pos, alive=1.0, foot slip, joint vel, joint acc, action rate penalties (Table 3).
  - control / sim rate: 50 Hz / 500 Hz, IsaacGym, 4096 envs, ~6.8B samples (Sec 4.1, 6.5).
  - adaptive termination threshold: E_i = 0.25 exp((c_i-1)/9 * ln(0.6/0.25)); c_i starts 10, x0.99 on each completion, min 1 (threshold tightens 0.6 -> 0.25) (Sec 3.1). Note: units of E_i not stated in the text read.
  - sampling level: s_i = c_i if c_i>1 else (min(E_max_keybody/0.15,1))^5; probability = normalized s_i (Eq. 1).
  - random clipping: clips >10 s cut into <=10 s sub-clips with random offset up to 2 s, re-clipped periodically (Sec 3.1).
  - future window: stacked frames covering ~2 s (100 frames) encoded by conv encoder, plus immediate next frame; next-frame-only is worse; window-only (no next frame) is worst (Sec 3.4, Table 2(b)).
  - ablation (AMASS-test E_mpkpe mm): full 42.07; w/o MoE 42.53; w/o AS 43.54; w/o both 44.34 (Table 2).
  - domain randomization: friction [0.1,2.0]; base mass +-3 kg; base COM +-0.05 m; push 0-1 m/s; motor strength [0.8,1.2]; action delay [0,0.02] s; gravity +-0.1; terrain height [0,0.02] m (Table 4).
  - armature: armature = k^2 * I (reduction ratio squared x drive inertia) (Sec 6.2).
  - data curation: rule-based filter (root roll/pitch/height) + preliminary-policy completion filter => 8925 clips / 33.12 h (Sec 3.3).
- **Code:** https://github.com/zixuan417/humanoid-general-motion-tracking; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE not read)
- **Relevance to our pipeline:** Adaptive sampling + tolerance curriculum map to per-phase sampling (backswing/downswing/impact) and a tightening tracking threshold; future window supports impact anticipation.

### BeyondMimic: From Motion Tracking to Versatile Humanoid Control via Guided Diffusion

- **Link:** https://arxiv.org/abs/2508.08241 (2025); arXiv id: 2508.08241
- **Read level:** `full_text_fetched`
- **Key idea:** Compact tracking MDP (one task term per quantity + 3 regularizers), same hyperparameters across motions, adaptive sampling over 1 s bins, minimal DR, careful actuation modelling (armature, PD gains from natural frequency).
- **Reported hyperparameters / reward terms:**
  - task reward: sum over {pos,ori,lin vel,ang vel}: exp(-mean_sq_err / sigma^2), uniform weights over target bodies (Sec Rewards).
  - sigmas: pos 0.3, ori 0.4, lin vel 1.0, ang vel 3.14 (Supp. Reward).
  - regularizers: joint-limit (soft limits 0.9x), action-rate ||a_t-a_{t-1}||, self-contact count (f>1 N); weights printed as -10.0, -0.1, -0.1 (Supp. Reward). Note: sign as printed; magnitudes 10/0.1/0.1.
  - optional global anchor term weight: 0.5 (Supp. Reward).
  - termination: anchor or end-effector |z error| > 0.25 m, or anchor orientation error > 0.8 rad (Supp. Termination).
  - adaptive sampling: 1 s bins; EMA failure rate f <- 0.999 f + 0.001 f_s; floor 0.1/S; look-back kernel rho=0.8 over 3 bins; sampled phase init + small pose noise (xy +-0.05 m, z +-0.01 m, roll/pitch +-0.1 rad, yaw +-0.2 rad) (Supp. Termination/Adaptive).
  - ablation effect: without adaptive sampling 3 of 4 motions fail hard segments after 30k iters; easy motion needs 2k vs 4k iters (Fig 8B text).
  - PD gains: kp = I w^2, kd = 2 I zeta w with zeta=2, natural freq 10 Hz, I = reflected armature; action scale alpha = 0.25 tau_max / kp (Supp. Heuristic).
  - domain randomization: static friction U(0.3,1.6), dynamic U(0.3,1.2), restitution U(0,0.5); default joint offset +-0.01 rad (ankle +-0.1); torso COM +-(0.025,0.05,0.05) m; velocity pushes every 1-3 s +-(0.5,0.5,0.2) m/s (Supp. DR).
  - observation findings: Rot6D better than quaternion/axis-angle for sim-to-real; adding history hurt in their setup; zero-armature causes overswing; latency 2 ms raises vel error, 5 ms one failure, 10 ms two of three failures (Validation section).
  - asymmetric actor-critic: critic also sees per-body anchor-relative poses (Supp. Observation).
- **Code:** https://github.com/HybridRobotics/whole_body_tracking; license: **MIT** (GitHub API spdx)
- **Relevance to our pipeline:** Best single recipe for our PPO tracker. A golf downswing is a short, fast motion with a hard impact: BeyondMimic shows velocity terms + adaptive phase sampling + accurate actuator model are what make agile segments work.

### UniTracker: Learning Universal Whole-Body Motion Tracker for Humanoid Robots

- **Link:** https://arxiv.org/abs/2507.07356 (2025); arXiv id: 2507.07356
- **Read level:** `abstract_only`
- **Key idea:** Three-stage: privileged teacher -> CVAE universal policy (global latent aligning partial-observation prior with full-observation encoder) -> lightweight adaptation module on hard sequences.
- **Reported hyperparameters / reward terms:**
  - details: abstract only; hyperparameters not extracted (abstract) *(unverified/not extracted)*.
- **Code:** https://github.com/yinkangning0124/Humanoid-UniTracker; license: **none detected** (GitHub API returned no license)
- **Relevance to our pipeline:** Adaptation-on-hard-clips is the same idea as PHC hard-negative mining; later stage only.

### KungfuBot (PBHC): Physics-Based Humanoid Whole-Body Control for Learning Highly-Dynamic Skills

- **Link:** https://arxiv.org/abs/2506.12851 (2025); arXiv id: 2506.12851
- **Read level:** `partial_text_fetched`
- **Key idea:** Physics-based motion filtering/correction of video-extracted references + adaptive tracking-factor sigma in exp(-x/sigma) rewards (sigma tightens as the policy improves).
- **Reported hyperparameters / reward terms:**
  - tracking reward form: r(x) = exp(-x/sigma), x = MSE error, sigma = tracking factor (Sec 3.2.1).
  - optimal sigma (derived under assumptions): sigma* = mean of optimal tracking error over trajectory (Eq. 7).
  - adaptive rule: maintain EMA of instantaneous tracking error x_hat; sigma <- min(sigma, x_hat); non-increasing; large sigma_init (Eq. 8).
  - phase variable and RSI: time phase phi in [0,1] in actor obs; RSI at random phases (Sec 3.3).
  - asymmetric actor-critic, reward vectorization: separate value head per reward term, advantages aggregated (Sec 3.3).
  - reference smoothing: EMA smoothing applied after floating correction to remove frame jitter (Sec 3.1).
- **Code:** not checked; license: **unverified** (not checked)
- **Relevance to our pipeline:** Our references come from video (noisy, ~30 fps). Adaptive sigma avoids hand-tuning the loose 0.5 in our current reward; per-term value heads help when impact reward and tracking reward have very different scales.

### Perceptive Humanoid Parkour: Chaining Dynamic Human Skills via Motion Matching (PHP)

- **Link:** https://arxiv.org/abs/2602.15827 (2026); arXiv id: 2602.15827
- **Read level:** `search_snippet_only`
- **Key idea:** Motion matching composes retargeted clips into long references; privileged RL experts distilled into one depth policy (DAgger + RL).
- **Reported hyperparameters / reward terms:**
  - details: search snippet only (-) *(unverified/not extracted)*.
- **Code:** https://github.com/amazon-far/php_parkour; license: **Apache-2.0** (GitHub API spdx)
- **Relevance to our pipeline:** Low: parkour/perception; the privileged-expert -> distillation pattern recurs.

### SMPLOlympics: Sports Environments for Physically Simulated Humanoids

- **Link:** https://arxiv.org/abs/2407.00187 (2024); arXiv id: 2407.00187
- **Read level:** `partial_text_fetched`
- **Key idea:** Sports benchmark (golf, tennis, table tennis...) for SMPL humanoids; baselines PPO, AMP, PULSE, PULSE+AMP; video-derived motion used as AMP prior.
- **Reported hyperparameters / reward terms:**
  - golf setup: right hand replaced by 1.14 m club, driver head box 0.05x0.025x0.02 m, wave terrain amplitude 0.5 m, goal 0-20 m to the left (Sec golf + Supp).
  - golf reward: w_p r_p + w_c r_c + w_g r_g + w_pred r_pred, all weights 1 (Supp (golf)).
  - r_p: clamp(||p_ball(t-1) - p_tar|| - ||p_ball(t) - p_tar||, 0, 1) (Supp).
  - r_c (contact): exp(-100 ||p_ball - p_club||^2) before contact, 1 after contact (Eq. 5).
  - r_g: exp(-0.1 ||p_ball,xy - p_tar,xy||^2) (Supp).
  - r_pred (predicted landing): exp(-0.1 ||p_land - p_ball,xy||^2), landing from ball pos/vel ballistic formula (Eq. 6).
  - early termination (golf): ball moves backward; no club contact within 2 s; ball too close to body; humanoid falls (Supp).
  - finding: for golf/penalty/free-throw 'initiating contact' is a sparse-exploration problem; only PULSE and PULSE+AMP solved it consistently; PPO/AMP exhibit inhuman strategies (Sec results).
  - finding: AMP reward can conflict with task reward (tennis): long rallies raise discriminator reward, policy ignores task (Sec results).
  - results table (hit rate etc.): not transcribed (Table 2) *(unverified/not extracted)*.
- **Code:** https://github.com/SMPLOlympics/SMPLOlympics; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE not read)
- **Relevance to our pipeline:** Only published humanoid golf RL reward found; our env's contact term is exp(-3*dist) (very wide) vs exp(-100*d^2) here, and ours lacks a predicted-landing dense term (we have analytic ball flight in env/ball_flight_analytic.py).

### PhysHOI: Physics-Based Imitation of Dynamic Human-Object Interaction

- **Link:** https://arxiv.org/abs/2312.04393 (2023); arXiv id: 2312.04393
- **Read level:** `abstract_only`
- **Key idea:** Imitate human-object interaction with a contact-graph reward instead of task-specific rewards (BallPlay dataset: 8 basketball skills).
- **Reported hyperparameters / reward terms:**
  - claim: contact graph reward 'proved to be critical for precise HOI imitation' (abstract).
  - reward coefficients: not extracted (-) *(unverified/not extracted)*.
- **Code:** https://github.com/wyhuai/PhysHOI; license: **custom (GitHub: NOASSERTION/Other)** (LICENSE not read)
- **Relevance to our pipeline:** Idea: reward matching the reference's contact event (club-ball contact timing/position) instead of only distance.

### Learning Physically Simulated Tennis Skills from Broadcast Videos (Vid2Player3D)

- **Link:** https://doi.org/10.1145/3592408 (2023, ACM TOG 42(4)); arXiv id: (no arXiv id used)
- **Read level:** `search_snippet_only`
- **Key idea:** Hierarchical: low-level imitation tracker on corrected video-derived motion + high-level RL that picks latent/wrist-elbow corrections to hit a target.
- **Reported hyperparameters / reward terms:**
  - ball state input: next 10 predicted ball positions (paper (search snippet)) *(unverified/not extracted)*. Note: snippet-level.
  - reward structure: racket-to-ball alignment before contact; after contact bounce-position and spin-direction rewards (paper (search snippet)) *(unverified/not extracted)*.
  - curriculum: three stages: approach ball -> fixed target zones -> continuous targets (paper (search snippet)) *(unverified/not extracted)*.
- **Code:** https://github.com/nv-tlabs/vid2player3d; license: **custom (GitHub: NOASSERTION/Other); trained models not released** (LICENSE not read)
- **Relevance to our pipeline:** Template for our curriculum: contact first, then fixed-distance targets, then ladder speed targets. Video-derived reference needed wrist correction by high-level policy (noisy hand motion) - analogous to our video refs.

## 3. Cross-cutting techniques (what the evidence says)

| Topic | Evidence | What we do |
|---|---|---|
| Reference-state init (RSI) | DeepMimic Table 5: backflip 0.379 (RSI only, no ET) vs 0.730 (ET only) vs 0.791 (both); spinkick .358/.858/.848; walk barely changes (.974/.981/.980). So RSI matters for dynamic, ballistic phases; ET matters broadly. | R02 |
| Early termination | DeepMimic (ground contact of torso/head), PHC 0.5 m mean joint error with relaxed ankles/toes, H2O (z<0.3 m, gravity proj>0.7, 0.5 m link error), BeyondMimic (0.25 m z / 0.8 rad), GMT (0.6 to 0.25 tightening), SMPLOlympics golf (ball backward, no contact in 2 s, too close, fall). | R03 |
| Phase variable | DeepMimic and KungfuBot feed phi in [0,1]; AMP/ASE/PULSE avoid it (no clip sync). DeepMimic lists the linear-time phase as a limitation (limits timing adaptation). BeyondMimic feeds reference joint pos/vel as a progress cue. | R01, R12 |
| Tracking reward shaping | Exponential per-term rewards everywhere; velocity terms in DeepMimic/PHC/GMT/BeyondMimic; KungfuBot adaptive sigma; BeyondMimic uses sigma^2 form with sigmas 0.3/0.4/1.0/3.14. | R04, R05 |
| Regularization | Action rate, joint limits, energy (PHC -0.0005), feet-height (OmniH2O, via curriculum). | R06 |
| Curriculum | DeepMimic progressive (flat to terrain); tennis 3-stage (snippet-level); GMT completion-level threshold curriculum; OmniH2O regularizer curriculum. | R08 |
| Adaptive sampling | BeyondMimic 1 s bins; GMT performance-based; PHC hard-negative mining/PMCP (1 to 4 primitives: 59.4% to 88.7% success on noisy video). | R09 |
| Domain randomization | BeyondMimic compact set; GMT table. Both flag latency/armature as first-order. | R13 |
| Sim2real | Teacher-student (TWIST, GMT, ExBody2, OmniH2O), armature k^2 I (GMT, BeyondMimic), 2-10 ms latency sensitivity (BeyondMimic). | R11, R17 |
| Ball-sport task terms | SMPLOlympics golf/tennis/table tennis; PhysHOI contact graph; tennis pre/post contact rewards; DeepMimic strike/throw `exp(-4 d^2)` target reward with 0.2 m hit radius. | R07 |

## 4. Read-only audit of our env/train against the literature

| Item | Finding (origin/main `a5df07b`) | File | Severity | Rec |
|---|---|---|---|---|

| reference indexing | ref_idx = min(len(joints)-1, episode_steps); reference['dt'] loaded but unused | `env/humanoid_golf_env.py:481` | high | R01 |
| phase variable | phase = episode_steps/max_steps (max_steps=200), not clip progress | `env/humanoid_golf_env.py:413-414` | high | R01 |
| termination | torso height<0.4 (disabled if pin_torso) or max_steps; no tracking-error ET | `env/humanoid_golf_env.py:487` | high | R03 |
| imitation reward | 2.0*exp(-mean(sq joint err rad)/0.5) (+1.5*exp(-club_err/0.5) in legacy); no velocity/orientation/COM terms | `env/humanoid_golf_env.py:238,302-309` | medium | R04 |
| contact reward | legacy 1.5*exp(-3*dist); curriculum 1.5*w_contact*exp(-3*dist); SMPLOlympics uses exp(-100*d^2) | `env/humanoid_golf_env.py:228,317` | medium | R07 |
| action space | direct torque ctrl = clip(action)*torque_scale (legacy 10); PD hook _substep_ctrl exists | `env/humanoid_golf_env.py:417` | medium | R11 |
| PPO config | SB3 PPO MlpPolicy lr 3e-4, n_steps 2048, batch 64, epochs 10, gamma .99, n_envs 4 | `train/train_ppo.py:111-122` | low | R14 |
| RSI | reset sets ref_idx=0 / phase 0; no random-phase reset visible in reset() | `env/humanoid_golf_env.py:374-375` | high | R02 |

No files in `env/`, `eval/`, `train/` were modified by this work. Line numbers refer to the committed version.

## 5. Suggested first experiment (small, reversible)

1. Single clip: one Mason clip from the unified refset *train* split (NOT the val clips p1_s06, p1_s11, p2_s01), R01 + R02 + R03 + R04 only, task weight 0, 8 envs, DeepMimic-order budget scaled down; success = completes clip with mean key-body error < 0.25 m.
2. Add R07 contact term (stage B) and measure contact rate on val clips.
3. Only then multi-clip (unified refset sampling 0.6/0.2/0.2) with R09 adaptive sampling, then the speed ladder.

## 6. Unverified items and caveats

- Whether the Orchestrator's '0.4 s bug' equals the 2x reference-clock mismatch in R01 (not verified).
- All numeric weights marked 'ours' in recommendation parameters (R04, R06, R07, R08, R09, R10, R12, R13, R14) are engineering starting points, not paper values.
- PHC learning rate (printed '5 x 2^-5').
- Hyperparameters not extracted: ASE, ExBody/ExBody2 reward values, H2O/OmniH2O reward weights, HumanPlus, UniTracker, PhysHOI contact-graph coefficients, tennis paper numbers (snippet-level), SMPLOlympics result tables.
- Code licenses marked 'custom'/'none detected'/'unverified' were not read from LICENSE files; treat as not cleared for commercial use.
- No paper reports a club-speed-at-impact reward or a 350 yd/150 mph target; the speed-ladder reward in R07 is our design.
- Papers' results are on SMPL humanoids or Unitree G1/H1 with PD control and GPU-scale sampling; transfer to this MuJoCo CPU env is untested.
- Style-profile language only: this is a methods survey; no player likeness data is used.
- No video was scraped; only arXiv/GitHub text was fetched.
- Do not copy third-party code with custom/non-commercial licenses into the commercial pipeline without legal review.

## 7. Not covered / follow-ups

- ASAP (delta-action sim-to-real), HOVER, Vid2Player (2D), table-tennis imitation (Wang 2024), minigolf phase-adaptation (Ewerton 2016) appear in `docs/research_methods.md` or were not read here.
- LICENSE files for repos marked custom were not read; do a legal pass before any code reuse (ExBody2 reported non-commercial).
- Ablation of R01-R04 on our env is the real test; none of the paper numbers transfer automatically.
