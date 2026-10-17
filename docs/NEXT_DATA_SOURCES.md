# Most practical real PureGolf / Adam Scott data sources (ranked)

Status: no openly licensed Adam Scott swing video exists that I could find (Wikimedia
Commons has 16 files, all photos). Everything below needs permission or a licence unless
stated. Not legal advice.

1. **Ask for permission from the high-fps creators (best quality / effort).**
   Golf Loopy (300 fps FO iron, 2014) and "GOLF JAPAN" / golftweet.com (250 fps DTL+FO
   Scott clips: Australian Open 2019 drivers, Wentworth 2021 irons). Fixed cameras and
   two views make pose estimation far better than reels. Email the owners for
   research-use permission; ask explicitly about trained-model/derived-data use.
2. **Official channels, with ToS review**: DP World Tour YouTube (Scott slow-motion
   2025 Hero Dubai Desert Classic, 3:25), PGA Tour / Golf Channel / Titleist clips.
   Fine for personal research viewing; get written clearance before redistributing
   data or shipping a model trained on them.
3. **PureGolf (@puregolf__)**: contact the account for a content partnership. Do not
   scrape Instagram (ToS). Clips would be a few seconds each at 30-60 fps; best treated
   as *style* validation, not bulk training.
4. **Licensed motion data**: commercial mocap/biomechanics vendors (e.g. TPI / K-Vest /
   Sportsbox 3D / GEARS style 3D data), or a university biomechanics lab with Tour-player
   datasets. Highest quality (true X-factor, sequencing, club), cost/licensing needed.
5. **Open golf / human-motion datasets for pre-training** (check licences): AMASS and
   other SMPL mocap that include golf swings, GolfDB (event-annotated golf swing videos,
   research use), 3D golf pose datasets from papers. Good for generic swing priors, not
   Scott style.
6. **Self-capture**: film an amateur/pro cooperator at 240 fps DTL + FO with fixed tripods
   (iPhone slo-mo), run WHAM/GVHMR. Fully owned data; best long-term path for a
   defensible training set, and lets you pair with a Scott-style coach drill.

Practical next steps: (a) send permission requests to #1 and #3; (b) install WHAM or
GVHMR on a GPU box (docs/WHAM_GVHMR.md); (c) record 20-50 owned swings; (d) calibrate
`STYLES` in `data/generate_synthetic_scott.py` against measured tempo / X-factor from
real clips; (e) fix the degree/radian mismatch in `HumanoidGolfEnv` (uses `joints_rad`).

## Addendum 2026-10-17: additional sources checked (documentation only; nothing downloaded)

Verification level is stated per row; "search snippet" means I only saw the repo/search summary, not the LICENSE file. Not legal advice.

| Source | What | License / terms seen | Provenance tag if ever used | Verdict |
|---|---|---|---|---|
| GolfPose (MingHanLee/GolfPose, ICPR 2024) | 3D golf-swing pose GT (`data_3d_golf_gt.npz`) + 2D | Dataset is released **on request by email to the authors**; no license text found in the repo summary (search snippet) | `license_class=unknown`, `commercial_ok=False` until written terms | Ask in writing (research + commercial + derived-model use). Do not use before reply. |
| Pose2Par (cavanaulton/Pose2Par, 2026) | **Tool**, not data: MMPose + OpenSim pipeline giving pelvis/torso rotation, X-factor, event timing from video up to 120 fps | Repo MIT (search snippet); components MMPose/OpenSim Apache-2.0; `marker-enhancer/LICENSE` **not checked**; its accuracy claim ("validated vs lab mocap") is the authors' claim, unverified | n/a (processing tool; outputs on Mason's own video would be `self_owned`) | Candidate for extracting X-factor/pelvis from Mason's 240 fps session (see docs/FILMING_PROTOCOL.md) after reading the marker-enhancer license. |
| CMU Mocap Kaggle mirror (kmader/cmu-mocap) | Same CMU data re-hosted | Kaggle page lists **CC BY-ND 4.0** on top of CMU's own text (search snippet). That conflicts in spirit with CMU's original grant ("free for all uses, no direct resale") | keep `cmu_permissive` sourced from mocap.cs.cmu.edu only | Do **not** use the Kaggle mirror; keep fetching/citing the original mocap.cs.cmu.edu terms (already done). No-derivatives wording would be a problem for converted data. |
