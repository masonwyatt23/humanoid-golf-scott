# Research: motion-capture / pose dataset licenses and commercial-use status (2026-10-17 ET)
Engineering diligence, **not legal advice**. Machine-readable twin: `data/references/mocap_dataset_licenses.json` (schema test: `tests/test_mocap_dataset_licenses.py`).
`primary_fetched` = I read the license/terms page or file today; `secondary_search_snippet` = only a search-engine summary of it; `unverified` = not confirmed. Numbers in a "size" field that say unverified must not be relied on. No data was downloaded; no player video touched.

## Bottom line
1. **Only CMU (and 100STYLE, locomotion only) are clean "yes".** CMU: "free for all uses ... may include this data in commercially-sold products, but you may not resell this data directly, even in converted form", with a required acknowledgment. Everything else golf-relevant is CC0/MIT-on-data (counsel) or non-commercial.
2. **The whole MPI/SMPL family is a hard no for commercial training**: AMASS, SMPL(-X) model, BEDLAM, 3DPW all carry text such as "This license also prohibits the use of the Dataset to train methods/algorithms/neural networks/etc. for commercial use of any kind". That transitively blocks HumanML3D and Motion-X (AMASS-derived), and makes any **video -> WHAM/GVHMR -> SMPL** step a counsel item for a commercial pipeline (docs/WHAM_GVHMR.md). MediaPipe-based extraction (what the project already uses) avoids the SMPL dependency.
3. **Retargeted humanoid sets do not launder licenses.** The Unitree LAFAN1 retarget repo has a BSD-3 LICENSE file, but its motion is LAFAN1 (CC BY-NC-ND 4.0): treat as non-commercial. 
4. **New: BONES-SEED (Bones Studio, 142k motions, SOMA + Unitree G1 CSV, NVIDIA Kimodo labels) is explicitly designed for humanoid policy training and allows commercial use for startups under $1M revenue** (policy/tracking models allowed; no public mirrors; attribution; audit; terminates on change of control). Probably the best *general* motion prior for the humanoid, but not golf-specific and eligibility/terms need counsel.
5. **OpenCap's hosted service forbids commercial entities "for any purpose, including research"** and may reuse uploaded videos: do not route Mason's swings through it for the commercial project.
6. **Mixamo**: royalty-free in products, but community posts quoting Adobe say ML training is not allowed (primary Adobe PDF not read): counsel.
7. **Golf:** no open dataset has left-handed or 120+ mph swings. MultiSenseGolf (CC0, 1,557 swings, 24 participants) is the best open golf source; GolfPose (3D golfer+club GT) is gated with no terms; Mason's own 240 fps footage remains the only route to the target swing.

## Counsel-needed list (priority order)
1. MultiSenseGolf: CC0 label vs identifiable participants/consent for commercial model training (already used in the unified refset at weight 0.2).
2. SMPL dependency in any commercial video pipeline (WHAM/GVHMR).
3. CaddieSet: MIT license applied to data; consent unknown (currently tagged `unknown`).
4. GolfPose: no terms; ask authors for written permission.
5. BONES-SEED: eligibility, attribution wording, change-of-control termination, no-public-mirror (never commit it to GitHub).
6. AIST++: CC BY annotations derived from research-only AIST videos.
7. Mixamo ML clause; KIT (no license found); OpenCap datasets (no terms found); Kimodo per-checkpoint licenses; Unitree LAFAN1 retarget.
8. CMU: home page ("may not resell directly") vs FAQ ("copied, modified, or redistributed without permission") differ; we follow the stricter text and keep the acknowledgment.

## Summary table
| Dataset | Commercial OK (⚠ counsel) | Golf relevance | Size | Format | Access | Proposed tag | Verified |
|---|---|---|---|---|---|---|---|
| CMU Graphics Lab Motion Capture Database | yes | high | 2605 trials, 6 categories, 23 subcategories (home page) | ASF/AMC, C3D, BVH (3rd-party conversions), AVI/MPG | Free direct download, no registration | `cmu_permissive` | primary_fetched |
| AMASS (Archive of Mocap as Surface Shapes) | no | medium | unverified (commonly cited ~40 h; not on the fetched license page) | SMPL-H npz (requires SMPL+H/DMPL body models, themselves non-commercial) | Registration + click-through license at amass.is.tue.mpg.de | `noncommercial` | primary_fetched |
| SMPL body model (and SMPL-X/SMPL+H family) | no ⚠ | medium | model files (few MB) | pkl/npz | Registration + click-through | `noncommercial` | primary_fetched |
| MultiSenseGolf | needs_counsel ⚠ | very high | 1,557 swings, 24 participants (record abstract); full-body IMU joint kinematics; project converted 28 swings from P19/P20/P22 (P10, P14 available, 1-2 GB each) | per-swing records (CSV/npz-like; see docs/research_open_data_v2.md) | Open download, no login | `cc0` | secondary_search_snippet |
| CaddieSet | needs_counsel ⚠ | medium | 1,757 shots, 8 golfers, 508 KB CSV (docs/research_open_data_v3.md) | CSV | GitHub | `unknown` | primary_fetched |
| GolfDB | no | high for event timing; videos not redistributable | 1,400 videos (per GolfPose paper text); preprocessed 160x160 clips available | MP4/pkl | GitHub + Google Drive links | `noncommercial` | primary_fetched |
| GolfPose / GolfSwing dataset | needs_counsel ⚠ | very high | size unverified; files data_2d_golf_gt.npz, data_3d_golf_gt.npz, images, coco | npz (VideoPose3D-style), COCO json, images | Email authorization -> gofile link | `unknown` | secondary_search_snippet |
| SportsPose | no | low-medium | 176,000 3D poses, 24 subjects, 5 sports, 7 views | npz/pickle + code (PyTorch dataset) | Email request from academic address (DTU) | `noncommercial` | primary_fetched |
| Human3.6M | no | none | 3.6M poses (from dataset name; not on fetched page - unverified) | C3D/CDF, video | Academic request at vision.imar.ro | `noncommercial` | primary_fetched |
| AIST++ (annotations on AIST Dance DB) | needs_counsel ⚠ | none | 1,408 motion sequences; 10.1M images with 3D keypoints, 30 subjects, 9 views | pkl (keypoints2d/3d, SMPL motions), mp4 (separate AIST DB) | Open download of annotations; videos via AIST application form | `noncommercial` | primary_fetched |
| 100STYLE | yes | low | >4 million frames, 100 styles, 60 fps | BVH | Zenodo + Google Drive, open | `cc_by` | primary_fetched |
| Ubisoft La Forge Animation Dataset (LAFAN1) | no | none | 77 sequences, 496,672 frames @30 fps (~4.6 h), 5 subjects | BVH (git-lfs zip 137 MB) | GitHub | `noncommercial` | primary_fetched |
| LAFAN1 Retargeting Dataset (Unitree G1/H1/H1_2) | needs_counsel ⚠ | none | ~37 trajectories x 3 robots; 30 fps; ~70 MB repo storage (HF usedStorage) | CSV (root xyz+quat, joint angles) | Hugging Face, open | `noncommercial` | primary_fetched |
| Mixamo animations (Adobe) | needs_counsel ⚠ | none for golf | ~2,500 animations (unverified) | FBX | Adobe ID, per-file download | `unknown` | secondary_search_snippet |
| KIT Whole-Body Human Motion Database | needs_counsel ⚠ | low | size unverified | C3D/MMM XML | Free account (unverified) | `unknown` | primary_fetched |
| HumanML3D | no | low | 14,616 motions / 44,970 texts (paper figure, unverified) | npy (263-d features) | Rebuild from AMASS with scripts | `noncommercial` | primary_fetched |
| Motion-X | no | low | ~81k motions (paper figure, unverified) | SMPL-X npy + text | Form/Google Drive | `noncommercial` | primary_fetched |
| BEDLAM / BEDLAM2 | no | low | size unverified (large) | PNG/MP4 + npz | Registration + click-through | `noncommercial` | primary_fetched |
| 3DPW | no | low | ~60 videos (unverified) | pkl + images | Open after license accept | `noncommercial` | primary_fetched |
| CMU Panoptic Studio dataset | no | low | Monocular Total Capture subset 270 GB; full set far larger | json + video/images | Open download scripts (panoptic-toolbox) | `noncommercial` | secondary_search_snippet |
| OpenCap service (Stanford/Utah) | no ⚠ | high as a self-capture tool, but see terms | n/a | OpenSim .mot/.osim, TRC | Web app account | `noncommercial` | primary_fetched |
| OpenCap validation / field datasets (SimTK) | needs_counsel ⚠ | low | unverified | OpenSim files, TRC/MOT | SimTK account | `unknown` | unverified |
| BONES-SEED (Bones Studio; SOMA + Unitree G1 retargets, NVIDIA labels) | needs_counsel ⚠ | low-medium | 142,220 motions (71,132 original + mirrors), ~288 h @120 fps | BVH (SOMA), npz, G1 CSV | Hugging Face gated, click-through | `unknown` | primary_fetched |
| NVIDIA Kimodo (kinematic motion diffusion; SOMA/G1 variants) | needs_counsel ⚠ | low | n/a | PyTorch checkpoints | GitHub/HF | `unknown` | secondary_search_snippet |
| Edinburgh DataShare doi:10.7488/ds/3823 (golf wrist angular velocity, club data, EMG) | needs_counsel ⚠ | high but gated | small spreadsheets | xls | Request-a-copy (gated) | `cc_by` | secondary_search_snippet |
| Harvard Dataverse 'Golf Swing Performance Dataset' (doi:10.7910/DVN/SFYVDN) | no | low | 2 videos (17 MB, 24 MB) + table | table + mov | Open | `unknown` | secondary_search_snippet |

## Recommended provenance tag mapping (proposal; `data/provenance.py` NOT edited)
Existing classes (`synthetic, self_owned, cmu_permissive, cc0, noncommercial, unknown`) cover most cases. Proposed additions, kept default-deny:
| New class | commercial_ok | Use for |
|---|---|---|
| `cc_by` | True, `acknowledgment_required=True` (credit string in `acknowledgment_text`) | 100STYLE ("The 100STYLE Dataset - Ian Mason"), Edinburgh DataShare if obtained |
| `commercial_license_required` | False | AMASS, SMPL, Human3.6M, BONES-SEED (until entity eligibility confirmed) |
| `needs_counsel` | False | GolfPose, Mixamo, KIT, OpenCap datasets, AIST++, CaddieSet |
Also propose provenance keys `counsel_required` (bool) and `license_url` (str). Suggested `infer_kind` keywords: `lafan`->noncommercial, `bedlam`/`3dpw`/`panoptic`/`human36m`/`humanml3d`/`motion-x`->noncommercial, `bones`/`seed`->commercial_license_required, `100style`->cc_by, `mixamo`/`kit`/`aist`->needs_counsel. Current `infer_kind` already routes golfdb/amass/sportspose/rep3d/golfpose/caddieset names to noncommercial/unknown behaviour; note `golfpose` and `caddieset` are really counsel-pending rather than confirmed-NC.

## Per-dataset detail
### CMU Graphics Lab Motion Capture Database  (`cmu_mocap`)
- **License:** Custom statement ('free for all uses') — <http://mocap.cs.cmu.edu/>
- **Evidence (quote/summary):** "This dataset of motions is free for all uses. ... You may include this data in commercially-sold products, but you may not resell this data directly, even in converted form. ... add this text to your acknowledgments: The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217."
- **Commercial OK:** **yes**. Commercial products OK; no standalone resale of data even converted. NOTE: the FAQ page (http://mocap.cs.cmu.edu/faqs.php) separately says 'may be copied, modified, or redistributed without permission' - the two statements are not identical; follow the stricter home-page text.
- **Attribution:** Acknowledgment text requested in publications (we require it in the project).  **ML training:** No ML restriction stated.
- **Golf relevance:** high (golf swings, subject 64; project uses 10). **Domain:** optical mocap, general (2605 trials, 6 categories; subject 64 = golf).
- **Verification:** primary_fetched

### AMASS (Archive of Mocap as Surface Shapes)  (`amass`)
- **License:** MPI Dataset Copyright License for non-commercial scientific research — <https://amass.is.tue.mpg.de/license.html>
- **Evidence (quote/summary):** "This license also prohibits the use of the Dataset to train methods/algorithms/neural networks/etc. for commercial use of any kind. ... For commercial uses of the Dataset, please send email to [contact email listed on the dataset page]"
- **Commercial OK:** **no**. Non-commercial research/education/artistic only; explicit ban on training models for commercial use; no sharing with third parties; no redistribution. Applies even to the CMU subset as distributed by AMASS (the AMASS wrapper terms govern what you get from AMASS; use CMU's own original files for CMU-permissive use).
- **Attribution:** Cite Mahmood et al. ICCV 2019 in publications.  **ML training:** Explicit prohibition: no training for commercial use.
- **Golf relevance:** medium (contains some golf/sports; includes CMU re-fit). **Domain:** SMPL-fitted aggregation of ~15+ mocap datasets (general).
- **Verification:** primary_fetched

### SMPL body model (and SMPL-X/SMPL+H family)  (`smpl_model`)
- **License:** SMPL-Model License (academic research) — <https://smpl.is.tue.mpg.de/modellicense.html>
- **Evidence (quote/summary):** "This software/data and the associated license is for academic research purposes. The software/data is also available for commercial licensing through Meshcapade.com. ... This license also prohibits the use of the Software to train methods/algorithms/neural networks/etc. for commercial use of any kind."
- **Commercial OK:** **no** (counsel needed: Whether outputs of a pipeline that merely passes through SMPL (e.g. our own self-filmed video -> WHAM -> joint angles -> humanoid) are 'artefacts for commercial purposes' under this license is a legal question. Prefer a non-SMPL pose path (MediaPipe, which the project already uses) for commercial data.). Commercial use requires a license (Meshcapade; [contact email listed on the dataset page]). Using SMPL as an intermediate in a commercial pipeline (e.g. WHAM/GVHMR video->SMPL->humanoid) is likely covered by the 'commercial use / production of artefacts for commercial purposes' language. SMPL-X page not fetched directly (search snippet only: also commercially licensed via Meshcapade).
- **Attribution:** Cite Loper et al. SIGGRAPH Asia 2015.  **ML training:** Explicit prohibition on training for commercial use (the model itself).
- **Golf relevance:** medium (needed to read most SMPL-format mocap; WHAM/GVHMR pose pipeline depends on it). **Domain:** parametric body model used by AMASS, AIST++, 3DPW, BEDLAM, HumanML3D, WHAM/GVHMR.
- **Verification:** primary_fetched

### MultiSenseGolf  (`multisensegolf`)
- **License:** CC0 1.0 (Dataverse default waiver; per record) — <https://doi.org/10.7910/dvn/lccllw>
- **Evidence (quote/summary):** "Dataverse datasets are CC0 by default unless the depositor opts out (dataverse.org community norms). Record: 'MultiSenseGolf ... 1,557 swing records from 24 participants'."
- **Commercial OK:** **needs_counsel** (counsel needed: CC0 + identifiable participants + consent scope. Existing project tag 'multisensegolf_cc0' sets commercial_ok=True; recommend keeping it but gate commercial release on counsel sign-off (already a pending item).). CC0 waiver on the record permits any use, but data are about identifiable people (video, gaze, body measurements); consent scope and GDPR/Korea-privacy implications for commercial model training are not something the CC0 label settles. Project uses joint-position data only (no video).
- **Attribution:** None required (CC0); citation courtesy.  **ML training:** No restriction (CC0).
- **Golf relevance:** very high (golf, 24 participants, beginner-to-pro). **Domain:** golf: IMU full-body kinematics, foot pressure, FPV/RGB-D video, gaze, launch monitor.
- **Verification:** secondary_search_snippet

### CaddieSet  (`caddieset`)
- **License:** MIT (repo LICENSE) — <https://raw.githubusercontent.com/damilab/CaddieSet/main/LICENSE>
- **Evidence (quote/summary):** "MIT License Copyright (c) 2024 damilab"
- **Commercial OK:** **needs_counsel** (counsel needed: MIT-on-data and subject consent for derived summary stats. Currently tagged unknown (commercial_ok False) - keep until counsel clears.). MIT is a software license applied to a data repo; no separate data/consent statement in README (per docs/research_open_data_v3.md). Features are vision-estimated from video of 8 golfers.
- **Attribution:** MIT requires copyright + permission notice in copies.  **ML training:** No restriction stated.
- **Golf relevance:** medium (summary stats; no trajectories). **Domain:** golf: shot/ball data + 2D-vision joint features at 8 swing events.
- **Verification:** primary_fetched

### GolfDB  (`golfdb`)
- **License:** Repo code/labels: CC BY-NC 4.0; videos are YouTube-sourced — <https://github.com/wmcnally/golfdb>
- **Evidence (quote/summary):** "The code in this repository is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. ... If you wish to use a different input configuration you must download the YouTube videos (URLs provided in dataset)"
- **Commercial OK:** **no**. NC license on labels; underlying videos belong to YouTube uploaders/players (likeness + copyright). Project policy: no GolfDB video downloaded.
- **Attribution:** CC BY: credit + license link + indicate changes.  **ML training:** NC bars commercial training; video rights separate.
- **Golf relevance:** high for event timing; videos not redistributable. **Domain:** golf: 1,400 YouTube swing videos with event labels (video, no 3D).
- **Verification:** primary_fetched

### GolfPose / GolfSwing dataset  (`golfpose`)
- **License:** No dataset license stated (code repo has its own LICENSE; dataset behind email authorization) — <https://github.com/MingHanLee/GolfPose>
- **Evidence (quote/summary):** "Please email [contact email listed on the dataset page] to authorize the dataset download."
- **Commercial OK:** **needs_counsel** (counsel needed: No license. Ask authors in writing for commercial-training permission (and subject consent).). No terms published; assume all rights reserved until the authors state terms in writing. Do not use for commercial work without written permission.
- **Attribution:** Unknown; cite ICPR 2024 paper.  **ML training:** Unknown.
- **Golf relevance:** very high (3D golfer+club GT) but access-gated. **Domain:** golf: Qualisys-style marker mocap 3D golfer + 5 club keypoints, synchronized RGB (ICPR 2024).
- **Verification:** secondary_search_snippet

### SportsPose  (`sportspose`)
- **License:** Custom academic-only license — <https://christianingwersen.github.io/SportsPose/download.html>
- **Evidence (quote/summary):** "Licenses free of charge are limited to academic use only. ... you may not rent, lease, lend, sub-license or transfer the dataset ... seek prior written permission from the authors and pay any additional fees or royalties, as may be required, for any uses not permitted"
- **Commercial OK:** **no**. Academic-address request required; no commercial use without written permission.
- **Attribution:** Must cite the papers (not just URL).  **ML training:** Not allowed outside academic use.
- **Golf relevance:** low-medium (no golf listed in abstract; unverified which 5 sports). **Domain:** sports 3D poses (5 sports, 24 subjects, 7 views); markerless GT.
- **Verification:** primary_fetched

### Human3.6M  (`human36m`)
- **License:** Custom academic-only EULA — <http://vision.imar.ro/human3.6m/eula.php>
- **Evidence (quote/summary):** "GRANT OF LICENSE FREE OF CHARGE FOR ACADEMIC USE ONLY ... Provided you send the request from an academic address ... FOR COMMERCIAL LICENSING, please contact us"
- **Commercial OK:** **no**. Academic only; commercial licensing by contacting authors (email not captured in fetch).
- **Attribution:** Cite the PAMI 2014 and ICCV 2011 papers (citing URL is non-compliant).  **ML training:** Not allowed commercially.
- **Golf relevance:** none. **Domain:** indoor mocap + video, 11 subjects, daily activities.
- **Verification:** primary_fetched

### AIST++ (annotations on AIST Dance DB)  (`aistpp`)
- **License:** Annotations: CC BY 4.0 (Google). Source videos: AIST Dance DB terms (research only) — <https://google.github.io/aistplusplus_dataset/factsfigures.html>
- **Evidence (quote/summary):** "The annotations are licensed by Google LLC under CC BY 4.0 license. // AIST DB: Use for commercial purposes is not permitted without prior written consent from AIST."
- **Commercial OK:** **needs_counsel** (counsel needed: CC BY on derived annotations vs non-commercial source videos; SMPL dependency.). Annotations alone are CC BY 4.0 (commercial OK with attribution), but they were derived from AIST videos whose terms forbid commercial use without consent, and use SMPL fitting. Treat as non-commercial until counsel decides.
- **Attribution:** CC BY 4.0 credit Google LLC; also must name 'AIST Dance Video Database'.  **ML training:** AIST: academic research only.
- **Golf relevance:** none (dance). **Domain:** dance, multi-view 3D keypoints + SMPL motion.
- **Verification:** primary_fetched

### 100STYLE  (`style100`)
- **License:** CC BY 4.0 — <https://www.ianxmason.com/100style/>
- **Evidence (quote/summary):** "This work is licensed under a Creative Commons Attribution 4.0 International License. For creative or commercial work please credit in an appropriate way. E.g. 'The 100STYLE Dataset - Ian Mason'."
- **Commercial OK:** **yes**. CC BY 4.0 + explicit commercial-credit request. Single actor (identifiable), IMU data. Zenodo record page not independently fetched.
- **Attribution:** Credit 'The 100STYLE Dataset - Ian Mason' (CC BY 4.0).  **ML training:** No ML restriction stated.
- **Golf relevance:** low (no golf; useful for locomotion/balance priors). **Domain:** locomotion styles, 1 actor, Xsens IMU mocap.
- **Verification:** primary_fetched

### Ubisoft La Forge Animation Dataset (LAFAN1)  (`lafan1`)
- **License:** CC BY-NC-ND 4.0 — <https://raw.githubusercontent.com/ubisoft/ubisoft-laforge-animation-dataset/master/license.txt>
- **Evidence (quote/summary):** "This dataset can be used under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License"
- **Commercial OK:** **no**. Non-commercial AND no derivatives. ND is problematic even for research derivatives such as retargeting; any robot retarget is a derivative.
- **Attribution:** CC BY: credit Ubisoft; cite Harvey et al. 2020.  **ML training:** NC bars commercial training.
- **Golf relevance:** none (a 'fight and sports' theme only). **Domain:** studio mocap, 5 subjects, locomotion/dance/fight; humanoid-RL staple.
- **Verification:** primary_fetched

### LAFAN1 Retargeting Dataset (Unitree G1/H1/H1_2)  (`unitree_lafan1_retarget`)
- **License:** Repo LICENSE = BSD-3-Clause (Unitree); underlying motion = LAFAN1 CC BY-NC-ND — <https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset/raw/main/LICENSE>
- **Evidence (quote/summary):** "BSD 3-Clause License Copyright (c) 2016-2024 HangZhou YuShu TECHNOLOGY CO.,LTD. (HF API tags: only task_categories:robotics; no license tag)"
- **Commercial OK:** **needs_counsel** (counsel needed: License laundering risk: BSD-3 on a derivative of CC BY-NC-ND data.). BSD-3 file covers Unitree's contribution/robot description; it cannot relicense Ubisoft's CC BY-NC-ND motion. Safe reading: non-commercial only.
- **Attribution:** BSD-3 notice retention; LAFAN1 credit.  **ML training:** Treat as NC (inherits LAFAN1).
- **Golf relevance:** none. **Domain:** LAFAN1 retargeted to Unitree humanoids (30 fps CSV).
- **Verification:** primary_fetched

### Mixamo animations (Adobe)  (`mixamo`)
- **License:** Adobe Mixamo terms (royalty-free use; no redistribution of raw assets; ML-training restricted) — <https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html>
- **Evidence (quote/summary):** "You can use both characters and animations royalty free for personal, commercial, and non-profit projects. [Adobe community FAQ/mod, secondary:] The only research application Mixamo content can't be used in is training machine-learning models."
- **Commercial OK:** **needs_counsel** (counsel needed: ML-training ban reported by community posts quoting Adobe; verify the primary Additional Terms PDF.). Embedding in products is allowed, but sources report a ban on using Mixamo content to train ML models (Adobe Additional Terms PDF not read by me). Never redistribute raw files.
- **Attribution:** None required.  **ML training:** Reported prohibition on ML training (secondary source; verify in Adobe's Mixamo Additional Terms).
- **Golf relevance:** none for golf. **Domain:** artist-made animation library, FBX.
- **Verification:** secondary_search_snippet

### KIT Whole-Body Human Motion Database  (`kit_whole_body`)
- **License:** No license text found on site — <https://motion-database.humanoids.kit.edu/>
- **Evidence (quote/summary):** "Page gives citation requirement only (Mandery et al., IEEE T-RO 2016); no license page (/license/ returned 404)."
- **Commercial OK:** **needs_counsel** (counsel needed: No license found.). No license statement located; contact [contact email listed on the dataset page]. Individual sub-datasets may differ.
- **Attribution:** Cite Mandery 2016 or the specific dataset.  **ML training:** Unknown.
- **Golf relevance:** low. **Domain:** mocap, whole-body, object interaction, MMM format.
- **Verification:** primary_fetched

### HumanML3D  (`humanml3d`)
- **License:** Code MIT; data = derived from AMASS (cannot be distributed) — <https://raw.githubusercontent.com/EricGuo5513/HumanML3D/main/LICENSE>
- **Evidence (quote/summary):** "MIT License Copyright (c) 2022 Chuan Guo // README: Due to the distribution policy of AMASS dataset, we are not allowed to distribute the data directly."
- **Commercial OK:** **no**. Motions are AMASS-derived; AMASS bans commercial training. MIT covers only the scripts. Text annotations' own terms not stated (unverified).
- **Attribution:** MIT notice for code; cite Guo et al. CVPR 2022.  **ML training:** Inherits AMASS ban.
- **Golf relevance:** low. **Domain:** text-motion pairs derived from AMASS + HumanAct12.
- **Verification:** primary_fetched

### Motion-X  (`motionx`)
- **License:** IDEA Non-commercial Scientific Research license + per-source licenses — <https://raw.githubusercontent.com/IDEA-Research/Motion-X/main/LICENSE>
- **Evidence (quote/summary):** "Any other use, in particular any use for commercial, pornographic, military, or surveillance, purposes is prohibited. Text and visualization results are owned by IDEA. README table links AMASS/AIST++/GRAB/EgoBody/HuMMan licenses per source."
- **Commercial OK:** **no**. Non-commercial; incorporates AMASS, AIST++, etc., so strictest source wins.
- **Attribution:** Indicate original source of RGB videos when reproducing.  **ML training:** NC.
- **Golf relevance:** low. **Domain:** whole-body motion w/ text, video-derived + AMASS/AIST++/others.
- **Verification:** primary_fetched

### BEDLAM / BEDLAM2  (`bedlam`)
- **License:** MPI non-commercial scientific research license — <https://bedlam.is.tue.mpg.de/license.html>
- **Evidence (quote/summary):** "Data & Software Copyright License for non-commercial scientific research purposes (BEDLAM2 page: same non-commercial family, search snippet)"
- **Commercial OK:** **no**. Synthetic images/videos, SMPL-X params, meshes, textures all under NC terms; commercial: [contact email listed on the dataset page].
- **Attribution:** Cite BEDLAM (CVPR 2023).  **ML training:** NC.
- **Golf relevance:** low. **Domain:** synthetic video with SMPL-X GT.
- **Verification:** primary_fetched

### 3DPW  (`3dpw`)
- **License:** MPI non-commercial scientific research data license — <https://virtualhumans.mpi-inf.mpg.de/3DPW/license.html>
- **Evidence (quote/summary):** "Data License For non-commercial and scientific research purposes ... Any other use, in particular any use for commercial purposes, is prohibited ... including ... 3D models, movies, or video games."
- **Commercial OK:** **no**. NC; also bars 'production of other artefacts for commercial purposes'.
- **Attribution:** Cite ECCV'18 paper.  **ML training:** NC.
- **Golf relevance:** low. **Domain:** in-the-wild video + IMU-based SMPL GT.
- **Verification:** primary_fetched

### CMU Panoptic Studio dataset  (`cmu_panoptic`)
- **License:** Custom research-only terms — <http://domedb.perception.cs.cmu.edu/>
- **Evidence (quote/summary):** "shared only for research purposes, and this cannot be used for any commercial purposes. The dataset or its modified version cannot be redistributed without permission from dataset organizers."
- **Commercial OK:** **no**. Research only; no redistribution. (Quote read via search result of the dataset page; the page itself timed out for direct fetch.)
- **Attribution:** Cite Joo et al. TPAMI 2017 and sub-dataset papers.  **ML training:** NC.
- **Golf relevance:** low. **Domain:** multi-view dome video + 3D pose.
- **Verification:** secondary_search_snippet

### OpenCap service (Stanford/Utah)  (`opencap_service`)
- **License:** Service Terms: academic/non-profit non-commercial only — <https://www.opencap.ai/terms-conditions>
- **Evidence (quote/summary):** "Use of the Service by any commercial entity for any purpose, including research, is prohibited. ... Commercial entities wishing to use this Service should contact the authors of OpenCap ([contact email listed on the dataset page])."
- **Commercial OK:** **no** (counsel needed: Self-hosting opencap-core under Apache-2.0 vs service terms; HRNet/OpenPose licenses.). Do not process Mason's swings on the hosted service for a commercial project; all uploaded data is visible to and usable by the OpenCap team. Source code (opencap-core) is Apache-2.0 (search snippet) and can be self-hosted subject to third-party pose-model licenses (OpenPose/HRNet).
- **Attribution:** n/a  **ML training:** Data may be used by developers for algorithm development (privacy term 6a).
- **Golf relevance:** high as a self-capture tool, but see terms. **Domain:** smartphone video -> OpenSim kinematics; useful for Mason's own data capture.
- **Verification:** primary_fetched

### OpenCap validation / field datasets (SimTK)  (`opencap_datasets`)
- **License:** No dataset-specific license found (SimTK project page) — <https://simtk.org/projects/opencap>
- **Evidence (quote/summary):** "Search synthesis: SimTK page lists datasets but states no dataset-specific license; my direct fetch of the page timed out."
- **Commercial OK:** **needs_counsel** (counsel needed: Terms not located.). Unverified; do not use commercially without reading SimTK terms of the specific download.
- **Attribution:** Unknown; cite Uhlrich et al. PLoS Comp Bio 2023.  **ML training:** Unknown.
- **Golf relevance:** low. **Domain:** OpenCap + marker mocap validation data.
- **Verification:** unverified

### BONES-SEED (Bones Studio; SOMA + Unitree G1 retargets, NVIDIA labels)  (`bones_seed`)
- **License:** BONES-SEED Dataset License Agreement (academic OR startup with <$1M revenue) — <https://bones.studio/info/seed-license>
- **Evidence (quote/summary):** "If you do not qualify as (i) an Academic User or (ii) a Qualifying Startup, then you are NOT granted any rights ... Qualifying Startup: ... annual gross revenue of less than $1,000,000 USD."
- **Commercial OK:** **needs_counsel** (counsel needed: Eligibility (entity status, revenue), change-of-control clause, attribution, no-public-mirror rule (our repo is on GitHub: never commit data).). Commercial OK only for Qualifying Startups (internal R&D and commercialization), terminates 30 days after revenue >$1M or change of control; policies/tracking models explicitly allowed, generative motion models that substitute the dataset forbidden; no public mirrors; attribution 'Motion Data by Bones Studio' required; audit rights. Fits a robot control-policy use case if entity qualifies.
- **Attribution:** Required: 'Training data includes Motion Data by Bones Studio' (link bones.studio) in model cards/README + credit in products.  **ML training:** Policy/tracking models allowed; generative motion models restricted.
- **Golf relevance:** low-medium (sports category; golf presence unverified). **Domain:** studio mocap, 522 actors, humanoid-RL oriented; sport ~3,993 motions.
- **Verification:** primary_fetched

### NVIDIA Kimodo (kinematic motion diffusion; SOMA/G1 variants)  (`kimodo`)
- **License:** Code Apache-2.0; checkpoints under separate licenses (NVIDIA Open Model License for Rigplay-trained; BONES-SEED variants inherit dataset terms) — <https://huggingface.co/spaces/nvidia/Kimodo/raw/main/LICENSE>
- **Evidence (quote/summary):** "Apache License 2.0, Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES (LICENSE file read). Checkpoint terms: search snippet only."
- **Commercial OK:** **needs_counsel** (counsel needed: Check each checkpoint model card before using generated motion as training data.). Apache-2.0 code is commercial-OK; per-checkpoint terms not verified by me. Synthetic motion generated from a checkpoint trained on BONES-SEED might itself fall under the 'commercially substitutable synthetic dataset' restriction only for BONES-licensees.
- **Attribution:** Apache-2.0 notice; checkpoint terms per card.  **ML training:** Per checkpoint.
- **Golf relevance:** low. **Domain:** model + checkpoints; generator of human/humanoid motion.
- **Verification:** secondary_search_snippet

### Edinburgh DataShare doi:10.7488/ds/3823 (golf wrist angular velocity, club data, EMG)  (`edinburgh_wrist_golf`)
- **License:** CC BY 4.0 (record license text) — <https://doi.org/10.7488/ds/3823>
- **Evidence (quote/summary):** "License text file CC BY 4.0 (read in docs/research_open_data_v3.md). GYRO_and_Club_Data.xls returns 401; request-a-copy."
- **Commercial OK:** **needs_counsel** (counsel needed: Human-subject consent; file not obtained.). CC BY allows commercial use with attribution, but human-subject consent for commercial ML not documented; file not obtained.
- **Attribution:** CC BY 4.0 attribution.  **ML training:** None.
- **Golf relevance:** high but gated. **Domain:** golf: 15 sub-elite golfers, per-phase wrist angular velocity.
- **Verification:** secondary_search_snippet

### Harvard Dataverse 'Golf Swing Performance Dataset' (doi:10.7910/DVN/SFYVDN)  (`harvard_sfyvdn`)
- **License:** CC0 on record, but re-upload of third-party Kaggle data — <https://doi.org/10.7910/dvn/sfyvdn>
- **Evidence (quote/summary):** "This dataset ... sourced from a publicly available dataset on Kaggle, originally collected using a launch monitor."
- **Commercial OK:** **no**. Uploader cannot waive rights in third-party data; no consent for the videos. Rejected (not downloaded).
- **Attribution:** n/a  **ML training:** n/a
- **Golf relevance:** low. **Domain:** golf: launch-monitor table copied from Kaggle + 2 personal videos.
- **Verification:** secondary_search_snippet

## Gaps / not verified
- Sizes for AMASS, Human3.6M, HumanML3D, Motion-X, 3DPW, BEDLAM, KIT, Mixamo, OpenCap datasets are not confirmed here.
- Direct fetches of the Panoptic page, SimTK, Kimodo GitHub README, SMPL-X license, BEDLAM2 and Adobe's Mixamo Additional Terms PDF failed or were not read; those rows rely on search summaries and are labelled so.
- Other sources noticed but not surveyed: TotalCapture, HuMMan, EgoBody, GRAB, KIT-ML, Kaggle/Roboflow golf sets (see docs/research_open_data_v3.md for the latter).
- Licenses can change; re-check before any release. Nothing here replaces counsel.
