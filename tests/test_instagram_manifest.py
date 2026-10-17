import json, re
import pytest
from pathlib import Path
from data.instagram_derived_manifest import classify

ROOT = Path(__file__).resolve().parents[1]


def test_classify_known_paths():
    assert classify("data/references/mason_v2_p1_s06.npz")[2] == "needs_counsel"
    assert classify("data/references/mason_keyframe_targets.json")[2] == "release_aggregates_only"
    assert classify("data/references/cmu_64_01.npz") is None


def test_manifest_has_no_raw_media_or_emails():
    p = ROOT / "data/references/instagram_derived_manifest.json"
    if not p.exists():
        pytest.skip("manifest JSON held back from the public repo pending Mason's decision")
    d = json.loads(p.read_text())
    assert d["n_entries"] == len(d["entries"]) > 0
    assert all(not e["path"].lower().endswith((".mov", ".mp4", ".png", ".jpg")) for e in d["entries"])
    assert all(e["raw_frames_or_images"] != "UNEXPECTED uint8 array" for e in d["entries"])
    assert not re.search(r"[\w.]+@[\w.]+\.\w+", p.read_text() + (ROOT / "docs/INSTAGRAM_DERIVED_MANIFEST.md").read_text())
