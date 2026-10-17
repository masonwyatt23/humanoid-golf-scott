"""Unified training reference set (unified_v1): manifest builder + loader helpers.

Does not modify env/train/eval. Works with imitation.reference_dataset.ReferenceDataset-style dicts
(`path, joints, club_head, dt, name, license_class, commercial_ok` + extra provenance fields).

  python -m data.unified_refset build      # rewrite data/reference_sets/unified_v1.json (+ sampling config if absent)
  from data.unified_refset import load_manifest, load_sampling_config, split_entries, sample, load_refs
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "data" / "references"
SET_DIR = ROOT / "data" / "reference_sets"
MANIFEST = SET_DIR / "unified_v1.json"
SAMPLING = SET_DIR / "unified_v1_sampling.json"

DEFAULT_SAMPLING = {
    "version": "unified_v1",
    "source_weights": {"mason": 0.6, "multisense": 0.2, "cmu": 0.2},
    "quality_power": 1.0,
    "rationale": ("Mason is the target player (left-handed, native footage) so he gets the highest total mass (0.6); "
                  "MultiSenseGolf (28 mirrored CC0 swings, 89-103 mph, IMU mocap) and CMU subject 64 (slow recreational "
                  "mocap, mirrored on load) are movement-sequencing priors at 0.2 each. Within a source the per-file "
                  "weight is quality_score**quality_power, normalised to sum to the source weight. Mason quality_score is "
                  "the video heuristic (0.66-0.83); MultiSense/CMU have none so quality=1-0.15*n_qc_flags (floor 0.05). "
                  "Weights are a prior, not tuned."),
    "multipliers": {"flip_edit_unmirrored": 1.0, "slowmo": 0.0},
    "slowmo_note": ("Slow-mo v3 swings are on a stretched video time axis (~3-6x), so they are excluded from default "
                    "sampling (multiplier 0). Set multipliers.slowmo>0 only if you resample with time_real_est."),
    "val_fraction": 0.2,
    "min_val_per_source": {"mason": 2, "multisense": 2, "cmu": 2},
    "split_seed": 20261016,
}

CMU_ACK = ("The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding "
           "from NSF EIA-0196217. (CMU: free for all uses incl. commercial; do not resell/distribute the converted data standalone.)")
MS_CITE = ("Oh, Seong, Ko, Lim, Kim, Choi, DelPreto, Rus, Kim. MultiSenseGolf, Harvard Dataverse, doi:10.7910/DVN/LCCLLW (CC0; citation courtesy).")


def _s(d, k, default=""):
    return d[k].item() if k in d.files and d[k].ndim == 0 else default


def _tracked_on_origin():
    try:
        out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/main", "data/references/"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        return set(out)
    except Exception:
        return None


def _groups(mason_files):
    """Union-find over Mason files: same video + overlapping time window, or shared v1_overlap."""
    meta = {}
    for p in sorted(REF_DIR.glob("mason_v[23]*.npz")):
        d = np.load(p, allow_pickle=True)
        meta[p.name] = (str(_s(d, "source_file")), float(d["t_start_in_video"]), float(d["t_end_in_video"]),
                        str(_s(d, "v1_overlap")))
    parent = {k: k for k in meta}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        parent.setdefault(a, a); parent.setdefault(b, b)
        parent[find(a)] = find(b)
    names = list(meta)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa, ta0, ta1, _ = meta[a]; sb, tb0, tb1, _ = meta[b]
            # v3 slow-mo windows are in video time and cover the same swing as the v2 cut they overlap
            if sa == sb and min(ta1, tb1) - max(ta0, tb0) > 0:
                union(a, b)
        v1 = meta[a][3]
        if v1:
            union(a, "v1:" + v1)
    for n in ["mason_v2_p3_s09.npz", "mason_v2_p3_s09_unmirrored.npz"]:
        if n in meta:
            pass
    # unmirrored p3_s09 is the same swing as p3_s09 (same window) -> unioned via time overlap already
    comp = {}
    for n in meta:
        comp.setdefault(find(n), []).append(n)
    gid = {}
    for members in comp.values():
        rep = sorted(m for m in members if not m.startswith("v1:"))
        label = "mason_group_" + rep[0].replace("mason_", "").replace(".npz", "")
        for m in members:
            gid[m] = label
    return gid


def _entry(p, source, group, tracked, **kw):
    d = np.load(p, allow_pickle=True)
    e = {
        "path": f"data/references/{p.name}", "source": source, "group": group,
        "license_class": str(_s(d, "license_class", "unknown")), "commercial_ok": bool(_s(d, "commercial_ok", False)),
        "handedness_file": str(_s(d, "handedness")), "mirrored": bool(_s(d, "mirrored", False)),
        "frames": int(len(d["joints"])), "dt": float(_s(d, "dt", 0.01)),
        "tempo_ratio": (None if "tempo_ratio" not in d.files else round(float(d["tempo_ratio"]), 3)),
        "on_origin_main": (None if tracked is None else f"data/references/{p.name}" in tracked),
    }
    e.update(kw)
    return e


def build_manifest():
    tracked = _tracked_on_origin()
    gid = _groups(None)
    entries = []
    # Mason v2 recommended native-left (+ the un-flipped edit) and v3 slow-mo
    for p in sorted(REF_DIR.glob("mason_v[23]*.npz")):
        d = np.load(p, allow_pickle=True)
        if not bool(_s(d, "recommended", False)) or not bool(_s(d, "commercial_ok", False)) or bool(_s(d, "partial", False)):
            continue
        slow = bool(_s(d, "slow_motion", False))
        native = bool(_s(d, "native_footage", True))
        mir = bool(_s(d, "mirrored", False))
        if mir and p.name != "mason_v2_p3_s09_unmirrored.npz":
            continue
        if str(_s(d, "handedness")) != "left":
            continue
        variant = "slowmo" if slow else ("flip_edit_unmirrored" if not native else "native")
        entries.append(_entry(p, "mason", gid[p.name], tracked, view=str(_s(d, "view")),
                              quality=round(float(d["quality_score"]), 4), variant=variant,
                              handedness="left", native_footage=native, effective_mirrored_on_load=False,
                              ack=None, note=("slow-mo: video-time axis stretched; excluded from default sampling" if slow else
                                              "caption-flagged flipped edit of a left-handed swing, un-mirrored back to left" if not native else "")))
    # MultiSense mirrored (left)
    for p in sorted(REF_DIR.glob("multisense_*_mirrored.npz")):
        d = np.load(p, allow_pickle=True)
        nflag = len(d["qc_flags"]) if "qc_flags" in d.files else 0
        entries.append(_entry(p, "multisense", "multisense_" + str(_s(d, "trial_id")), tracked, view="3d",
                              quality=round(max(0.05, 1 - 0.15 * nflag), 4), variant="mirrored", handedness="left",
                              native_footage=True, effective_mirrored_on_load=False, ack=MS_CITE,
                              club_speed_mph=round(float(_s(d, "club_speed_mph_launch_monitor", 0.0)), 1), note=""))
    # CMU subject 64: right-handed originals, mirrored at load time for the left humanoid
    for p in sorted(REF_DIR.glob("cmu_64_*.npz")):
        d = np.load(p, allow_pickle=True)
        nflag = len(d["qc_flags"]) if "qc_flags" in d.files else 0
        entries.append(_entry(p, "cmu", "cmu_" + str(_s(d, "trial_id")), tracked, view="3d",
                              quality=round(max(0.05, 1 - 0.15 * nflag), 4), variant="mirror_on_load", handedness="left",
                              native_footage=True, effective_mirrored_on_load=True, ack=CMU_ACK,
                              note="file is right-handed; loader mirrors it (data.mirror_references.mirror_dict)"))
    cfg = dict(DEFAULT_SAMPLING)
    assign_splits(entries, cfg)
    for e in entries:
        e["weight_train"] = None
    w = train_weights(entries, cfg)
    for e in entries:
        e["weight_train"] = round(w.get(e["path"], 0.0), 6)
    return {
        "version": "unified_v1",
        "base": "origin/main (impact-geometry commits a873466/09d53d3 are NOT required; no file here comes from that branch)",
        "n_entries": len(entries),
        "notes": ["handedness = effective handedness after any load-time mirroring (all left for the left humanoid)",
                  "weight_train = default weight from unified_v1_sampling.json (train split only; val weight 0)",
                  "quality for multisense/cmu is a proxy (1-0.15*n_qc_flags); Mason uses video quality_score",
                  "CMU and MultiSense carry attribution requirements: see 'ack'"],
        "entries": entries,
    }


def _h(seed, key):
    return int(hashlib.sha256(f"{seed}:{key}".encode()).hexdigest(), 16)


def assign_splits(entries, cfg):
    """Deterministic group-level split stratified by source. Whole groups move together."""
    seed = cfg["split_seed"]
    for src in sorted({e["source"] for e in entries}):
        groups = sorted({e["group"] for e in entries if e["source"] == src}, key=lambda g: _h(seed, g))
        n_val = max(cfg["min_val_per_source"].get(src, 1), int(np.ceil(cfg["val_fraction"] * len(groups))))
        # count in swings rather than groups: groups are mostly singletons; keep >= min swings
        val, count = set(), 0
        for g in groups:
            if count >= n_val:
                break
            val.add(g)
            count += sum(1 for e in entries if e["group"] == g and e["variant"] != "slowmo") or 1
        for e in entries:
            if e["source"] == src:
                e["split"] = "val" if e["group"] in val else "train"


def train_weights(entries, cfg):
    sw = cfg["source_weights"]
    mult = cfg.get("multipliers", {})
    raw = {}
    for e in entries:
        if e["split"] != "train":
            continue
        m = mult.get(e["variant"], 1.0)
        raw[e["path"]] = (max(e["quality"], 1e-6) ** cfg["quality_power"]) * m
    out = {}
    for src, tw in sw.items():
        keys = [e["path"] for e in entries if e["source"] == src and e["path"] in raw]
        tot = sum(raw[k] for k in keys)
        for k in keys:
            out[k] = tw * raw[k] / tot if tot > 0 else 0.0
    z = sum(out.values())
    return {k: v / z for k, v in out.items()} if z > 0 else out


# ---------------- loader helpers ----------------
def load_manifest(path=None):
    return json.load(open(path or MANIFEST))


def load_sampling_config(path=None):
    p = Path(path or SAMPLING)
    cfg = dict(DEFAULT_SAMPLING)
    if p.exists():
        cfg.update(json.load(open(p)))
    return cfg


def split_entries(manifest=None, split="train"):
    m = manifest or load_manifest()
    return [e for e in m["entries"] if e["split"] == split]


def iter_split(manifest=None, split="val", root=ROOT):
    for e in split_entries(manifest, split):
        yield load_ref(e, root)


def weights(manifest=None, cfg=None, split="train"):
    """Recompute normalised weights from the (possibly user-edited) config. Returns (entries, probs)."""
    m = manifest or load_manifest()
    cfg = cfg or load_sampling_config()
    ents = [dict(e) for e in m["entries"]]
    w = train_weights(ents, cfg) if split == "train" else {}
    if split != "train":
        ents = [e for e in ents if e["split"] == split]
        p = np.array([1.0] * len(ents)); return ents, p / p.sum()
    ents = [e for e in ents if e["split"] == "train" and w.get(e["path"], 0) > 0]
    p = np.array([w[e["path"]] for e in ents])
    return ents, p / p.sum()


def load_ref(entry, root=ROOT):
    """Load an entry as a ReferenceDataset-style dict (mirrors on load when flagged)."""
    path = Path(root) / entry["path"]
    d = {k: v for k, v in np.load(path, allow_pickle=True).items()}
    if entry.get("effective_mirrored_on_load"):
        from data.mirror_references import mirror_dict
        d = mirror_dict(d, path.name)
    return {
        "path": str(path), "joints": np.asarray(d["joints"], dtype=float),
        "club_head": d["club_head"] if "club_head" in d else None,
        "dt": float(d["dt"]) if "dt" in d else 0.01, "name": path.stem + ("_mirroredload" if entry.get("effective_mirrored_on_load") else ""),
        "license_class": entry["license_class"], "commercial_ok": entry["commercial_ok"],
        "source": entry["source"], "handedness": entry["handedness"], "mirrored": bool(entry["mirrored"] or entry.get("effective_mirrored_on_load")),
        "view": entry["view"], "quality": entry["quality"], "split": entry["split"], "weight": entry["weight_train"],
        "acknowledgment": entry.get("ack"),
    }


def sample(rng, manifest=None, cfg=None, root=ROOT):
    """Draw one train reference dict using the weighted config. rng: np.random.Generator."""
    ents, p = weights(manifest, cfg)
    return load_ref(ents[int(rng.choice(len(ents), p=p))], root)


def as_reference_dataset(split="train", manifest=None, root=ROOT):
    """ReferenceDataset-compatible object (has .references/.sample()/.get_by_name/len) without globbing a dir."""
    from imitation.reference_dataset import ReferenceDataset
    ds = ReferenceDataset.__new__(ReferenceDataset)
    ds.references = [load_ref(e, root) for e in split_entries(manifest, split)]
    return ds


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["build"]); a = ap.parse_args()
    SET_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLING.exists():
        json.dump(DEFAULT_SAMPLING, open(SAMPLING, "w"), indent=2)
    m = build_manifest()
    json.dump(m, open(MANIFEST, "w"), indent=1)
    print(m["n_entries"], "entries ->", MANIFEST)


if __name__ == "__main__":
    main()
