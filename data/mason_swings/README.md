# data/mason_swings/

Drop **your own** swing videos here (one swing per file). Raw videos are git-ignored and must
never be committed. Do not put anyone else's footage here.

    python -m data.ingest_mason_swings --dry-run         # validate only
    python -m data.ingest_mason_swings --capture-fps 240 # slow-mo files exported at 30 fps
    python -m data.ingest_mason_swings                   # resumable; re-run after adding files

Outputs: `data/references/mason_<name>.npz` (source=`mason_self_filmed`, is_synthetic=False) plus
`data/references/mason_ingest_report.json`.

**Naming:** `mason_YYYYMMDD_<club>_<view>_<NNN>.mp4`, e.g. `mason_20261016_driver_dtl_001.mp4`
(view: `dtl` or `fo`). Club/view are read from the name if no sidecar says otherwise.

**Sidecar (optional):** `metadata.csv` (see `metadata.example.csv`) or `metadata.json` or
`<video>.json` with `club, view, handedness, capture_fps`. Precedence: CLI --capture-fps >
per-video json > metadata.csv/json > filename > defaults (right-handed).

**Common errors:** `unreadable` (re-export/convert to H.264 mp4), `low_resolution` (<360px short
side), `too_long` (trim to one swing), `no_person` / `person_intermittent` (whole body in frame),
`bad_fps` (capture_fps must be the real camera rate), `insufficient_valid_frames`.

Full guide: `docs/MASON_SWINGS.md`.
