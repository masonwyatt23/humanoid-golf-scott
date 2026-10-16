"""CaddieSet (damilab/CaddieSet, CVPRW 2025) -> event-level driver feature summary JSON.

License check (2026-10-16): the GitHub repo LICENSE is the MIT License (Copyright (c) 2024 damilab) and the CSV is
data/CaddieSet.csv in that repo; README calls it the 'Official dataset'.  MIT is a software licence applied to a
data file and the README gives no separate data-use/consent statement, so counsel should confirm; we only use
numeric per-event joint features (no video, no faces) and store summary statistics, not the raw CSV.
Content: 1,757 shots, 8 golfers, FACEON/DTL views, per-shot ball data and 2D-vision-derived joint features at 8
swing events (events 0-7, presumably Address, Toe-up, Mid-backswing, Top, Mid-downswing, Impact, Mid-follow-through,
Finish: inferred from the feature names, not documented in the README).  Features are ~50 % missing, handedness is not
recorded, driver (W1) ball speed tops out at 69.4 m/s (about 155 mph; roughly 105 mph club speed), so this is NOT
a 120 mph reference.  Output is not an .npz trajectory: the training code cannot consume it; it is a diagnostic prior.

    python -m data.convert_caddieset --csv /workspace/golf_scratch/v3/ext/CaddieSet.csv
(raw CSV: https://raw.githubusercontent.com/damilab/CaddieSet/main/data/CaddieSet.csv; keep out of git)
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "references" / "caddieset_driver_event_features.json"
LICENSE = dict(license_class="mit_repo_data", commercial_ok=True, provenance_source="damilab/CaddieSet (GitHub)",
               provenance_note="Repo LICENSE = MIT (c) 2024 damilab; no separate data/consent statement; counsel to confirm. "
                               "Summary statistics only; raw CSV not redistributed.",
               acknowledgment_required=True,
               acknowledgment_text="Jung et al., CaddieSet: A Golf Swing Dataset with Human Joint Features and Ball Information, "
                                   "CVPR Workshops 2025 (MIT licence, damilab).")


def summarize(df, feats):
    out = {}
    for c in feats:
        v = pd.to_numeric(df[c], errors="coerce").dropna().to_numpy(float)  # CSV contains "#NAME?" spreadsheet errors
        if len(v) >= 10:
            out[c] = dict(n=int(len(v)), median=round(float(np.median(v)), 3),
                          q25=round(float(np.percentile(v, 25)), 3), q75=round(float(np.percentile(v, 75)), 3))
    return out


def main(csv):
    d = pd.read_csv(csv)
    w1 = d[d.ClubType == "W1"]
    feats = [c for c in d.columns[11:]]
    res = dict(license=LICENSE, source_rows=int(len(d)), driver_rows=int(len(w1)),
               note="2D vision-derived features; angles in degrees, ratios dimensionless; events 0-7 (see module docstring)",
               groups={})
    for view in ("FACEON", "DTL"):
        s = w1[w1.View == view]
        cut = float(s.BallSpeed.quantile(0.75))
        fast = s[s.BallSpeed >= cut]
        res["groups"][view] = dict(
            n_all=int(len(s)), ball_speed_ms=dict(median=round(float(s.BallSpeed.median()), 2), max=float(s.BallSpeed.max())),
            fast_quartile_ball_speed_ms_min=round(cut, 2), n_fast=int(len(fast)),
            all=summarize(s, feats), fast_quartile=summarize(fast, feats))
    OUT.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print("wrote", OUT, res["driver_rows"], "driver rows")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    main(ap.parse_args().csv)
