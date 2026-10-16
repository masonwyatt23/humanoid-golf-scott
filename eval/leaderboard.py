"""
Leaderboard over every checkpoint in models/.   python -m eval.leaderboard [--episodes 50] [--seed 4000] [--force]

* Identical files (same md5) are evaluated once; all names are listed.
* Each model uses its own training config: results/train_<name>.json (any alias of that md5),
  else KNOWN_CONFIGS below (models with no JSON; config taken from the training command line).
* Caching: results/leaderboard_cache.json keyed by md5 + env fingerprint (md5 of
  env/humanoid_golf_env.py + env/models/*.xml). Evaluated md5s are skipped unless the env changed or --force.
* results/leaderboard_history.json keeps every evaluation ever made (incl. seeded pre-v2-physics results).
* Contact regression: a (checkpoint, mode) whose contact rate is lower than the best contact rate of
  any EARLIER-trained checkpoint (by model file mtime / history order) in the same mode is flagged.
* DTW: mean joint-trajectory DTW (rad) vs every data/references/*_swing.npz (incl. mason_swing.npz if present).
  Non-Scott reference columns are pure reference-style distances.
"""
import argparse, hashlib, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
ENV_KEYS = ["curriculum", "pin_torso", "address_pose", "torque_scale", "randomize_reset", "forward_reward",
            "carry_reward", "ball_damping", "action_smoothing", "shoulder_range_deg"]
# no results/train_*.json exist for these; configs from the launch command lines seen in `ps` / logs
KNOWN_CONFIGS = {
    "ppo_scott_baseline": dict(steps=30000, env={}, source="launch cmd `--timesteps 30000 --tag _baseline` (default env); no train JSON"),
    "ppo_scott_curr": dict(steps=30000, env=dict(curriculum=True, pin_torso=True, address_pose="fixed", torque_scale=3.0),
                           source="launch cmd `--curriculum --pin_torso --address_pose fixed --torque_scale 3 --tag _curr`; no train JSON"),
}
# earlier evaluations (my own runs, seeds 3000-3049, 50 eps) under the PRE-v2 physics env
SEED_HISTORY = [
    dict(md5="79f83863b227a1267fbdcab08642473f", names=["ppo_scott(30k, old)", "ppo_scott_prev_backup"], steps=30000, order=1,
         env_fingerprint="pre-v2-physics", modes={"deterministic": {"contact_rate": 1.0, "mean_distance": 1.92}, "stochastic": {"contact_rate": 0.18, "mean_distance": 2.65}}),
    dict(md5="90b069adbd3d5c4693692032d49806a3", names=["ppo_scott_final2", "ppo_scott(60k)"], steps=60000, order=2,
         env_fingerprint="pre-v2-physics", modes={"deterministic": {"contact_rate": 0.98, "mean_distance": 2.71}, "stochastic": {"contact_rate": 0.52, "mean_distance": 2.74}}),
]


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def env_fingerprint():
    h = hashlib.md5()
    for p in [ROOT / "env/humanoid_golf_env.py", *sorted((ROOT / "env/models").glob("*.xml"))]:
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def discover():
    groups = {}
    for z in sorted((ROOT / "models").glob("*.zip"), key=lambda p: p.stat().st_mtime):
        g = groups.setdefault(md5(z), {"names": [], "mtime": z.stat().st_mtime})
        g["names"].append(z.stem)
    j = RES / f"{SCRIPTED_SRC}.json"
    if j.exists():
        groups["scripted-" + SCRIPTED_SRC] = {"names": [SCRIPTED], "mtime": j.stat().st_mtime - 1, "scripted": True}
    return groups


SCRIPTED = "scripted_baseline"   # pseudo-checkpoint: ResidualGolfEnv with the LADDER run's exact config and a ZERO residual action
SCRIPTED_SRC = "ppo_resid_v3_ladder_s0"


def config_for(names):
    for n in names:                       # residual-PPO models: exact env flags from results/<name>.json "args"
        j = RES / f"{n}.json"
        if n.startswith("ppo_resid") and j.exists():
            from eval.env_factory import resid_kw_from_args
            args = json.loads(j.read_text())["args"]
            assert args.get("name", n) == n, f"{j} args.name mismatch"
            note = f"results/{j.name} args" + ("" if "ball_dz" in args else "; ball_dz ABSENT in args (flag predates run) -> env default 0.0 used, true training value UNKNOWN")
            return args["timesteps"], resid_kw_from_args(args), note
    for n in names:                       # prefer a JSON that exists for any alias
        j = RES / f"train_{n.replace('ppo_', '', 1)}.json"
        if j.exists():
            d = json.loads(j.read_text())
            return d["timesteps"], {k: d[k] for k in ENV_KEYS if k in d}, f"results/{j.name}"
    for n in names:
        if n in KNOWN_CONFIGS:
            k = KNOWN_CONFIGS[n]
            return k["steps"], k["env"], k["source"]
    return None, None, "UNKNOWN"


def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=50); ap.add_argument("--seed", type=int, default=4000)
    ap.add_argument("--force", action="store_true"); a = ap.parse_args()
    import eval.dispersion_report as dr
    refs = sorted(p.name[:-len("_swing.npz")] for p in (ROOT / "data/references").glob("*_swing.npz"))
    dr.REFS = refs
    fp = env_fingerprint()
    cache = load(RES / "leaderboard_cache.json", {})
    hist = load(RES / "leaderboard_history.json", {"entries": SEED_HISTORY})
    groups = discover()
    for h, g in groups.items():
        key = f"{h}:{fp}:{a.episodes}:{a.seed}:s7"
        if key in cache and not a.force:
            print("skip (cached)", g["names"]); continue
        if g.get("scripted"):
            from eval.env_factory import resid_kw_from_args
            steps, kw, src = 0, resid_kw_from_args(json.loads((RES / f"{SCRIPTED_SRC}.json").read_text())["args"]), f"zero-residual action with results/{SCRIPTED_SRC}.json args"
        else:
            steps, kw, src = config_for(g["names"])
        if kw is None:
            cache[key] = {"md5": h, "names": g["names"], "config_source": "UNKNOWN", "error": "training config unknown; not evaluated"}
            continue
        print("evaluating", g["names"], kw)
        modes = {}
        for det in (True, False):
            try:
                d, _ = dr.run(g["names"][0], kw, a.episodes, a.seed, det, scripted=bool(g.get("scripted")))
            except Exception as e:
                d = {"error": f"{type(e).__name__}: {e}"}
            modes["deterministic" if det else "stochastic"] = d
        if any("error" in v for v in modes.values()):
            print("ERROR (not cached):", g["names"], {m: v.get("error") for m, v in modes.items()}); continue
        cache[key] = {"md5": h, "names": g["names"], "steps": steps, "env_kwargs": kw, "config_source": src,
                      "env_fingerprint": fp, "episodes": a.episodes, "seed_base": a.seed, "mtime": g["mtime"], "modes": modes, "scripted": bool(g.get("scripted")),
                      "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
        if not g.get("scripted") and not any(e["md5"] == h and e.get("env_fingerprint") == fp for e in hist["entries"]):
            hist["entries"].append({"md5": h, "names": g["names"], "steps": steps, "order": g["mtime"], "env_fingerprint": fp,
                                    "modes": {m: {"contact_rate": v.get("contact_rate"), "mean_distance": v.get("mean_distance")} for m, v in modes.items()}})
    (RES / "leaderboard_cache.json").write_text(json.dumps(cache, indent=1))
    (RES / "leaderboard_history.json").write_text(json.dumps(hist, indent=1))

    cur = sorted([c for k, c in cache.items() if k.split(":")[1] == fp and k.split(":")[2:] == [str(a.episodes), str(a.seed), "s7"]],
                 key=lambda c: c.get("mtime", 0))
    # contact regressions vs best EARLIER-trained checkpoint (any env fingerprint, from history)
    flags = []
    for c in cur:
        if c.get("scripted"): continue
        for m, v in c.get("modes", {}).items():
            if "contact_rate" not in v: continue
            prev = [(e["modes"][m]["contact_rate"], e["names"][0]) for e in hist["entries"]
                    if e["md5"] != c["md5"] and e["order"] < c["mtime"] and e["modes"].get(m, {}).get("contact_rate") is not None]
            if prev:
                best, who = max(prev)
                v["best_prev_contact"], v["best_prev_model"] = best, who
                if v["contact_rate"] < best - 1e-9:
                    flags.append(f"{'/'.join(c['names'])} [{m}]: contact {v['contact_rate']*100:.0f}% < best previous {best*100:.0f}% ({who})")
    def score(c):
        ms = [v for v in c.get("modes", {}).values() if "contact_rate" in v]
        if not ms: return (-1, -1)
        return (sum(v["contact_rate"] for v in ms) / len(ms), sum(v["mean_carry"] for v in ms) / len(ms))
    ranked_all = sorted(cur, key=score, reverse=True)           # incl. scripted baseline
    ranked = [c for c in ranked_all if not c.get("scripted")]   # trained checkpoints only
    best_line = ("**Current best model: " + " / ".join(ranked[0]["names"]) + f"** ({ranked[0]['steps']} steps) - mean true contact over det+stoch {score(ranked[0])[0]*100:.0f}%, mean carry {score(ranked[0])[1]:.3f} m."
                 if ranked else "No evaluated models.")
    out = {"env_fingerprint": fp, "episodes": a.episodes, "seed_base": a.seed, "references": refs,
           "lateral_threshold_m": 0.5, "models": cur, "contact_regressions": flags, "best_model": (ranked[0]["names"] if ranked else None), "best_overall": (ranked_all[0]["names"] if ranked_all else None),
           "ranking": ["/".join(c["names"]) for c in ranked], "ranking_incl_scripted": ["/".join(c["names"]) for c in ranked_all],
           "history": hist["entries"]}
    (RES / "leaderboard.json").write_text(json.dumps(out, indent=1))
    if ranked:
        bv = [v for v in ranked[0]["modes"].values() if "peak_club_speed_max" in v]
        if bv:
            mx = max(v["peak_club_speed_max"] for v in bv)
            best_line += (f" Peak club-head speed (best single swing over det+stoch): {mx:.2f} m/s = {mx*2.23694:.1f} mph = {mx/53.64*100:.1f}% of the 120 mph (53.64 m/s) target.")
    rank_txt = ("Ranking criterion: (1) true club-ball contact rate averaged over deterministic and stochastic modes, higher first; "
                "(2) ties broken by mean carry (m, averaged over both modes, mean over all episodes). Distance is not used.")
    rk = " > ".join("/".join(c["names"][:1]) for c in ranked_all)
    if ranked_all and ranked_all[0].get("scripted"):
        best_line += f" **Best overall (incl. scripted, no-learning baseline): {SCRIPTED}** - mean contact {score(ranked_all[0])[0]*100:.0f}%, mean carry {score(ranked_all[0])[1]:.3f} m (no trained checkpoint beats it)."
    elif ranked_all:
        best_line += f" Best overall incl. scripted baseline: {' / '.join(ranked_all[0]['names'])}."
    L = ["# Leaderboard", "", best_line, "", rank_txt, "", f"Full ranking (scripted baseline included): {rk}", "",
         "Peak club speed = max club_head linear speed over every physics substep of the swing, measured per episode (mean / max over episodes); mph = m/s x 2.23694; % of target = peak / 53.64 m/s (120 mph). "
         "Impact club speed = club_head linear speed at first club-ball contact; smash factor = peak ball speed / impact club speed (contact shots with club speed > 0.05 m/s, averaged).", "",
         f"Current env fingerprint `{fp}` (env + XML hash). {a.episodes} episodes, seeds {a.seed}..{a.seed+a.episodes-1}. "
         "+y = left, miss = |final y| > 0.5 m. Distance = final ball x (total); carry = x at landing after flight, 0 if never landed (mean over all episodes). "
         "DTW = mean joint-trajectory DTW (rad) to each reference; non-Scott columns are pure reference-style distances.", "",
         "| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | DTW Mason best (11j / upper5) | " + " | ".join(f"DTW {r}" for r in refs) + " |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|" + "---|" * len(refs)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            nm = "<br>".join(c["names"])
            if "error" in v:
                L.append(f"| {nm} | {c['steps']} | {m} | ERROR: {v['error']} |"); continue
            L.append(f"| {nm} | {c['steps']} | {m[:5]} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['mean_peak_ball_speed']:.2f} | {v['impact_club_speed_mean']:.2f} | {v['smash_factor_mean']:.2f} (n={v['smash_factor_n']}) | {'n/a' if v['peak_club_speed_mean'] != v['peak_club_speed_mean'] else format(v['peak_club_speed_mean'],'.2f') + ' / ' + format(v['peak_club_speed_max'],'.2f')} | {'n/a' if v['peak_club_mph_mean'] != v['peak_club_mph_mean'] else format(v['peak_club_mph_mean'],'.1f') + ' / ' + format(v['peak_club_mph_max'],'.1f')} | {'n/a' if v['peak_club_pct_target_mean'] != v['peak_club_pct_target_mean'] else format(v['peak_club_pct_target_mean'],'.1f') + '% / ' + format(v['peak_club_pct_target_max'],'.1f') + '%'}{' (' + str(v['peak_club_unstable_episodes']) + ' sim-unstable eps excluded; raw max ' + format(v['peak_club_raw_max_unstable'],'.3g') + ' m/s)' if v['peak_club_unstable_episodes'] else ''} | {v['dtw_mason'][dr.MASON_REFS[0]]['all11']['mean']:.3f} / {v['dtw_mason'][dr.MASON_REFS[0]]['upper5']['mean']:.3f} | "
                     + " | ".join(f"{v['dtw_to_reference_style_rad'][r]['mean']:.3f}" for r in refs) + " |")
    L += ["", "## Configs used (each model evaluated with its own)", ""]
    for c in cur:
        L.append(f"- **{'/'.join(c['names'])}** ({c['steps']} steps): {c['config_source']}; env = `{json.dumps(c['env_kwargs'])}`")
    for k, c in cache.items():
        if k.split(":")[1] == fp and c.get("config_source") == "UNKNOWN": L.append(f"- {c['names']}: training config UNKNOWN, not evaluated.")
    L += ["", "## DTW vs MIRRORED Mason video references (mirrored=true copies of all 8 refs in docs/REFERENCE_PATHS.md; mean DTW rad: all 11 joints / upper-body 5 joints)", "",
          "**CAVEAT: Mason references are 2D-proxy joint angles from MediaPipe landmarks of a single phone view (unknown angle), screen-recorded at ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak. Scores are INDICATIVE ONLY and say nothing about swing quality.**", "",
          "Mapping: `*_mirrored.npz` (mirrored=True, left-handed-consistent per docs) `joints` (degrees, 11 cols = process_video.JOINT_NAMES) -> radians; only `valid_mask` frames kept; policy trajectory = those 11 joints read BY NAME from qpos each env step (works for both the original and v3 models; joint sign conventions between video angles and MuJoCo joints are NOT calibrated; right-handed policies vs left-handed-consistent refs may be penalised); length-normalised DTW (tempo-tolerant). 'upper5' = joint cols 0-4 only (leg cols 5-10 unreliable). q = reference quality_score from the docs.", "",
          "| Model(s) | Mode | " + " | ".join(r.replace("mason_swing_", "").replace("_refined", "") + " (q=" + str(dr.MASON_QUALITY[r]) + ")" for r in dr.MASON_REFS) + " |",
          "|---|---|" + "---|" * len(dr.MASON_REFS)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            if "dtw_mason" not in v: continue
            L.append("| " + "<br>".join(c["names"]) + " | " + m[:5] + " | " + " | ".join(format(v["dtw_mason"][r]["all11"]["mean"], ".3f") + " / " + format(v["dtw_mason"][r]["upper5"]["mean"], ".3f") for r in dr.MASON_REFS) + " |")
    L += ["", "## Contact regressions (vs best earlier-trained checkpoint, same mode)", ""] + ([f"- {f}" for f in flags] or ["- none"])
    L += ["", "## History (all evaluated checkpoints)", "", "| Checkpoint(s) | Steps | Env | Det contact | Stoch contact |", "|---|---|---|---|---|"]
    for e in sorted(hist["entries"], key=lambda e: e["order"]):
        f = lambda m: "n/a" if e["modes"].get(m, {}).get("contact_rate") is None else f"{e['modes'][m]['contact_rate']*100:.0f}%"
        L.append(f"| {', '.join(e['names'])} | {e['steps']} | {e['env_fingerprint']} | {f('deterministic')} | {f('stochastic')} |")
    # dispersion detail for the ladder model and the scripted baseline
    det_rows = [c for c in cur if c.get("scripted") or "ppo_resid_v3_ladder_s0" in c["names"]]
    D = ["# Dispersion detail: ladder model and scripted baseline", "",
         f"{a.episodes} episodes/mode, seeds {a.seed}..{a.seed+a.episodes-1}; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).", "",
         "| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['std_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_max_ball_x']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['mean_y']:+.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['peak_club_speed_mean']:.2f} / {v['peak_club_speed_max']:.2f} | {v['peak_club_mph_mean']:.1f} / {v['peak_club_mph_max']:.1f} | {v['peak_club_pct_target_max']:.1f}% | {v['peak_club_unstable_episodes']} |")
    D += ["", "DTW to mirrored Mason refs (mean rad, all11 / upper5):", "", "| Model | Mode | " + " | ".join(dr.MASON_REFS) + " |", "|---|---|" + "---|" * len(dr.MASON_REFS)]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | " + " | ".join(format(v['dtw_mason'][r]['all11']['mean'], '.3f') + " / " + format(v['dtw_mason'][r]['upper5']['mean'], '.3f') for r in dr.MASON_REFS) + " |")
    (RES / "dispersion_ladder_scripted.md").write_text("\n".join(D) + "\n")
    (RES / "dispersion_ladder_scripted.json").write_text(json.dumps([{k: c[k] for k in ("names", "steps", "config_source", "env_kwargs", "modes")} for c in det_rows], indent=1))
    (RES / "leaderboard.md").write_text("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()
