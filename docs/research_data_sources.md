# Research: legally usable data for a golf-swing humanoid training set

Prepared 2026-10-16 (ET). **Not committed or pushed.** No video was downloaded. License text below was fetched from the primary source pages on this date unless marked **[secondary]** (reported by a search summary, not read on the primary page) or **[unverified]**. This is engineering diligence, not legal advice. Get counsel's sign-off before shipping a commercial product.

Legend: GREEN = commercial use stated OK. AMBER = ambiguous or conditional. RED = non-commercial, or no license (so default copyright applies).

---------------------------------------------------------------------
## 0. Bottom line

1. The only **clearly commercial-safe, golf-containing, 3D** source found is **CMU Graphics Lab Mocap**, subject 64 (already converted, 10 swings). The KIT "play golf" clips are free to the scientific community, but no commercial grant was found. Treat KIT as RED until KIT confirms in writing.
2. **AMASS, BEDLAM, Motion-X, HuMMan, Human3.6M, GolfDB and the Kaggle Golf-Pose set all prohibit commercial use** (quotes below). AMASS is the trap: it re-hosts CMU and KIT, but the AMASS license forbids commercial use and even forbids training commercial networks. **Get CMU from CMU directly, never through AMASS.**
3. **Mason's own swings are the highest-value legal data** (own IP, golf-specific, real speed). CMU is slow (tempo ~1.7:1) and is best used as a sequencing prior only.
4. For elite-swing **targets**, use published biomechanics numbers (facts and measurements are not copyrightable, and the papers are cited). Section 2 gives a numeric profile for a style reward.
5. Ball and club rules (USGA/R&A) are public. TrackMan tour averages give a calibration target. CaddieSet (MIT) is the only open shot-level ball-flight dataset found.

---------------------------------------------------------------------
## 1. Motion / mocap datasets

| Dataset | Golf content | License (primary text) | Commercial? |
|---|---|---|---|
| **CMU Mocap** (mocap.cs.cmu.edu) | Subject 64, golf trials (10 swings converted locally) | "free for all uses" | **GREEN** (with limits) |
| **KIT Whole-Body Human Motion DB** | "play golf" category, Subject #3 etc. | Free to "the whole scientific community"; account needed | **RED/AMBER** (no commercial grant) |
| **AMASS** | Aggregates CMU, KIT, etc. | Non-commercial only | **RED** |
| **BEDLAM** | None (synthetic people, generic motions via AMASS) | Non-commercial only | **RED** |
| **Motion-X** | Includes sports videos (golf likely among its categories, unverified) | Non-commercial only | **RED** |
| **HuMMan** | Actions are generic, golf not confirmed | S-Lab License 1.0, non-commercial | **RED** |
| **Human3.6M** | No golf (15 daily activities) | Academic-only EULA | **RED** |
| **AIST++ / AIST Dance DB** | None (dance) | CC BY 4.0 [secondary] | GREEN but irrelevant to golf |
| **GolfDB** | ~1,400 labeled swings, 248 players | Repo CC BY-NC 4.0, videos are YouTube content | **RED** |
| **GolfPose / GolfSwing 3D** | Real 3D mocap keypoints, 17 body + 5 club [secondary] | No license stated, email authors | **RED** until the authors grant rights in writing |
| **CaddieSet** (CVPRW 2025) | 1,757 shots, 8 golfers, 2D joints, ball-flight | MIT (repo LICENSE file) | **GREEN** for the repo, but see the caveat |
| **Kaggle "Golf-Pose"** | 2D pose, not verified | CC BY-NC-SA 4.0 [secondary] | **RED** |
| **Mixamo** | Golf animations exist (not verified) | Royalty-free, no raw redistribution [secondary] | **AMBER** |

### 1.1 Quoted license text and notes

**CMU** (http://mocap.cs.cmu.edu/, fetched 2026-10-16):
> "This dataset of motions is free for all uses."
> "This data is free for use in research projects. You may include this data in commercially-sold products, but you may not resell this data directly, even in converted form. If you publish results obtained using this data, we would appreciate it if you would send the citation to your published paper to contact per CMU terms (http://mocap.cs.cmu.edu), and also would add this text to your acknowledgments section: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217."

FAQ page (http://mocap.cs.cmu.edu/faqs.php): "The motion capture data may be copied, modified, or redistributed without permission."

Obligations to follow: (a) don't resell or publish the converted `.npz` files as a standalone dataset, (b) add the acknowledgment sentence above to credits and README, (c) the data can be inside a commercial product and can train a model. The statements are slightly inconsistent ("redistributed without permission" vs "may not resell directly"). Follow the stricter one. Note CMU's own warning: "the same person may appear under more than one subject number", and hand and finger joints are noisy or not captured. That matters for grip and wrist targets.

**AMASS** (https://amass.is.tue.mpg.de/license.html):
> "To use the Dataset for the sole purpose of performing non-commercial scientific research, non-commercial education, or non-commercial artistic projects; Any other use, in particular any use for commercial purposes, is prohibited. This includes, without limitation, incorporation in a commercial product, use in a commercial service, or production of other artefacts for commercial purposes."
> "This license also prohibits the use of the Dataset to train methods/algorithms/neural networks/etc. for commercial use of any kind."

Commercial licensing contact stated: contact per the licensor terms (see the license URL above). The `.npz` files we derive from AMASS would count as "other artefacts". **Do not use AMASS-derived data**, including AMASS-derived collections such as HumanML3D.

**BEDLAM** (https://bedlam.is.tue.mpg.de/license.html): "...in particular any use for commercial, pornographic, military, or surveillance, purposes is prohibited. This includes, without limitation, incorporation in a commercial product, use in a commercial service, or production of other artifacts for commercial purposes." Commercial contact: the licensor contact named on the BEDLAM license page.

**Motion-X** (GitHub LICENSE, fetched via search result; annotations PDF): "Any other use, in particular any use for commercial, pornographic, military, or surveillance, purposes is prohibited." Annotations are CC BY-NC-SA 4.0: "You may not use the material for commercial purposes." It also says each sub-dataset has its own license (AMASS, GRAB custom licenses; BAUM, AIST++, EgoBody CC-BY 4.0; HuMMan S-Lab; IDEA400 CC BY-SA 4.0). The source videos are "from online source", so there is third-party video copyright too.

**HuMMan** (http://caizhongang.com/projects/HuMMan/license.txt, S-Lab License 1.0): "Redistribution and use for non-commercial purpose in source and binary forms ... are permitted ..." and "4. In the event that redistribution and/or use for commercial purpose in source or binary forms, with or without modification is required, please contact the contributor(s) of the work."

**Human3.6M** (https://vision.imar.ro/human3.6m/eula.php): the quoted section says "seek prior written permission from the authors and pay any additional fees or royalties, as may be required, for any uses not permitted or not specified in this agreement." Search result summary says academic use only. I could not read the full grant clause in the fetch, so the academic-only reading is **[secondary]**. Either way it has no golf, so skip it.

**KIT** (https://motion-database.humanoids.kit.edu/faq/): "In general, we aim to make content freely available to the whole scientific community." Downloads require a free account. No license grant for commercial use is stated. The Master Motor Map software is GPL, which is separate from the data. The category list has "play golf". **Action:** email KIT H²T (Prof. Asfour's lab) and ask for written commercial-use terms before using it. The citation text is on their pages (Mandery et al., IEEE T-RO 2016).

**GolfDB** (https://github.com/wmcnally/golfdb): "The code in this repository is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License." The dataset is annotations over 580 YouTube videos (paper: "A collection of 580 YouTube videos ... professional golfers from the PGA, LPGA and Champions Tours, totalling 248 individuals"). The videos belong to third parties. Matches the earlier project finding: **do not use GolfDB for the commercial product**. It is fine for internal, non-shipped experiments only if counsel agrees, and that is not recommended.

**CaddieSet** (https://github.com/damilab/CaddieSet): LICENSE is the standard MIT text. The data is "Swing videos and ball flight estimates of 8 individuals" with joint features (2D, camera-based) and ball data (Distance, Carry, DirectionAngle, SpinBack, SpinSide, BallSpeed). Caveat: MIT covers the repo, but I could not confirm whether the human participants consented to commercial reuse. The README only describes the data as "intended for research and analysis". Treat as GREEN for ball-flight statistics (non-personal numbers), AMBER for joint features. Cite: Jung et al., CVPRW 2025.

**GolfPose** (https://github.com/MingHanLee/GolfPose): README says "Please email the contact given in the GolfPose README (https://github.com/MingHanLee/GolfPose) to authorize the dataset download." The repo shows no license text. Data contains `data_3d_golf_gt.npz`. No license means all rights reserved, so ask the authors for a written commercial grant before use. High value if granted (real 3D golf keypoints with club).

**Mixamo** [secondary, Adobe FAQ via search]: royalty-free for personal, commercial and nonprofit projects, but you may not distribute raw character or animation files separately. Animations are keyframed or captured by Mixamo, not elite swings, and carry no verified golf swing quality. Low priority. Also check Adobe's current terms on ML training use, which I did not verify.

### 1.2 Recommendation for the dataset
1. **Tier 1 (use now):** CMU subject 64 (sequencing prior), Mason's own swings (best), published biomechanics numbers (targets, Section 2).
2. **Tier 2 (ask first, in writing):** GolfPose authors (3D golf), KIT H²T (golf mocap), AMASS commercial license (contact per the licensor terms (see the license URL above)) if the budget exists.
3. **Tier 3 (never for the product):** GolfDB, Motion-X, BEDLAM, HuMMan, Human3.6M, Kaggle Golf-Pose, AMASS-derived data.
4. **Collect our own:** the cleanest long-term answer. A few hundred swings from consenting golfers (signed release that covers commercial ML use), from phone video plus a pose lifter chosen for license cleanliness. Check the pose model's license too (several, e.g. SMPL-family models, are non-commercial).

---------------------------------------------------------------------
## 2. Elite driver biomechanics and an "ideal driver swing profile"

### 2.1 Primary sources read for this section
- **Cheetham, Rose, Hinrichs, Neal, Mottram, Hurrion, Vint (2008).** "Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers." Science and Golf V, pp. 30-36. 19 PGA Tour pros vs 19 amateurs, 240 Hz electromagnetic 3D capture (TPI database). Full text read. Numbers below are from its Table 1.
- **Hume, Keogh, Reid (2005).** "The role of biomechanics in maximising distance and accuracy of golf shots." Sports Med 35(5):429-449. Full text read.
- Primary studies cited inside Hume 2005 that I did **not** read directly: Cochran & Stobbs 1968 (tempo), McLean 1992/93 (X-factor), McTeigue et al. 1994, Cheetham et al. 2000 (X-factor stretch), Barrentine et al. 1994 (GRF), Sprigings & Neal 2000 (wrist torque), Burden et al. 1998. They are quoted through Hume.
- TrackMan tour averages (ball and club numbers): see 3.1.
- TPI's linear kinematic sequence article was surfaced by search (https://www.mytpi.com/articles/biomechanics/the-linear-kinematic-sequence). Not read, **[secondary]**.

### 2.2 Numeric profile (male tour-level driver)

| Quantity | Value | Source |
|---|---|---|
| Club head speed at impact | 109 ± 3 mph (48.7 m/s) for the Cheetham pros. Tour average 113 mph (50.5 m/s) | Cheetham 2008; TrackMan 3.1 |
| Peak pelvis rotational speed | 477 ± 53 °/s | Cheetham Table 1 |
| Peak thorax rotational speed | 727 ± 61 °/s | Cheetham Table 1 |
| Peak lead-arm rotational speed | 980 ± 68 °/s | Cheetham Table 1 |
| Peak club rotational speed | 2254 ± 68 °/s | Cheetham Table 1 |
| Alternative averages (hip / shoulder / arm / club) | 498 / 723 / 1165 / 2090 °/s | Hume 2005, citing Geisler 2001 |
| Speed gains | pelvis→thorax 250 ± 42, thorax→arm 253 ± 59, arm→club 1274 ± 65 °/s | Cheetham Table 1 |
| Avg rotational accel (thousand °/s²) | pelvis 2.1, thorax 3.3, arm 5.1, club 8.8 | Cheetham Table 1 |
| Avg rotational decel (thousand °/s²) | pelvis 2.0, thorax 2.6, arm 7.0 | Cheetham Table 1 |
| Peak timing before impact | pelvis 87 ± 19 ms, thorax 68 ± 14 ms, arm 65 ± 8 ms, club at impact (0 ms) | Cheetham Table 1 |
| Order of peaks | pelvis → thorax → arm → club, each peak higher and later than the last | Cheetham (discussion) |
| Pelvis deceleration before impact | present in **every** pro swing | Cheetham (discussion) |
| Backswing duration (drive, elite) | ~0.82 s | Cochran & Stobbs via Hume |
| Downswing duration (drive, elite) | ~0.23 s | Cochran & Stobbs via Hume |
| Tempo ratio | ~3.5:1 from the two numbers above. Other reports ~3:1 (range 2.5-3.5:1) | Hume; tempo reports are **[secondary]** (web summaries) |
| Shoulder turn at top | 78-102° (varies by level) | Hume |
| Hip turn at top | 47-55° | Hume |
| X-factor (shoulder minus hip) at top | PGA 32° (McTeigue), long hitters 38° vs short hitters 24° (McLean) | Hume Table I |
| X-factor stretch (early downswing) | Pros ~19% greater than amateurs; hips begin to unwind while shoulders still turn back | Cheetham 2000 via Hume |
| Setup posture | Knee flex 20-25°, trunk flexed ~45° at hips, lateral shoulder tilt ~16°, 50-60% weight on back foot | Hume |
| Impact posture | Spine angle ~34°, secondary tilt ~28°, shoulders ~27° and hips ~43° rotated to the left of the address line | Hume |
| Weight on lead leg at top | ~40% of bodyweight | Hume |
| GRF (driver) | Peak vertical 1.6-2.0 BW, anterior-posterior 0.4-0.6 BW, medial-lateral 0.2-0.3 BW. Lead-leg vertical compression up to ~80% BW at impact; back foot loaded in the backswing, transferred to front foot in the downswing | Hume (Barrentine, Gatt) |
| Wrist release | Uncock when the lead arm is ~30° below horizontal. Wrist torque adds ~9% club speed in a 44 m/s simulation. Wrist cock was the strongest of 15 predictors, 60.3% of club-speed variance (Robinson, between golfers) | Hume (Sprigings & Neal 2000) |
| Linear speed contribution | wrist 70%, shoulders 20%, spine 5%, hips 5% | Hume (Milburn / Neal) |
| Consistency | Pros' timing SDs are less than half the amateurs' (e.g. arm peak ±8 vs ±23 ms) | Cheetham |

Caution: the numbers come from different studies, different sensor setups and different "angular velocity" definitions (about the segment's vertical axis for pelvis and thorax, about the swing-plane normal for arm and club). X-factor definitions vary. Burden et al. report 70 ± 20° with a different method, so use X-factor as a *relative* signal (stretch, not absolute). A search summary quoted "thorax 763" and "arm 980", but the primary table says thorax **727** and arm **980**. 763 is the amateur arm value. Use the table above.

### 2.3 How to turn this into a style reward
Compute per-swing features from the simulated body, then score them:

1. **Sequence order:** peak times of pelvis < thorax < arm < club in the downswing. Reward = 1 if ordered. A partial score is fine for pairs.
2. **Peak speeds:** pelvis/thorax/arm/club speed ratios. Because the sim is scaled and the target is club speed, use the **ratios** from Cheetham (thorax/pelvis 1.52, arm/thorax 1.35, club/arm 2.30) rather than raw values.
3. **Timing lead:** peak offsets before the club peak of ~87 / 68 / 65 ms (tolerance one SD, so ±19 / 14 / 8 ms). Note the arm lead (65 ms) is close to the thorax lead (68 ms), so keep this term soft.
4. **Decel before impact:** pelvis and thorax speed at impact < their peak (reward the drop).
5. **X-factor stretch:** shoulder-minus-hip angle should rise during the first ~30% of the downswing to above its top-of-backswing value.
6. **Tempo:** backswing/downswing ratio in [2.5, 3.5], penalize outside. Use the sim's own absolute time carefully: real downswing is ~0.23 s, so a policy with a 1 s downswing is not a golf swing.
7. **Weight transfer:** back-foot share of vertical GRF > 50% at top, front-foot share > 70% at impact. These are inferred targets from Hume's qualitative description and the 80% lead-leg figure. The 70% front-foot number is **my engineering choice, not a published value**.
8. **Contact gate:** pay all style rewards only if the club makes true contact (the project's existing finding), and add the ball-speed term separately.

Mark each constant with its source in code. Items 3, 5 and 7 are the least certain.

---------------------------------------------------------------------
## 3. Ball and club data

### 3.1 Launch-monitor reference numbers
- **TrackMan PGA Tour averages** (PDF listed at https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf; blog https://www.trackman.com/blog/introducing-updated-tour-averages, fetched). Blog text: "Male data is captured across 40+ different events and 200+ different players... Averages are based on data from competition as well as on the range." Search summary of the PDF reports for driver: club speed 113 mph, ball speed 167 mph, smash factor 1.48, launch 10.9°, spin 2,686 rpm, carry 251 m **[secondary: I could not parse the PDF]**. A 2025 secondary report cites 115 mph, 171 mph, 1.49, 10.4°, 2,545 rpm. Verify against the PDF before using as hard constants. TrackMan publishes averages as a download, not raw shots. **Check TrackMan's terms before redistributing the table in a product.** Quoting a few average numbers with attribution in documentation is low risk.
- **Open shot-level data:** CaddieSet (MIT, 1,757 shots, 8 golfers, ball speed, carry, spin, direction) is useful to validate the ball-flight model in non-tour regimes. PGA Tour ShotLink is not open.

### 3.2 Equipment rules (USGA / R&A)
These are public rules. Values from search summaries of the official pages. Verify against the PDF at https://www.randa.org/roe/the-rules-of-equipment/part-2-conformance-of-clubs before hard-coding **[secondary]**:
- Driver head volume: 460 cc (+10 cc test tolerance). MOI about the vertical axis: 5,900 g·cm² (+100 tolerance).
- Club length: up to 48 in (except putters).
- Spring-like effect (trampoline) via Characteristic Time: 239 µs (+18 µs test tolerance, 257 µs practical limit). CT is the rule in force, not a COR number. Older COR ≈ 0.83 is the equivalent figure that engineers use. **[unverified here]**
- Ball: max weight 1.620 oz (45.93 g), min diameter 1.680 in (42.67 mm), initial velocity max 250 ft/s (76.2 m/s) with 2% test tolerance, overall distance max 317 yd (+3 yd tolerance), spherically symmetric.
- Simulation consequence: ball speed limit 76.2 m/s, and at smash ≈ 1.5 that implies a club speed ≈ 51 m/s, which matches tour averages. The earlier research's "145 mph for 350 yd" is outside what tours do.

### 3.3 Ball aerodynamics (for the flight model)
- Smits & Smith (1994), "A new aerodynamic model of a golf ball in flight", in Science and Golf II. Reynolds-dependent drag and spin decay. Drag falls sharply near Re ≈ 200,000 (drag crisis).
- Bearman & Harvey (1976), "Golf ball aerodynamics", Aeronautical Quarterly 27:112-122. Lift and drag against Reynolds number and spin.
- A third-party implementation (https://github.com/avrybrdly93/golfsim, license not checked) uses CL = 1.99S - 3.25S² and CD = 0.29 + 0.2S above Re = 170,000, with S = rω/V. **[secondary, unverified]** Cross-check against the papers before relying on them, and check the repo license before copying code. Re-implementing the published equations ourselves is safe.
- Calibration test: reproduce TrackMan tour driver (167 mph ball, 10.9° launch, 2,686 rpm → ≈251 m carry). The prior project note says the model is already within 1% on one point. Add more points (e.g. 7-iron) so it is not fit to a single shot.

---------------------------------------------------------------------
## 4. Legitimately synthesizing more training variety

**What the evidence supports**
- Retargeting quality matters more than heavy reward tuning for humanoid tracking (paper "Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking", https://jaraujo98.github.io/retargeting_matters/ **[secondary]**).
- **GMR** (https://github.com/YanjieZe/GMR): MIT License, text fetched ("Permission is hereby granted ... to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software"). Fine for commercial use. **ProtoMotions**: Apache-2.0 **[secondary]**. **PHC** shows license "Other" **[secondary]**, so read its LICENSE before use (it may inherit SMPL/AMASS terms).
- Pose models and body models (SMPL, SMPL-X) carry **non-commercial** terms. Avoid them in the product pipeline, or buy the commercial license. Use a body model we own (the MuJoCo humanoid) with CMU's skeleton directly.

**Safe augmentation menu (all operate on data we are allowed to use)**
1. **Time warping and tempo scaling:** speed up CMU's slow swings to the 0.23 s downswing and 3:1 ratio from 2.2. Non-uniform warps keep the phase order. Keep the kinematic-sequence timing from 2.2.
2. **Spatial variation:** scale limb lengths and height (retarget to different body proportions), add small amplitude jitter to the top-of-backswing and plane angles, mirror for left-handed golfers (flip signs and swap sides).
3. **Style interpolation:** blend Mason clips with CMU clips in joint space (after retargeting), and blend between phase-aligned swings (dynamic time warping on event frames: address, top, impact, finish).
4. **Physics-informed randomization (domain randomization) in MuJoCo:** friction, club mass, shaft stiffness, ball mass and radius within USGA limits, actuator gains and strength, timestep, sensor noise and delay, tee height, ball position relative to feet, uneven lie and slope.
5. **Kinematic-sequence prior as curriculum:** start from a scripted swing following the 2.2 profile, then relax the style weight so RL can exceed it.
6. **Dataset hygiene:** keep a provenance table (source, license, date, who approved) for every clip in the training set and exclude RED rows automatically in the loader. Hold out Mason's best swings for evaluation, not training.
7. **Data we collect ourselves:** with a signed release covering commercial ML training, record golfers on phone (two views), and run a pose lifter whose license permits commercial use. Mason's clips already follow this idea.

**Don'ts:** don't scrape YouTube, Instagram or pro video. Augmenting a non-commercial dataset does not clean its license, because derived data and models inherit the restriction (the AMASS text above says so explicitly).

---------------------------------------------------------------------
## 5. Open items for a human
1. Counsel review of CMU's two statements (redistribute vs resell) and the acknowledgment text.
2. Written commercial terms from KIT H²T and from the GolfPose authors.
3. Verify TrackMan PDF values, USGA CT/MOI/COR from the official PDF, and the golfsim coefficients against Smits & Smith / Bearman & Harvey.
4. Decide whether to buy an AMASS commercial license (contact per the licensor terms (see the license URL above)).
5. Read the Cochran & Stobbs, McTeigue et al., and Cheetham et al. 2000 originals before leaning on tempo and X-factor-stretch constants.

## Sources (all fetched or surfaced 2026-10-16)
- CMU: http://mocap.cs.cmu.edu/ , http://mocap.cs.cmu.edu/faqs.php , http://mocap.cs.cmu.edu/info.php
- AMASS license: https://amass.is.tue.mpg.de/license.html
- BEDLAM license: https://bedlam.is.tue.mpg.de/license.html
- Motion-X: https://github.com/IDEA-Research/Motion-X/blob/main/LICENSE , https://motion-x-dataset.github.io/static/license/Motion-X%20License.pdf
- HuMMan: http://caizhongang.com/projects/HuMMan/license.txt
- Human3.6M: https://vision.imar.ro/human3.6m/eula.php
- KIT: https://motion-database.humanoids.kit.edu/faq/
- GolfDB: https://github.com/wmcnally/golfdb , https://arxiv.org/html/1903.06528v1
- CaddieSet: https://github.com/damilab/CaddieSet (LICENSE, README fetched)
- GolfPose: https://github.com/MingHanLee/GolfPose
- GMR: https://github.com/YanjieZe/GMR (LICENSE fetched)
- Cheetham et al. 2008: http://www.waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf
- Hume, Keogh, Reid 2005: https://pubmed.ncbi.nlm.nih.gov/15896091/ (full text read at waddengolfacademy.com copy)
- TrackMan: https://www.trackman.com/blog/introducing-updated-tour-averages
- USGA/R&A rules: https://www.randa.org/roe/the-rules-of-equipment/part-2-conformance-of-clubs , https://www.usga.org/content/dam/usga/pdf/Equipment/TPX3007-initial-velocity-test-procedure.pdf
