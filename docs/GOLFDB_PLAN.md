# GolfDB acquisition & processing plan (research only; nothing downloaded)

Status: PLANNING ONLY. No video and no video-bearing file was downloaded. Only the 117 KB
annotation file `golfDB.mat` was read (to a temp dir outside the repo) to count players. Verified 2026-10-15.

## 1. Where things live
| Item | Location |
|---|---|
| Repo (code + annotations) | https://github.com/wmcnally/golfdb (branch `master`) |
| Annotations | `data/golfDB.mat` (117 KB) and `data/golfDB.pkl` (709 KB) in that repo; `data/generate_splits.py` converts .mat -> pandas |
| Paper | McNally et al., "GolfDB", CVPR Workshops 2019, https://arxiv.org/abs/1903.06528 , https://doi.org/10.1109/cvprw.2019.00311 |
| Preprocessed 160x160 clips | Google Drive link in the README (`videos_160`, clipped from event[0] to event[-1]). **Video-bearing: not downloaded.** |
| YouTube sources | `youtube_id` column in the annotations (580 unique videos); `data/preprocess_videos.py` expects you to fetch them yourself |
| Project page | The UWaterloo VIP-lab demo page exists but I could not extract any licence text from it. |

## 2. License and terms
- README states: "The code in this repository is licensed under CC BY-NC 4.0." There is no LICENSE file (GitHub API reports no licence; LICENSE/LICENSE.md 404). The README wording says *code*; it says nothing explicit about the annotation file or the videos. Safest reading: treat the annotations as CC BY-NC 4.0 too (attribution, **non-commercial only**), and cite the paper.
- **Videos are not the authors' to license.** They are third-party YouTube uploads (golf broadcasts/tour channels; copyright belongs to uploaders/tours). CC BY-NC on the repo does not grant rights to them, and the 160x160 Drive copy is a redistribution of that third-party footage with no stated licence.
- YouTube ToS generally prohibits downloading content except via a provided download/offline feature, and prohibits circumventing it. Downloading via the youtube_id links, or using the Drive copy, therefore carries copyright and ToS risk. Research/academic fair-use arguments are jurisdiction-dependent; **I am not a lawyer and this is not legal advice.** Training a model used in a commercial product on this footage is the highest-risk use.
- Conclusion: obtaining the videos is **not clearly permitted** for our use. The authors do not grant permission for the video content; permission would have to come from the rights holders.

## 3. How videos are obtained per authors
1. Easy path: download `videos_160` from the Drive link in the README (no licence given; redistribution of third-party footage).
2. Full-resolution path: download YouTube videos by `youtube_id` yourself, then run `data/preprocess_videos.py` (crops by `bbox`, keeps frames events[0]..events[-1], resizes/pads to dim x dim). Note it opens files named `<youtube_id>.mp4` in `../../database/videos/`; the repo ships no downloader.
Many of the 580 videos may now be removed/private; availability is unverified.

## 4. Annotation contents (verified from golfDB.mat)
1400 samples x fields: `id, youtube_id, player, sex, club, view, slow, events, bbox, split`.
- `events`: 10 frame indices = [sample start, 8 events, sample end], in the source video's frame numbering (1-based in preprocess script).
- `bbox`: normalized [x, y, w, h]. `slow`: 0/1 slow-motion flag. `split`: 1-4 (350 each).
- **8 events:** 1 Address, 2 Toe-up (backswing), 3 Mid-backswing (arm parallel), 4 Top, 5 Mid-downswing (arm parallel), 6 Impact, 7 Mid-follow-through (shaft parallel), 8 Finish.
- Note: annotators could not label precisely at 30 fps real-time (per paper); events are +/- a few frames.

## 5. Players present (player names ARE in the labels)
246 unique player names, in upper case. Both sexes: 783 male, 617 female samples. Clubs: driver 952, iron 229, fairway 162, hybrid 34, wedge 23. Views: down-the-line 585, face-on 461, other 354. Slow-mo 642, real-time 758.
- **ADAM SCOTT: 17 samples from 6 YouTube videos** (ids 1yBqlMwG8Lw, AmJx1lu1fv8, XwnbLuQSLuY, jbB8LaUIq1c, t-DfeLMz6Rc, wnNyaR1S28w). 8 driver, 7 iron, 2 wedge; views: down-the-line 5, face-on 4, other 8; slow-mo 8 / real-time 9. Splits: 12 in split 1, 3 in 4, 2 in 2.
- Other relevant: RORY MCILROY 27, TIGER WOODS 53, JUSTIN ROSE 16, HENRIK STENSON 15, JASON DAY 10, DUSTIN JOHNSON 12, JUSTIN THOMAS 12, BUBBA WATSON 14, RICKIE FOWLER 18, PHIL MICKELSON 11, FRED COUPLES 14, LYDIA KO 58, MICHELLE WIE 54.
- **Scottie Scheffler: absent** (0 samples; the dataset predates his rise).
- Name is as labelled by annotators; I did not verify each against the video.

## 6. Conversion to our `.npz` format (if/when videos are cleared)
Steps (video acquisition gated on Section 8):
1. Load `golfDB.mat` (see `generate_splits.py`); filter `player == "ADAM SCOTT"` (optionally prefer view `face-on` / `down-the-line`, driver/iron, `slow==1`).
2. Obtain the clip. Prefer own-licence/permissioned source frames at native resolution; the 160x160 clips work but see limits below.
3. For each sample cut frames events[0]..events[-1] (already done in `videos_160`). Store the 10 event indices relative to events[0].
4. Run `python data/process_video.py --videos <dir> --out data/references_golfdb --capture-fps <native fps>`. Only declare `--capture-fps` for slow-mo (`slow==1`) clips when the true camera rate is known; GolfDB does not store it, so tempo from slow-mo clips is **unreliable** unless the rate is determined (e.g., YouTube source metadata). Real-time clips: pass nothing (container fps used).
5. **Event-based time normalization:** map the 8 events to the reference's phases. Compute backswing time = (Top - Address) and downswing time = (Impact - Top) in real seconds, tempo = back/down (only trustworthy at true fps >= ~120). Piecewise-linearly resample each segment between consecutive events to fixed frame counts, then convert to `dt=0.01` (process_video's `--out-dt`) using the real durations. This needs a small extension (events are not yet consumed by process_video.py); then add `events` and `tempo_ratio` keys to match the synthetic files.
6. Keys we can fill: `time`, `joints` (deg, crude single-view proxies), `valid_mask`, `landmarks` (n,33,4), `source`, `events`, `tempo_ratio` (conditional, above), approximately `pelvis_rot_deg`/`thorax_rot_deg`/`x_factor_deg` (only from face-on... and still 2D-ambiguous), `wrist_hinge_deg` (rough). Mark `style="real_golfdb_<player>"` and `source` with annotation id + youtube_id + license note.
7. Keys we **cannot** recover: `club_head` (no club tracking; MediaPipe has none), `joints_rad` (derive by deg2rad), `lateral_sway_m` (no metric scale), `plane_angle_deg` (needs 3D), reliable 3D joint angles (single uncalibrated view; use WHAM/GVHMR per docs/WHAM_GVHMR.md, which adds its own SMPL licence caveat).
8. Resolution limits: at 160x160 the golfer is ~100-150 px tall; MediaPipe landmarks (wrists, hands, ankles) jitter and low visibility is common, and fast downswing motion blur/compression hurts most near impact. Expect many rejected clips (`--min-valid-frac`). Full-res crops (via bbox) are far better but need source videos.
9. Quality gate: reject clips with <60% valid frames, sanity check event order, and keep all derived data flagged non-commercial in metadata.

## 7. Licensing / commercial-use caveats
- CC BY-NC 4.0 (stated for repo): must attribute (cite paper), no commercial use; derived .npz/model weights trained on it should be treated as non-commercial too (conservative).
- Underlying video copyright & YouTube ToS are separate and unresolved.
- Keep GolfDB-derived files segregated (e.g. `data/references_golfdb/`, never mixed into shipping artifacts) and do not redistribute the clips or derived landmarks publicly.
- Adam Scott's likeness/name: using his name for a product style would raise separate publicity-rights questions for a commercial product.

## 8. Go / No-go
- **Metadata (labels, names, events): GO.** Already usable for planning (done); cite the paper, non-commercial.
- **Video download (Drive 160x160 or YouTube): NO-GO until Mason decides.** Licence for videos is absent and ToS/copyright risk exists. Even for research-only use it is a judgement call, and for any commercial use it should be a no.
- Practical value is also modest: only 17 Scott samples / 6 source videos, mostly 30 fps-class footage with imprecise events, at 160x160.

## 9. Decisions needed from Mason
1. Is this project strictly non-commercial research? If commercial intent, drop GolfDB videos entirely.
2. Accept the legal/ToS risk of downloading the 160x160 Drive clips or YouTube videos for private research (or only permit after counsel review)? Which subset (Scott's 17 only, vs. a handful of other pure swingers)?
3. Alternatively, authorise contacting rights holders (YouTube channel owners / tours) or the GolfDB authors for permission.
4. Approve extending `process_video.py` to consume the `events` array for event-based normalization (code change, no data).
5. How to treat slow-mo clips with unknown capture fps (skip vs. estimate).
6. Whether to use Scott's name in the shipped style label.
