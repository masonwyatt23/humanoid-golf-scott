"""Recompute track_score with the Trainer's opt-in track_arm='lead' (commit 3b60369: Mason shoulder reference -> env left_shoulder_pitch, qtraj col 5), SEPARATE from the legacy numbers.
python -m eval.track_score_lead  ->  results/track_score_lead.{json,md}
Same protocol as eval.leaderboard.track_score_run (det policy, 10 episodes, seeds 4000+, the run's own track_set/weight). Only the SHOULDER part is remapped; no lead-wrist joint exists so the wrist
part (still the trail wrist) is reported but EXCLUDED from the lead mean (mean_sh_yaw). Legacy results/leaderboard.json track_score is untouched (VOID/UNVERIFIED)."""
import json, sys
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import eval.leaderboard as L

def main():
    # --new-only: only models NOT already in results/track_score_lead.json; written to results/track_score_lead_new.{json,md} (existing file untouched)
    new_only = "--new-only" in sys.argv; stem = "track_score_lead_new" if new_only else "track_score_lead"
    done = set(json.load(open(ROOT / "results/track_score_lead.json"))["models"]) if new_only else set()
    lb = json.load(open(ROOT / "results/leaderboard.json")); out = {}
    for c in lb["models"]:
        n = c["names"][0]; ts = c.get("track_score")
        if n in done: continue
        if not (isinstance(ts, dict) and ts.get("defined") and "parts" in ts): continue
        jj = ROOT / "results" / f"{n}.json"
        ek = json.load(open(jj)).get("env_kwargs_full") if jj.exists() else None
        if not ek: continue
        kw = dict(c["env_kwargs"], track_set=ek["track_set"], track_weight=float(ek["track_weight"]))
        try:
            res = {}
            for arm in ("legacy", "lead"):
                res[arm] = L.track_score_run(n, dict(kw, track_arm=arm), 10, 4000)
        except Exception as e:
            print(n, "ERR", e, flush=True); continue
        p = res["lead"]["parts"]; leg = res["legacy"]["parts"]
        out[n] = dict(legacy_parts=leg, lead_parts=p, legacy_mean=res["legacy"]["mean"], lead_mean_sh_yaw=float(np.mean([p["sh"], p["yaw"]])) if "sh" in p and "yaw" in p else None,
                      leaderboard_legacy_mean=ts["mean"], episodes=10)
        print(n, {k: round(v, 3) for k, v in p.items()}, "legacy sh", round(leg.get("sh", float("nan")), 3), flush=True)
    json.dump(dict(label="track_score recomputed with track_arm='lead' (shoulder -> left_shoulder_pitch); wrist untracked (excluded); separate from legacy VOID numbers", models=out), open(ROOT / f"results/{stem}.json", "w"), indent=1)
    md = ["# track_score with track_arm=lead (SEPARATE from legacy; shoulder only, wrist excluded)", "",
          "Trainer opt-in `track_arm='lead'` (commit 3b60369): Mason shoulder reference mapped to env left_shoulder_pitch. No lead-wrist joint exists, so the wrist part is not remapped and is excluded from `mean(sh,yaw)`. 10 det episodes, seeds 4000+, N small. Legacy columns in leaderboard.md stay VOID/UNVERIFIED.", "",
          "| model | legacy sh | lead sh | yaw | legacy wr (trail wrist, not remapped) | lead mean(sh,yaw) | legacy mean(sh,yaw,wr) |", "|---|---|---|---|---|---|---|"]
    for n, r in out.items():
        lp, ld = r["legacy_parts"], r["lead_parts"]
        md.append(f"| {n} | {lp.get('sh', float('nan')):.3f} | {ld.get('sh', float('nan')):.3f} | {ld.get('yaw', float('nan')):.3f} | {ld.get('wr', float('nan')):.3f} | {r['lead_mean_sh_yaw']:.3f} | {r['legacy_mean']:.3f} |")
    open(ROOT / f"results/{stem}.md", "w").write("\n".join(md) + "\n")

if __name__ == "__main__": main()
