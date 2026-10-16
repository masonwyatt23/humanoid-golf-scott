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
    for p in [ROOT / "env/humanoid_golf_env.py", ROOT / "env/residual_golf_env.py", ROOT / "env/ball_flight_analytic.py", *sorted((ROOT / "env/models").glob("*.xml"))]:
        if not p.exists(): continue
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
    if (RES / "ppo_resid_v3_left_an10_s8.json").exists():   # trainer's scripted config (TRAINING_NOTES: ball_x 0.422, noise 0.005, loft 7, left; eval/eval_scripted_cfg.py base)
        groups["scripted-bx0422"] = {"names": [SCRIPTED_BX], "mtime": j.stat().st_mtime - 0.5, "scripted": True, "scripted_cfg": "bx0422"}
    return groups


SCRIPTED = "scripted_baseline[ladder cfg: right, loft 6, default ball_x]"   # pseudo-checkpoint: ResidualGolfEnv with the LADDER run's exact config and a ZERO residual action
SCRIPTED_SRC = "ppo_resid_v3_ladder_s0"
SCRIPTED_BX = "scripted_baseline[trainer cfg: left, loft 7, ball_x 0.422 +-5mm]"


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
        key = f"{h}:{fp}:{a.episodes}:{a.seed}:s10"
        if key in cache and not a.force:
            print("skip (cached)", g["names"]); continue
        if g.get("scripted_cfg") == "bx0422":
            import eval.eval_scripted_cfg as esc
            steps, kw, src = 0, dict(esc.base, ball_x=0.422, ball_x_noise=0.005, loft_deg=7.0), "zero-residual action; trainer config from TRAINING_NOTES / eval/eval_scripted_cfg.py base + ball_x 0.422, ball_x_noise 0.005, loft 7, left"
        elif g.get("scripted"):
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

    cur = sorted([c for k, c in cache.items() if k.split(":")[1] == fp and k.split(":")[2:] == [str(a.episodes), str(a.seed), "s10"]],
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
    def v2m(v):
        a = [v['dtw_mason_v2'][r]['all11']['mean'] for r in v['dtw_mason_v2']]; u = [v['dtw_mason_v2'][r]['upper5']['mean'] for r in v['dtw_mason_v2']]
        return f"{sum(a)/len(a):.3f} / {sum(u)/len(u):.3f}"

    def score(c):
        ms = [v for v in c.get("modes", {}).values() if "contact_rate" in v]
        if not ms: return (-1, -1)
        return (sum(v["contact_rate"] for v in ms) / len(ms), sum(v["mean_carry"] for v in ms) / len(ms))
    ranked_all = sorted(cur, key=score, reverse=True)           # incl. scripted baseline
    ranked = [c for c in ranked_all if not c.get("scripted")]   # trained checkpoints only
    best_line = ("**Current best model: " + " / ".join(ranked[0]["names"]) + f"** ({ranked[0]['steps']} steps) - mean true contact over det+stoch {score(ranked[0])[0]*100:.0f}%, mean carry {score(ranked[0])[1]:.3f} m."
                 if ranked else "No evaluated models.")
    left = [c for c in ranked if c.get("env_kwargs", {}).get("handedness") == "left"]
    Q_CARRY, Q_LAT, Q_ELEV = 30.0, 2.73, 5.0
    def qual(c):
        v = c.get("modes", {}).get("deterministic", {})
        if "contact_rate" not in v: return None
        checks = {"contact==100% (det and stoch)": all(m.get("contact_rate", 0) >= 1.0 for m in c["modes"].values()),
                  f"mean carry >= {Q_CARRY:g} m (det)": v["mean_carry"] >= Q_CARRY,
                  f"lateral std <= {Q_LAT:g} m (det)": v["lateral_std"] <= Q_LAT,
                  f"mean launch elev >= {Q_ELEV:g} deg, not flat (det)": not v["launch_flat_flag"]}
        return checks
    qrows = [(c, qual(c)) for c in ranked if qual(c)]
    qualifying = [c for c, q in qrows if all(q.values())]
    qualifying.sort(key=score, reverse=True)
    out = {"env_fingerprint": fp, "episodes": a.episodes, "seed_base": a.seed, "references": refs,
           "lateral_threshold_m": 0.5, "models": cur, "contact_regressions": flags, "best_model": (ranked[0]["names"] if ranked else None), "best_overall": (ranked_all[0]["names"] if ranked_all else None), "best_left": (left[0]["names"] if left else None), "qualifying": [c["names"] for c in qualifying], "best_qualifying": (qualifying[0]["names"] if qualifying else None),
           "qualify_criterion": {"carry_m_min": Q_CARRY, "lateral_std_m_max": Q_LAT, "launch_elev_deg_min": Q_ELEV, "contact": "100% in both modes", "mode": "deterministic for carry/lateral/launch"},
           "ranking": ["/".join(c["names"]) for c in ranked], "ranking_incl_scripted": ["/".join(c["names"]) for c in ranked_all],
           "history": hist["entries"]}
    (RES / "leaderboard.json").write_text(json.dumps(out, indent=1))
    if ranked:
        bv = [v for v in ranked[0]["modes"].values() if "peak_club_speed_max" in v]
        if bv:
            mx = max(v["peak_club_speed_max"] for v in bv)
            best_line += (f" Peak club-head speed (best single swing over det+stoch): {mx:.2f} m/s = {mx*2.23694:.1f} mph = {mx/53.64*100:.1f}% of the 120 mph (53.64 m/s) target.")
    if left:
        best_line += f" **Best left-handed model: {' / '.join(left[0]['names'])}** (mean contact {score(left[0])[0]*100:.0f}%, mean carry {score(left[0])[1]:.2f} m, physics protocol)."
    best_line += (f" **Best model meeting the showcase criterion (real carry AND tight lateral AND not-flat launch AND 100% contact; see below): {' / '.join(qualifying[0]['names'])}.**"
                  if qualifying else " **NO model meets the showcase criterion (carry >= %g m, lateral std <= %g m, launch elev >= %g deg, contact 100%%); see qualification table.**" % (Q_CARRY, Q_LAT, Q_ELEV))
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
         "| Model(s) | Steps | Mode | Contact | Mean dist (m) | Max dist (m) | Mean carry (m) | Landed | Lateral std (m) | Left | Right | Peak ball spd (m/s) | Impact club spd (m/s) | Smash | Peak club spd mean/max (m/s) | Peak club mph mean/max | % of 120 mph mean/max | Launch elev mean deg (std) [flat?] | DTW native Mason v2, mean of 11 refs (11j / upper5) | " + " | ".join(f"DTW {r}" for r in refs) + " |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|" + "---|" * len(refs)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            nm = "<br>".join(c["names"])
            if "error" in v:
                L.append(f"| {nm} | {c['steps']} | {m} | ERROR: {v['error']} |"); continue
            L.append(f"| {nm} | {c['steps']} | {m[:5]} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['mean_peak_ball_speed']:.2f} | {v['impact_club_speed_mean']:.2f} | {v['smash_factor_mean']:.2f} (n={v['smash_factor_n']}) | {'n/a' if v['peak_club_speed_mean'] != v['peak_club_speed_mean'] else format(v['peak_club_speed_mean'],'.2f') + ' / ' + format(v['peak_club_speed_max'],'.2f')} | {'n/a' if v['peak_club_mph_mean'] != v['peak_club_mph_mean'] else format(v['peak_club_mph_mean'],'.1f') + ' / ' + format(v['peak_club_mph_max'],'.1f')} | {'n/a' if v['peak_club_pct_target_mean'] != v['peak_club_pct_target_mean'] else format(v['peak_club_pct_target_mean'],'.1f') + '% / ' + format(v['peak_club_pct_target_max'],'.1f') + '%'}{' (' + str(v['peak_club_unstable_episodes']) + ' sim-unstable eps excluded; raw max ' + format(v['peak_club_raw_max_unstable'],'.3g') + ' m/s)' if v['peak_club_unstable_episodes'] else ''} | {v['launch_elev_mean_deg']:.1f} ({v['launch_elev_std_deg']:.1f}){' FLAT' if v['launch_flat_flag'] else ''} | {v2m(v)} | "
                     + " | ".join(f"{v['dtw_to_reference_style_rad'][r]['mean']:.3f}" for r in refs) + " |")
    L += ["", "## Configs used (each model evaluated with its own)", ""]
    for c in cur:
        L.append(f"- **{'/'.join(c['names'])}** ({c['steps']} steps): {c['config_source']}; env = `{json.dumps(c['env_kwargs'])}`")
    for k, c in cache.items():
        if k.split(":")[1] == fp and c.get("config_source") == "UNKNOWN": L.append(f"- {c['names']}: training config UNKNOWN, not evaluated.")
    Qs = ["", "## Showcase qualification criterion", "",
          f"A model qualifies only if ALL hold (deterministic mode unless stated, physics protocol, 50 eps): true contact 100% in both modes; mean carry >= {Q_CARRY:g} m (documented threshold; the scripted baseline carries ~38 m on this protocol); lateral std <= {Q_LAT:g} m (the trainer's gate baseline); mean launch elevation >= {Q_ELEV:g} deg (ball velocity at the end of club-ball contact; rules out the flat/negative-launch exploit). Among qualifiers: highest mean carry over det+stoch.", "",
          "| Model | " + " | ".join(next(iter([q for _, q in qrows])).keys()) + " | Qualifies |", "|---|" + "---|" * (len(next(iter([q for _, q in qrows])))+1)]
    for c, q in qrows:
        Qs.append(f"| {'/'.join(c['names'])} | " + " | ".join('yes' if x else 'NO' for x in q.values()) + f" | {'**YES**' if all(q.values()) else 'no'} |")
    Qs += ["", ("Qualifying: " + ", ".join('/'.join(c['names']) for c in qualifying)) if qualifying else "**None qualifies.**"]
    flat = [c for c in cur if any(v.get("launch_flat_flag") for v in c.get("modes", {}).values())]
    Qs += ["", "Flat/negative-launch flag (mean elevation < %g deg or >= 50%% of shots below it): " % Q_ELEV + (", ".join('/'.join(c['names']) + " [" + ", ".join(f"{m[:3]} {v['launch_elev_mean_deg']:.1f} deg" for m, v in c['modes'].items() if v.get('launch_flat_flag')) + "]" for c in flat) or "none")]
    L += Qs
    # trainer gate numbers next to verified ones (left-handed models)
    G = ["", "## Left-handed models: trainer gate JSON vs verified (this leaderboard, same protocol: MuJoCo physics, flight tracker, 450-step horizon, deterministic, 50 eps, seeds 4000+)", "",
         "Verified = this run. Trainer gate = `results/gate_<name>.json` (`eval.eval_gate`; gate: carry > 11.98 m AND lateral std < 2.73 m AND contact >= 99%). Trainer 'analytic' = `results/<name>.json` policy block (100 eps, analytic flight from the MuJoCo launch vector with ASSUMED backspin, episode ends 3 steps after contact) - NOT re-verified here, different protocol.", "",
         "| Model | Source | Contact | Landed | Mean carry (m) | Lateral std (m) | Peak club mph mean | Gate pass |", "|---|---|---|---|---|---|---|---|"]
    for c in cur:
        if c.get("env_kwargs", {}).get("handedness") != "left" or c.get("scripted"): continue
        nm = c["names"][0]; v = c["modes"].get("deterministic", {})
        if "contact_rate" in v:
            ok = v["mean_carry"] > 11.98 and v["lateral_std"] < 2.73 and v["contact_rate"] >= 0.99
            G.append(f"| {nm} | verified (this run, det) | {v['contact_rate']*100:.0f}% | {v['landed_fraction']*100:.0f}% | {v['mean_carry']:.2f} | {v['lateral_std']:.2f} | {v['peak_club_mph_mean']:.1f} | {'PASS' if ok else 'FAIL'} |")
        gj = RES / f"gate_{nm}.json"
        if gj.exists():
            g = json.loads(gj.read_text()).get("policy_det", {})
            G.append(f"| {nm} | trainer gate JSON (det) | {g['contact_rate']*100:.0f}% | {g['landed_fraction']*100:.0f}% | {g['mean_carry']:.2f} | {g['lateral_std']:.2f} | {g['peak_club_mph_mean']:.1f} | {'PASS' if json.loads(gj.read_text()).get('gate_pass') else 'FAIL'} |")
        tj = RES / f"{nm}.json"
        if tj.exists():
            t = json.loads(tj.read_text()).get("policy", {})
            if t: G.append(f"| {nm} | trainer analytic (100 eps) | {t['true_contact_rate']*100:.0f}% | {t['landed_fraction']*100:.0f}% | {t['mean_carry']:.2f} | {t['lateral_std']:.2f} | {t['impact_club_speed_mean_mph']:.1f} (impact) | n/a |")
    L += G
    # native Mason v2 refs
    V = ["", "## DTW vs NATIVE Mason v2 references (recommended, non-partial, license self_owned/commercial_ok; mean DTW rad: all 11 joints / upper-body 5)", "",
         "**CAVEATS: 2D-proxy joint angles from single-view MediaPipe, screen-recorded ~30 fps (tempo +-15%), not retargeted to the MuJoCo humanoid, no club data, leg joints weak; native left-handed footage, `right_*` columns = anatomical right = LEAD arm of a left-hander, whereas the env's `right_*` joints are the swinging arm of its own model (mapping/sign conventions NOT calibrated). Indicative only. MultiSense (right-handed, CC0, different protocol) deliberately NOT scored here.**", "",
         "Refs: " + ", ".join(f"`{r.replace('mason_v2_','')}` (q={dr.MASON_V2_INFO[r]['quality']}, {dr.MASON_V2_INFO[r]['view']}, mirrored={dr.MASON_V2_INFO[r]['mirrored']})" for r in dr.MASON_V2_REFS), "",
         "| Model(s) | Mode | " + " | ".join(r.replace("mason_v2_", "") for r in dr.MASON_V2_REFS) + " | mean over refs |", "|---|---|" + "---|" * (len(dr.MASON_V2_REFS) + 1)]
    for c in cur:
        for m, v in c.get("modes", {}).items():
            if "dtw_mason_v2" not in v: continue
            a11 = [v["dtw_mason_v2"][r]["all11"]["mean"] for r in dr.MASON_V2_REFS]; u5 = [v["dtw_mason_v2"][r]["upper5"]["mean"] for r in dr.MASON_V2_REFS]
            V.append("| " + "<br>".join(c["names"]) + " | " + m[:5] + " | " + " | ".join(f"{x:.3f} / {y:.3f}" for x, y in zip(a11, u5)) + f" | {sum(a11)/len(a11):.3f} / {sum(u5)/len(u5):.3f} |")
    L += V
    L += ["", "## Contact regressions (vs best earlier-trained checkpoint, same mode)", ""] + ([f"- {f}" for f in flags] or ["- none"])
    L += ["", "## History (all evaluated checkpoints)", "", "| Checkpoint(s) | Steps | Env | Det contact | Stoch contact |", "|---|---|---|---|---|"]
    for e in sorted(hist["entries"], key=lambda e: e["order"]):
        f = lambda m: "n/a" if e["modes"].get(m, {}).get("contact_rate") is None else f"{e['modes'][m]['contact_rate']*100:.0f}%"
        L.append(f"| {', '.join(e['names'])} | {e['steps']} | {e['env_fingerprint']} | {f('deterministic')} | {f('stochastic')} |")
    # dispersion detail for the ladder model and the scripted baseline
    det_rows = [c for c in cur if c.get("scripted") or "ppo_resid_v3_ladder_s0" in c["names"] or c.get("env_kwargs", {}).get("handedness") == "left"]
    D = ["# Dispersion detail: scripted baseline, ladder model and all left-handed models", "",
         f"{a.episodes} episodes/mode, seeds {a.seed}..{a.seed+a.episodes-1}; flight_tracker definitions (+y left, miss |y|>0.5 m; distance = final ball x at episode end (episode ends on landing/stop); max_ball_x = furthest x reached; carry = x at first landing after flight, mean over all episodes, 'landed' = fraction that landed). Peak club speed validated (>100 m/s or non-finite excluded and counted).", "",
         "| Model | Mode | Contact | Mean final x (m) | Std | Max | Mean max ball x (m) | Mean carry (m) | Landed | Lateral std (m) | Mean y | Left miss | Right miss | Peak club mean/max (m/s) | Peak club mph mean/max | % of 120 mph (max) | unstable eps | Launch elev mean deg (std) | flat? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | {v['contact_rate']*100:.0f}% | {v['mean_distance']:.2f} | {v['std_distance']:.2f} | {v['max_distance']:.2f} | {v['mean_max_ball_x']:.2f} | {v['mean_carry']:.3f} | {v['landed_fraction']*100:.0f}% | {v['lateral_std']:.3f} | {v['mean_y']:+.3f} | {v['left_miss_rate']*100:.0f}% | {v['right_miss_rate']*100:.0f}% | {v['peak_club_speed_mean']:.2f} / {v['peak_club_speed_max']:.2f} | {v['peak_club_mph_mean']:.1f} / {v['peak_club_mph_max']:.1f} | {v['peak_club_pct_target_max']:.1f}% | {v['peak_club_unstable_episodes']} | {v['launch_elev_mean_deg']:.1f} ({v['launch_elev_std_deg']:.1f}) | {'FLAT' if v['launch_flat_flag'] else 'no'} |")
    D += ["", "DTW to native Mason v2 recommended refs (mean rad, all11 / upper5; see leaderboard.md for caveats): mean over the 11 refs", "", "| Model | Mode | mean of 11 refs |", "|---|---|---|"]
    for c in det_rows:
        for m, v in c["modes"].items():
            D.append(f"| {'/'.join(c['names'])} | {m} | {v2m(v)} |")
    (RES / "dispersion_ladder_scripted.md").write_text("\n".join(D) + "\n")
    (RES / "dispersion_ladder_scripted.json").write_text(json.dumps([{k: c[k] for k in ("names", "steps", "config_source", "env_kwargs", "modes")} for c in det_rows], indent=1))
    (RES / "leaderboard.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
    from eval.compare_styles import from_leaderboard
    from_leaderboard()

if __name__ == "__main__":
    main()
