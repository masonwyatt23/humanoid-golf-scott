"""Manifest of files derived from Mason's Instagram-feed screen recordings.

Read-only: lists git-tracked files at a ref (default origin/main) plus local untracked/ignored ones.
Usage: python -m data.instagram_derived_manifest [--ref origin/main] [--local-repo PATH] [--out-json P] [--out-md-table]
No file is moved or deleted. Nothing here is legal advice; 'third_party_content' is UNREVIEWED for all items.
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ("keep_private", "release_aggregates_only", "needs_counsel", "safe")
THIRD = "unreviewed (feed recordings may contain other people's posts/likeness/music; nobody has checked)"

# (regex, derivation, content_type, release, note)
RULES = [
    (r"^data/references/mason_swing_part\d_s\d+(_refined)?(_mirrored)?\.npz$", "v1 first pass / refined, parts 1-3 of feed recordings", "pose landmarks (33x4 MediaPipe) + 11 joint angles + metadata", "needs_counsel", "per-frame body pose of an identifiable person; no pixels"),
    (r"^data/references/mason_v2_p\d_s\d+(_partial)?(_unmirrored)?\.npz$", "v2 re-mine of same parts 1-3 (native or mirrored)", "pose landmarks + joint angles + metadata", "needs_counsel", "same as v1"),
    (r"^data/references/mason_v3_p\d_s\d+_slowmo\.npz$", "v3 re-mine of slow-motion segments in parts 1-2", "pose landmarks + joint angles + metadata", "needs_counsel", "same as v1"),
    (r"^data/references/mason_(v2|v3|feed)_report\.json$|^data/references/mason_cadence_audit\.json$", "per-clip QC of the recordings", "per-clip metadata/aggregates (timestamps in video, quality)", "release_aggregates_only", "includes per-clip timestamps that locate clips in the source recordings"),
    (r"^data/references/mason_(target_features|impact_geometry_targets|impact_face_path_proxies|keyframe_targets(_extra)?|elbow_address_stats|elbow_camera_bias|vs_profiles)\.json$", "computed from mason_v2/v3 npz", "joint-angle / aggregate statistics", "release_aggregates_only", "per-clip entries are also per-swing joint data; pooled stats only are lowest risk"),
    (r"^data/references/(wrist_elbow_event_targets|wrist_sign_mapping)\.json$", "computed from mason_v2 clips (plus CMU for comparison)", "per-clip joint angles and mapping constants", "release_aggregates_only", "contains Mason per-clip values; CMU part is separate (needs_counsel by its own audit)"),
    (r"^data/reference_sets/unified_v[12](_sampling)?\.json$", "index of reference clips; Mason entries point to npz paths", "manifest (paths, weights, flags); no pose data", "safe", "only the Mason entries are Instagram-derived; low risk by itself"),
    (r"^data/(ingest_mason_swings|process_mason_swings|refine_swings|ingest_feed_recordings|remine_feed_v2|remine_slowmo_v3|audit_feed_cadence|mason_[a-z_]+|compare_mason_to_profile|wrist_elbow_event_targets|wrist_sign_mapping|unified_refset)\.py$", "code", "code", "safe", "code only; unified_refset/ingest scripts contain no data (verify before release)"),
    (r"^data/mason_swings/(README\.md|metadata\.example\.csv|\.gitkeep)$", "placeholders/instructions", "docs", "safe", "raw videos in this dir are git-ignored"),
    (r"^docs/(MASON_[A-Z_]+|WRIST_ELBOW_EVENT_TARGETS|WRIST_SIGN_MAPPING|UNIFIED_V1_LICENSE_AUDIT)\.md$", "doc quoting Mason-derived numbers", "docs with per-clip/aggregate numbers", "release_aggregates_only", "check per-clip tables before release"),
    (r"^(tests/test_(ingest_mason|mason_[a-z_]+|wrist_elbow_event_targets|wrist_sign_mapping|unified_refset)\.py)$", "tests", "code", "safe", "may read Mason npz files"),
]


def sh(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False).stdout


def classify(path):
    for rx, deriv, ctype, rel, note in RULES:
        if re.search(rx, path):
            return deriv, ctype, rel, note
    return None


def npz_meta(blob):
    try:
        import io, numpy as np
        z = np.load(io.BytesIO(blob), allow_pickle=True)
        g = lambda k: (z[k].item() if k in z.files and z[k].ndim == 0 else None)
        arr_kinds = {n: (list(z[n].shape), str(z[n].dtype)) for n in z.files if z[n].ndim >= 2}
        return {"source_file": str(g("source_file")), "swing_index": g("swing_index"), "t_start_in_video": g("t_start_in_video"),
                "view": str(g("view")), "handedness": str(g("handedness")), "mirrored": g("mirrored"),
                "n_landmark_frames": (z["landmarks"].shape[0] if "landmarks" in z.files else None),
                "has_image_like_array": any(len(s) >= 3 and d in ("uint8",) for s, d in arr_kinds.values()),
                "license_class": str(g("license_class")), "commercial_ok": g("commercial_ok")}
    except Exception as e:  # unverified
        return {"error": repr(e)}


def build(ref="origin/main", local_repo=None):
    files = sh(["git", "ls-files", "-z", "--with-tree=" + ref] if False else ["git", "ls-tree", "-r", "-z", "--name-only", ref], ROOT).split("\0")
    entries, unclassified = [], []
    for p in filter(None, files):
        c = classify(p)
        if c is None:
            continue
        deriv, ctype, rel, note = c
        blob = subprocess.run(["git", "show", f"{ref}:{p}"], cwd=ROOT, capture_output=True).stdout
        e = {"path": p, "git_tracked_on_ref": True, "derivation": deriv, "content_type": ctype, "size_bytes": len(blob),
             "sha256": hashlib.sha256(blob).hexdigest()[:16], "raw_frames_or_images": "none found" if p.endswith(".npz") else "none (text)",
             "third_party_content_risk": THIRD, "release_recommendation": rel, "note": note,
             "mentions_mason_count": len(re.findall(rb"(?i)mason", blob)) if not p.endswith(".npz") else None}
        if p.endswith(".npz"):
            m = npz_meta(blob); e["npz"] = m
            if m.get("has_image_like_array"): e["raw_frames_or_images"] = "UNEXPECTED uint8 array"
            e["instagram_derived_confirmed"] = bool(m.get("source_file", "").startswith("mason_swing_part"))
        entries.append(e)
    # other tracked files that merely mention Mason-derived artifacts (grep, not exhaustive proof)
    mention = sh(["git", "grep", "-l", "-E", "mason_swing|mason_v2|mason_v3|mason_keyframe|mason_target|wrist_elbow_event|wrist_sign_mapping", ref, "--"], ROOT)
    known = {e["path"] for e in entries}
    other = []
    for line in mention.splitlines():
        p = line.split(":", 1)[1] if ":" in line else line
        if p not in known and not p.startswith("logs/"):
            other.append(p)
    local = {"note": "from --local-repo status; not in git. Never committed/deleted by this script."}
    if local_repo:
        st = sh(["git", "status", "--short", "--ignored", "--", "data", "logs"], local_repo)
        local["ignored_or_untracked"] = [l for l in st.splitlines() if re.search(r"(?i)mason|instagram|\.mov|raw", l)]
    return entries, sorted(other), local


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main"); ap.add_argument("--local-repo")
    ap.add_argument("--out", default=str(ROOT / "data/references/instagram_derived_manifest.json"))
    a = ap.parse_args()
    entries, other, local = build(a.ref, a.local_repo)
    from collections import Counter
    out = {"status": "DRAFT; UNVERIFIED legal/third-party content; classification rules are heuristic (see script RULES)",
           "ref": a.ref, "ref_sha": sh(["git", "rev-parse", a.ref], ROOT).strip(), "n_entries": len(entries),
           "counts_by_recommendation": dict(Counter(e["release_recommendation"] for e in entries)),
           "entries": entries, "other_tracked_files_mentioning_mason_artifacts": other, "local_untracked_ignored": local}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(out["n_entries"], out["counts_by_recommendation"], "other:", len(other))


if __name__ == "__main__":
    main()
