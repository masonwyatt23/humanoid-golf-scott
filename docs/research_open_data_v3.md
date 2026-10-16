# Research v3: further search for commercially usable golf motion data (2026-10-16 ET)
Extends docs/research_open_data_v2.md. Engineering diligence, **not legal advice**. "[primary]" = read from the source's own page/API/raw file today.

## Result: no new swing-trajectory source. One low-value summary-statistics source converted; one gated; the rest no-go.
| Source | Content | License evidence | Verdict |
|---|---|---|---|
| **CaddieSet** (damilab/CaddieSet, CVPRW 2025; `data/CaddieSet.csv`, 508 KB) | 1,757 shots, 8 golfers, face-on + DTL, ball data, 2D-vision-derived joint features at 8 events (50 % missing); driver ball speed max 69.4 m/s | GitHub `LICENSE` = MIT, "Copyright (c) 2024 damilab" [primary, raw file]; README gives no separate data/consent statement; earlier docs listed it as "no license", now MIT | **Converted to summary JSON only** (`data/convert_caddieset.py` -> `data/references/caddieset_driver_event_features.json`, 1,137 driver rows). MIT-on-data and consent need counsel. Low value: no trajectories, no handedness, noisy features (e.g. hip rotation at the top median 7.8 deg), ~105 mph club-speed ceiling |
| Edinburgh DataShare doi:10.7488/ds/3823 (wrist angular velocity, club data, EMG; 15 sub-elite golfers) | per-phase max/min wrist angular velocity, clubhead speed/path at impact, driver included | license text file is **CC BY 4.0** [primary: datashare.ed.ac.uk bitstream `license_text`] (the v2 doc could not read it) | **Gated, not obtained:** `GYRO_and_Club_Data.xls` returns HTTP 401 / login page (request-a-copy); only the EMG file is open, which is irrelevant. Worth emailing the depositor (Howie Carson) if wrist angular velocity peaks are wanted |
| Harvard Dataverse doi:10.7910/DVN/SFYVDN "Golf Swing Performance Dataset" | launch-monitor table copied "from a publicly available dataset on Kaggle" + 2 personal .mov clips (17 MB, 24 MB) + notes | CC0 1.0 in the record [primary] | **No-go:** re-upload of third-party Kaggle data (the uploader cannot waive rights they do not hold), launch metrics only, 2 videos of an unidentified person, no consent statement; not downloaded |
| NLDL 2023 "Evaluating monocular 3D pose models for golf" (Qualisys marker mocap, 124 swings, 4 golfers, 85 fps) | marker-based ground-truth 3D swings | article is CC BY 4.0 [primary]; the page has no dataset link or data statement | **Not available** (dataset not published; contact authors) |
| Hugging Face `34data/golf-pose` (361 rows, 2.75 GB zip) | video zip | no license field/tags in the API record [primary], no dataset card | **No-go** (no license, unknown subjects) |
| Kaggle `thomassimm/golfdb3` (marked CC0) | GolfDB model weights + test video, no new data | CC0 label on a re-upload of wmcnally/golfdb (non-commercial research data) | **No-go** (label cannot override GolfDB's terms) |
| Roboflow Universe golf keypoint sets (422 / 450 images) | 2D keypoints/boxes | no license stated on the pages [primary] | **No-go** |
| GolfPose (MingHanLee) | 3D golf mocap GT | dataset behind an email-authorisation gate; no license | unchanged: ask in writing |
| Zenodo / Figshare / Dataverse / Dryad API searches ("golf swing", "golf motion capture", "golf pose estimation", "golf swing IMU", "golf kinematics") | only PDFs, surveys, EMG/putting/fNIRS, ball aerodynamics; Zenodo 7233465 (pelvis/torso sex differences) has no license and no files | n/a | **Nothing usable** |
| MultiSenseGolf, more participants | P10 (105 mph) and P14 (96 mph), same CC0 record as v2 | as in v2 | **Available, not converted** this round (1-2 GB zips each); P10 would be the fastest swings (105 mph vs 102.7 max converted). Say if wanted |

## Honest bottom line
Nothing found that adds open, commercially usable full-body swing trajectories beyond CMU (10 swings, optical) and MultiSenseGolf (28 converted,
more available). No open dataset has left-handed or 120+ mph swings; Mason's own footage (best: filmed at 240 fps from two angles) remains the
only route to a left-handed 120+ mph reference.
