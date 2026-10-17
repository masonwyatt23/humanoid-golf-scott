"""Retag MultiSenseGolf reference .npz files: cc0/commercial_ok=True -> needs_counsel/commercial_ok=False.

Only license metadata fields are changed (license_class, commercial_ok, provenance_note, plus the added
license_class_as_published and counsel_required). All other arrays are saved unchanged and asserted equal after rewrite.
Idempotent. Not legal advice; see docs/UNIFIED_V1_LICENSE_AUDIT.md.

  python scripts/retag_multisense.py [--dir data/references] [--dry-run]
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data import provenance as P  # noqa: E402

CHANGED = ("license_class", "commercial_ok", "provenance_note", "license_class_as_published", "counsel_required")


def retag_file(path, dry_run=False):
    path = Path(path)
    with np.load(path, allow_pickle=True) as d:
        before = {k: d[k] for k in d.files}
    new = P.preset("multisensegolf_needs_counsel")
    after = dict(before)
    for k in CHANGED:
        v = new[k]
        after[k] = np.array(v, dtype=bool) if isinstance(v, bool) else np.array(str(v))
    if all(k in before and before[k].shape == () and before[k].item() == after[k].item() for k in CHANGED):
        return "skipped"
    if dry_run:
        return "would_retag"
    tmp = path.with_name(path.stem + ".retagtmp.npz")
    try:
        np.savez(tmp, **after)
        with np.load(tmp, allow_pickle=True) as chk:
            assert set(chk.files) == set(after), "key set changed"
            for k in before:
                if k in CHANGED:
                    continue
                assert before[k].dtype == chk[k].dtype and np.array_equal(before[k], chk[k], equal_nan=True) if before[k].dtype.kind == "f" \
                    else np.array_equal(before[k], chk[k]), f"array {k} changed in {path.name}"
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return "retagged"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parents[1] / "data" / "references"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    counts = {}
    for p in sorted(Path(a.dir).glob("multisense_*.npz")):
        r = retag_file(p, a.dry_run)
        counts[r] = counts.get(r, 0) + 1
    print(counts)
    return counts


if __name__ == "__main__":
    main()
