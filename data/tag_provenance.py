"""Retro-tag reference .npz files with provenance/licensing keys. Idempotent, atomic, array-preserving.

  python -m data.tag_provenance [--dir data/references] [--force] [--dry-run]
Existing tags are kept unless --force. Prints a summary table.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

from data import provenance as P


def tag_file(path: Path, force: bool = False, dry_run: bool = False) -> str:
    with np.load(path, allow_pickle=True) as z:
        arrays = {k: z[k] for k in z.files}
    if "license_class" in arrays and not force:
        return "skipped"
    kind = P.infer_kind(path.stem, arrays)
    P.tag(arrays, kind, overwrite=True)
    if not dry_run:
        P.save_npz_atomic(path, arrays)
    return f"tagged:{arrays['license_class'].item()}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent / "references"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    for f in sorted(Path(a.dir).glob("*.npz")):
        print(f"{f.name:48s} {tag_file(f, a.force, a.dry_run)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
