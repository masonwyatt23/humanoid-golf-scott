"""DTW style distance of key models to the unified_v1 reference set, VAL split only (never trained on), grouped by source.

  python -m eval.unified_style [--episodes 20] [--seed 4000]      -> results/unified_val_style.{md,json}

Rollouts/trajectories come from eval.swing_compare.collect (deterministic policy, evaluator protocol; control-step joint angles of the 11 reference columns, radians).
References: data/unified_refset.py load_ref(entry) for entries with split=='val' in data/reference_sets/unified_v1.json (joints in degrees -> radians; Mason native left-handed,
MultiSense mirrored files, CMU mirrored on load via effective_mirrored_on_load). Distance = eval.style_match.dtw_distance (mean per aligned frame, rad; all 11 joints and upper-body
cols 0-4). Per source: mean over that source's val refs of the per-reference mean over episodes. Lower = closer.

CAVEATS (labelled, not hidden)
  * Val split is tiny (3 Mason, 6 MultiSense, 2 CMU swings) - differences of a few hundredths rad are within what a different split would change.
  * Reference joint angles are proxies: Mason = single-view MediaPipe 2D angles; MultiSense = IMU mocap, different protocol, 89-103 mph recreational/amateur right-handers mirrored; CMU = slow
    recreational mocap (tempo ~1.8 vs sim ~5). None is retargeted to the MuJoCo humanoid; column sign/zero conventions are not calibrated, so absolute values are indicative only.
  * DTW is tempo-invariant by design; these numbers say nothing about tempo (see results/swing_compare.md for tempo).
  * Earlier results/leaderboard DTW numbers used the native mason_v2 'recommended' set, not this split; the two are not directly comparable.
  * The impact-geometry targets (data/references/mason_impact_geometry_targets.json, schema mason_impact_geometry_targets/v1) are diagnostic hand-path proxies, present in the tree; not used here (needs hand-height/torso-length model outputs the sim run does not record).
"""
import argparse, json, time
from pathlib import Path
import numpy as np
from data.unified_refset import load_manifest, load_ref
from eval.style_match import dtw_distance, UPPER_COLS
from eval.swing_compare import collect, DEFAULT_MODELS

ROOT = Path(__file__).resolve().parent.parent; RES = ROOT / "results"


def val_refs():
    out = []
    for e in load_manifest()["entries"]:
        if e["split"] != "val": continue
        r = load_ref(e); j = np.deg2rad(np.asarray(r["joints"], float)); j = j[np.all(np.isfinite(j), axis=1)]
        out.append(dict(path=e["path"], source=e["source"], mirrored_on_load=bool(e["effective_mirrored_on_load"]), handedness=e["handedness"], frames=len(j), joints=j))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--episodes", type=int, default=20); ap.add_argument("--seed", type=int, default=4000)
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS); a = ap.parse_args()
    refs = val_refs(); res = {"generated": time.strftime("%Y-%m-%d %H:%M"), "episodes": a.episodes, "seed": a.seed, "split": "val",
                              "refs": [{k: v for k, v in r.items() if k != "joints"} for r in refs], "models": {}}
    for n in a.models:
        try: r = collect(n, a.episodes, a.seed, True)
        except Exception as e: print("SKIP", n, e); continue
        per = []
        for ref in refs:
            d11 = [dtw_distance(t, ref["joints"]) for t in r["trajs"]]; d5 = [dtw_distance(t[:, UPPER_COLS], ref["joints"][:, UPPER_COLS]) for t in r["trajs"]]
            per.append(dict(path=ref["path"], source=ref["source"], all11=float(np.mean(d11)), upper5=float(np.mean(d5))))
        by = {}
        for s in sorted({p["source"] for p in per}):
            q = [p for p in per if p["source"] == s]
            by[s] = dict(n_refs=len(q), all11=float(np.mean([p["all11"] for p in q])), upper5=float(np.mean([p["upper5"] for p in q])),
                         best_ref=min(q, key=lambda p: p["all11"])["path"])
        m = r["meta"]; res["models"][n] = dict(label=m["label"], scripted=m["scripted"], hypothetical_actuators=m["hypothetical_actuators"], by_source=by, per_ref=per)
        print("done", n, {s: round(v["all11"], 3) for s, v in by.items()})
    (RES / "unified_val_style.json").write_text(json.dumps(res, indent=1))
    srcs = ["mason", "multisense", "cmu"]
    L = ["# Style distance (DTW, rad) to unified_v1 VAL split", "",
         f"Val refs: {sum(r['source']=='mason' for r in refs)} Mason (native left), {sum(r['source']=='multisense' for r in refs)} MultiSense (mirrored), {sum(r['source']=='cmu' for r in refs)} CMU (mirrored on load). {a.episodes} deterministic episodes/model, seeds {a.seed}+. Lower = closer. Cells: all 11 joints / upper-body 5 joints.", "",
         "**Caveats:** tiny val split; reference angles are uncalibrated proxies (Mason 2D MediaPipe; MultiSense amateur IMU; CMU slow recreational) not retargeted to the humanoid; DTW ignores tempo; not comparable with the earlier leaderboard DTW (different ref set); all sim rows use boosted actuators (force_scale 2 = HYPOTHETICAL ACTUATORS). Scripted rows are NOT learned. Magnitudes ~2 rad (mean per-frame distance over 11 joints) mean every row is FAR from every reference in joint space (the leaderboard's native-Mason DTW for ppo_v3flt_yaw_s31 is 2.34 on its own set, same order); learned and scripted v3 rows are within 0.003 rad of each other, i.e. no measurable style learning; an3/loft-7 rows are 'closer' mainly because their trajectories differ, not because they hit better.", "",
         "| Model | Kind | " + " | ".join(srcs) + " |", "|---|---|" + "---|" * len(srcs)]
    for n, m in res["models"].items():
        L.append(f"| {n} | {'SCRIPTED (not learned)' if m['scripted'] else 'LEARNED'} | " + " | ".join(f"{m['by_source'][s]['all11']:.3f} / {m['by_source'][s]['upper5']:.3f}" if s in m["by_source"] else "-" for s in srcs) + " |")
    L += ["", "## Per reference (all11)", "", "| Model | " + " | ".join(Path(r["path"]).stem for r in refs) + " |", "|---|" + "---|" * len(refs)]
    for n, m in res["models"].items():
        L.append(f"| {n} | " + " | ".join(f"{p['all11']:.3f}" for p in m["per_ref"]) + " |")
    (RES / "unified_val_style.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
