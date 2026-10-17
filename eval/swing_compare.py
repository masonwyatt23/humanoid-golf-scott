"""Swing comparison evaluator: score simulated swing FEATURES against (1) Mason reference features and (2) style profiles built ONLY
from published biomechanics / launch-monitor summary statistics (each number carries its source below; numbers I could not verify are absent).

  python -m eval.swing_compare [--episodes 20] [--seed 4000] [--models best_learned_yaw_s31 ...]   # writes results/swing_compare.{md,json}
  from eval.swing_compare import collect, features_from_rollout     # also used by eval/unified_style.py

Model/config selection reuses results/leaderboard_cache.json (env kwargs + scripted flag, latest entry; the env code simulated is the live working tree, whose fingerprint is stored in meta - the trainer's uncommitted env edits change it); evaluator protocol =
deterministic policy, seeds seed..seed+episodes-1, episodes end at first landing, FlightTracker substep instrumentation.

FEATURE DEFINITIONS (all per episode, then median/IQR over episodes; episodes without true club-ball contact are dropped from features and counted)
  t_impact        sim time of the first true club-head/ball contact (FlightTracker.t_impact).
  t_takeaway      first control step where the club-head geom is >0.05 m from its address position.            (club-based; Mason events are landmark-based)
  t_top           sim time of the maximum club-head height before t_impact.
  backswing_s     t_top - t_takeaway ;  downswing_s = t_impact - t_top ;  takeaway_to_impact_s = t_impact - t_takeaway.
  tempo_ratio     backswing_s / downswing_s.
  seq_*           peak |joint angular velocity| times from FlightTracker (5 ms resolution) in [t_impact-0.30 s, t_impact+0.05 s]:
                  wrist_minus_shoulder_s = t(peak wrist_R) - t(peak shoulder_R pitch); elbow_minus_shoulder_s likewise; torso_minus_hips_s = t(chest_yaw) - t(mean hip pitch);
                  seq_proximal_to_distal = peaks of hips -> chest_yaw -> shoulder -> elbow -> wrist -> club-head speed non-decreasing (fraction of episodes).
                  PROXY: the humanoid has hip PITCH joints and a chest_yaw joint but no pelvis-yaw joint; single-joint speeds, not segment angular speeds.
  chest_yaw_top_deg  |chest_yaw(t_top) - chest_yaw(address)| in degrees = upper-body turn relative to the (pinned) torso/pelvis. X-FACTOR PROXY ONLY: torso(pelvis) yaw is
                  fixed in this model, so this equals shoulders-vs-pelvis separation only if the pelvis does not turn (true here by construction); it is NOT a measured X-factor
                  and is NOT comparable to a human's, whose pelvis also rotates ~45-50 deg (see TPI row).
  peak_club_mph   peak club-head speed over substeps (FlightTracker; validated <100 m/s).   club_pre_mph = speed at the substep before first contact.
  ball_speed_mph  |ball velocity at end of contact| (separation velocity).   smash = ball_speed_sep / club_pre.   (KNOWN: sim smash ~1.0 because contact damping ratio=1,
                  see results/smash_anomaly.md - do not read it as strike quality.)
  launch_deg      elevation of the ball separation velocity.
  attack_deg      elevation of the club-head world velocity at the substep before first contact (+ = ascending). Club-head GEOM centre velocity, not TrackMan's
                  definition at max compression, and sim loft is applied through a rotated club geom (negative loft_deg = lofted face) - a proxy.
  carry_yd        env carry in yards (1 m = 1.09361 yd).

COMPARISON RULES
  * Mason profile: data/references/mason_target_features.json (v2 clips, real time, 11 swings; ~30 fps screen recordings: tempo +-15% at best, events +-1 frame; 2D MediaPipe proxies).
    Only features that exist on both sides are scored: tempo_ratio, backswing_s, downswing_s, wrist_minus_shoulder lag. Sim lag uses a different window than Mason's
    ([top, impact+0.15 s] arm-only), so it is indicative only. Mason speed/launch/attack/X-factor are UNAVAILABLE and are never scored.
  * Published profiles: a feature is scored only where the published statistic is the same quantity (see PROFILES). Status = within published range / below / above, with the
    percent deviation to the nearest edge. No composite 'style score' is claimed; we report n_within / n_scored.
  * The sim uses hypothetical actuators when the config boosts force_scale (>1) - speeds/tempo then describe the boosted model, not a human; flagged per row.
"""
import argparse, json, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
CACHE_DIR = RES / "_swing_cache"
MPS_TO_MPH = 2.23694
M_TO_YD = 1.09361

# ---------------------------------------------------------------- published profiles (ONLY numbers verified against a source on 2026-10-17)
S_TM_GM = "TrackMan PGA Tour driver averages as reproduced by Golf Monthly 'How Far PGA Tour Players Carry Their Drives' (https://www.golfmonthly.com/tour/how-far-pga-tour-players-carry-their-drives; numbers: Trackman) and the TrackMan tour-average table PDF (https://teeituprva.com/wp-content/uploads/2019/03/PGA-AVERAGES-INTERACTIVE.pdf)"
S_TM_AOA = "TrackMan blog 'What is Attack Angle?' (https://www.trackman.com/blog/attack-angle) tour averages: PGA Tour driver -0.9 deg, LPGA Tour driver +2.8 deg"
S_TM_CARRY = "TrackMan blog 'What Is Carry in Golf?' (https://www.trackman.com/blog/what-is-carry) tour averages: PGA Tour driver 282 yd, LPGA Tour driver 223 yd"
S_NOV = "J. Novosel, 'Tour Tempo' (2004) as reported in The Golf Wire press release 2006-05-03 (https://thegolfwire.com/105752-2/) and tourtempo.com/blogs/tips/what-the-numbers-mean: back:down ~3:1 (27/9 frames at 30 fps etc.); takeaway-to-impact 0.93-1.20 s for tour pros. Popular-book video analysis, not peer reviewed"
S_SONIC = "arXiv:1001.1137v1 'The Physics behind the Sonic Golf Swing Monitoring Device': ONE professional, 7 swings, backswing 731+-21 ms, downswing 258+-8 ms, ratio 2.8:1"
S_TPI = "Cheetham, Martin, Mottram, St Laurent (2001) 'The importance of stretching the X-Factor in the downswing of golf' (in Optimising Performance in Golf, ISBN 1 875378 37 5; reprinted J. Applied Golf Research 2011) via TPI article https://www.mytpi.com/articles/biomechanics/the-difference-between-x-factor-and-x-factor-stretch : 'TPI Tour average for X-Factor at pelvis transition is about 42 degrees'"
S_CHEETHAM_SEQ = "Cheetham, Rose, Neal, 'Comparison of Kinematic Sequence Parameters between Amateur and Professional Golfers' and Cheetham 'Kinematic Sequence: Transition and Downswing Phases' (http://sgpl.ch/Dokumente/Article-KinematicSequenceTransitionDownswing.pdf): pros peak pelvis -> thorax -> lead arm -> club, club still accelerating at impact; amateurs' mean arm peak occurs before mean thorax peak"

# each feature: value or (lo, hi) range, unit, source text, note.  Ranges only when the source states a range; point values get +-10% tolerance band (stated).
PROFILES = {
    "pga_tour_driver": {
        "label": "PGA Tour driver averages (TrackMan) + Tour Tempo",
        "features": {
            "peak_club_mph":   dict(value=113, source=S_TM_GM, note="'club speed' at impact; our peak substep club speed used as the proxy"),
            "ball_speed_mph":  dict(value=167, source=S_TM_GM),
            "smash":           dict(value=1.48, source=S_TM_GM, note="sim smash ~1.0 is a known contact-model artifact (smash_anomaly.md)"),
            "launch_deg":      dict(value=10.9, source=S_TM_GM),
            "attack_deg":      dict(value=-0.9, source=S_TM_AOA, note="older table (S_TM_GM) lists -1.3 deg; both published, we use the newer"),
            "carry_yd":        dict(value=282, source=S_TM_CARRY, note="older table (S_TM_GM) lists 275 yd"),
            "tempo_ratio":     dict(value=3.0, source=S_NOV, note="popular-book 3:1; arXiv single-pro measurement gives 2.8:1 (" + S_SONIC.split(':')[0] + ")"),
            "takeaway_to_impact_s": dict(range=(0.93, 1.20), source=S_NOV),
            "chest_yaw_top_deg": dict(value=42, source=S_TPI, note="TPI figure is X-factor AT PELVIS TRANSITION (shoulder-minus-pelvis turn); our value is a chest-yaw proxy - NOT the same quantity, shown for context only", context_only=True),
        },
        "qualitative": {"sequence_proximal_to_distal": S_CHEETHAM_SEQ},
    },
    "lpga_tour_driver": {
        "label": "LPGA Tour driver (TrackMan; only the numbers verified)",
        "features": {
            "attack_deg": dict(value=2.8, source=S_TM_AOA),
            "carry_yd":   dict(value=223, source=S_TM_CARRY),
        },
        "qualitative": {},
    },
}
POINT_TOL = 0.10   # +-10% band around a published point value (a judgement call, not a published tolerance)


def _band(spec):
    if "range" in spec: return spec["range"]
    v = spec["value"]; d = abs(v) * POINT_TOL if v else 0.1
    return (v - d, v + d)


def score_profile(med, prof):
    rows, n_in, n_sc = [], 0, 0
    for f, spec in prof["features"].items():
        x = med.get(f)
        if x is None or not np.isfinite(x): rows.append(dict(feature=f, status="not measured")); continue
        lo, hi = _band(spec)
        st = "within" if lo <= x <= hi else ("below" if x < lo else "above")
        edge = lo if x < lo else hi
        dev = None if st == "within" else (float(x - edge) if f in ("attack_deg", "launch_deg") else float((x - edge) / (abs(edge) if edge else 1) * 100))   # angles: absolute deg outside (percent of a near-zero angle is meaningless); others: % outside
        ctx = bool(spec.get("context_only"))
        if not ctx: n_sc += 1; n_in += st == "within"
        rows.append(dict(feature=f, sim_median=float(x), target=spec.get("value"), band=[float(lo), float(hi)], status=st, pct_outside=dev, context_only=ctx,
                         source=spec["source"], note=spec.get("note", "")))
    return dict(label=prof["label"], n_within=n_in, n_scored=n_sc, rows=rows)


# ---------------------------------------------------------------- Data Agent style profiles (data/references/pro_swing_profiles.json, main a5df07b)
PRO_MAP = {"club_head_speed_mph": "peak_club_mph", "ball_speed_mph": "ball_speed_mph", "attack_angle_deg": "attack_deg", "launch_angle_deg": "launch_deg",
           "backswing_s": "backswing_s", "downswing_s": "downswing_s", "tempo_ratio": "tempo_ratio", "smash_factor": "smash"}
CONF_W = {"high": 1.0, "medium": 0.6, "low": 0.3, "none": 0.0}   # my weighting choice; unverified or null-target features get weight 0 (listed as skipped)
PRO_NOT_MEASURED = ("x_factor_top_deg", "pelvis_turn_top_deg", "thorax_turn_top_deg", "pelvis_peak_speed_dps", "thorax_peak_speed_dps", "arm_peak_speed_dps", "spin_rate_rpm",
                    "driving_distance_yd", "pelvis_sway_top_in", "pelvis_sway_impact_in")   # no sim counterpart (pelvis fixed / no spin readout - ball-model spin is ~60% high vs tour data per impact_physics_calibration.json / total != carry)


def load_pro_profiles():
    """Reads data/references/pro_swing_profiles.json; falls back to `git show origin/main:` (file lives on main, a5df07b) so no copy is needed in this branch."""
    import subprocess
    f = ROOT / "data/references/pro_swing_profiles.json"
    txt = f.read_text() if f.exists() else subprocess.run(["git", "show", "origin/main:data/references/pro_swing_profiles.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return json.loads(txt)


def score_pro_profiles(med, pro):
    """Confidence-weighted score per style profile. Feature scored iff: sim feature exists, target not null, unverified is False, confidence weight > 0.
    Band = [min, max] if both given, else target +-10% (my tolerance). Reported: weighted fraction within band, weighted mean |normalised deviation| (|x-target| / half-band), and the skipped list with reasons."""
    out = {}
    for pid, prof in pro["profiles"].items():
        rows, skipped, wsum, win, wdev = [], [], 0.0, 0.0, 0.0
        for f, spec in prof["features"].items():
            sf = PRO_MAP.get(f)
            if f in PRO_NOT_MEASURED or sf is None: skipped.append((f, "no sim counterpart / proxy only")); continue
            if spec.get("target") is None: skipped.append((f, "null target")); continue
            if spec.get("unverified"): skipped.append((f, "unverified")); continue
            w = CONF_W.get(spec.get("confidence"), 0.0)
            if w <= 0: skipped.append((f, f"confidence {spec.get('confidence')}")); continue
            x = med.get(sf)
            if x is None or not np.isfinite(x): skipped.append((f, "not measured in this run")); continue
            t = spec["target"]; lo, hi = (spec["min"], spec["max"]) if spec.get("min") is not None and spec.get("max") is not None else (t - abs(t) * POINT_TOL, t + abs(t) * POINT_TOL)
            half = max((hi - lo) / 2, 1e-9); inside = lo <= x <= hi; dev = abs(x - t) / half
            wsum += w; win += w * inside; wdev += w * dev
            rows.append(dict(feature=f, sim=float(x), target=t, band=[float(lo), float(hi)], inside=bool(inside), norm_dev=float(dev), weight=w, confidence=spec["confidence"], note=spec.get("note", "")))
        out[pid] = dict(weighted_within=(win / wsum if wsum else None), weighted_norm_dev=(wdev / wsum if wsum else None), n_scored=len(rows), weight_sum=wsum, rows=rows, skipped=skipped)
    return out


# ---------------------------------------------------------------- rollout + features
def _fp():
    from eval.leaderboard import env_fingerprint
    return env_fingerprint()


def resolve(name):
    """-> (kw, scripted, label, md5name, hypothetical_note) from the leaderboard cache for the current fingerprint (latest entry whose names contain `name` as substring)."""
    cache = json.loads((RES / "leaderboard_cache.json").read_text())
    cand = [c for k, c in cache.items() if "env_kwargs" in c and any(name == n or name in n for n in c["names"])]   # latest entry; env kwargs only (the env CODE used is the live working tree)
    if not cand: raise KeyError(f"{name}: no leaderboard-cache entry; run eval.leaderboard first")
    c = max(cand, key=lambda c: c.get("evaluated_at") or "")
    kw = c["env_kwargs"]
    hyp = kw.get("force_scale", 1.0) > 1.0
    return kw, bool(c.get("scripted")), c["names"][0], hyp


def collect(name, episodes=20, seed=4000, det=True, force=False):
    """Roll out; returns dict(features per episode list, joint trajectories (list of (T,11) rad, control-step rate), meta). Cached in results/_swing_cache (not committed)."""
    import mujoco
    from stable_baselines3 import PPO
    from eval.env_factory import make_env, joint_qpos_idx
    from eval.flight_tracker import FlightTracker
    kw, scripted, label, hyp = resolve(name)
    CACHE_DIR.mkdir(exist_ok=True)
    cp = CACHE_DIR / f"{name}_{episodes}_{seed}_{int(det)}_{_fp()[:8]}.npz"
    if cp.exists() and not force:
        z = np.load(cp, allow_pickle=True); return dict(eps=json.loads(str(z["eps"])), trajs=[z[f"t{i}"] for i in range(int(z["n"]))], meta=json.loads(str(z["meta"])))
    env = make_env(kw); zero = np.zeros(env.action_space.shape, np.float32)
    model = None if scripted else PPO.load(str(ROOT / "models" / label))
    qi = joint_qpos_idx(env); yaw_q = int(env.model.jnt_qposadr[env.model.joint("chest_yaw").id])
    ft = FlightTracker(env).install()
    rec = {"v": [], "hist": []}
    prev = mujoco.mj_step
    def wrapped(m, d, *a, **k):   # records club-head world velocity per substep (chained after FlightTracker's own hook)
        prev(m, d, *a, **k)
        v6 = np.zeros(6); mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_GEOM, env._club_geom, v6, 0); rec["v"].append(v6[3:].copy())
        if env.true_contact and "att" not in rec and len(rec["v"]) >= 3: rec["att"] = rec["v"][-3].copy()
    mujoco.mj_step = wrapped
    eps, trajs = [], []
    try:
        for ep in range(episodes):
            obs, _ = env.reset(seed=seed + ep); ft.reset(); rec["v"].clear(); rec.pop("att", None); done = False; info = {}
            tt, cz, cp_, yaw, jq = [], [], [], [], [env.data.qpos[qi].copy()]
            c0 = env.data.geom_xpos[env._club_geom].copy(); yaw0 = float(env.data.qpos[yaw_q])
            while not done:
                a = zero if scripted else model.predict(obs, deterministic=det)[0]
                obs, _, te, tr, info = env.step(a); ft.step(); done = te or tr
                tt.append(float(env.data.time)); cp_.append(env.data.geom_xpos[env._club_geom].copy()); yaw.append(float(env.data.qpos[yaw_q]) - yaw0); jq.append(env.data.qpos[qi].copy())
            sh = ft.summary(info); trajs.append(np.array(jq))
            e = dict(contact=bool(sh["true_contact"]), carry_yd=sh["carry_yd"], launch_deg=sh["launch_elev_deg"], peak_club_mph=sh["peak_club_speed"] * MPS_TO_MPH,
                     ball_speed_mph=sh["ball_speed_sep"] * MPS_TO_MPH, club_pre_mph=sh["club_speed_pre_contact"] * MPS_TO_MPH, seq=sh["seq"])
            e["smash"] = e["ball_speed_mph"] / e["club_pre_mph"] if e["club_pre_mph"] and e["club_pre_mph"] == e["club_pre_mph"] else float("nan")
            ti = ft.t_impact
            if e["contact"] and ti is not None:
                tt = np.array(tt); P = np.array(cp_); w = tt <= ti + 1e-9
                far = np.linalg.norm(P - c0, axis=1) > 0.05
                t_take = float(tt[np.argmax(far & w)]) if (far & w).any() else float("nan")
                t_top = float(tt[w][int(np.argmax(P[w, 2]))])
                e.update(t_takeaway=t_take, t_top=t_top, t_impact=float(ti), backswing_s=t_top - t_take, downswing_s=float(ti) - t_top,
                         takeaway_to_impact_s=float(ti) - t_take)
                e["tempo_ratio"] = e["backswing_s"] / e["downswing_s"] if e["downswing_s"] > 0 else float("nan")
                e["chest_yaw_top_deg"] = float(abs(np.degrees(np.array(yaw)[w][int(np.argmax(P[w, 2]))])))
                if "att" in rec:
                    v = rec["att"]; e["attack_deg"] = float(np.degrees(np.arctan2(v[2], np.hypot(v[0], v[1]) + 1e-9)))
                s = e["seq"]
                if s.get("seq_ok"):
                    e.update(wrist_minus_shoulder_s=s["wrist_minus_shoulder_s"], elbow_minus_shoulder_s=s["elbow_minus_shoulder_s"],
                             torso_minus_hips_s=s["torso_minus_hips_s"], seq_proximal_to_distal=float(s["prox_to_distal"]))
            eps.append(e)
    finally:
        mujoco.mj_step = prev; ft.close()
    meta = dict(name=name, label=label, scripted=scripted, hypothetical_actuators=hyp, force_scale=kw.get("force_scale"), episodes=episodes, seed=seed, deterministic=det,
                env_fingerprint=_fp(), control_dt=float(tt[1] - tt[0]) if len(tt) > 1 else None)
    np.savez(cp, eps=json.dumps(eps), meta=json.dumps(meta), n=len(trajs), **{f"t{i}": t for i, t in enumerate(trajs)})
    return dict(eps=eps, trajs=trajs, meta=meta)


FEATS = ["tempo_ratio", "backswing_s", "downswing_s", "takeaway_to_impact_s", "wrist_minus_shoulder_s", "elbow_minus_shoulder_s", "torso_minus_hips_s", "seq_proximal_to_distal",
         "chest_yaw_top_deg", "peak_club_mph", "club_pre_mph", "ball_speed_mph", "smash", "launch_deg", "attack_deg", "carry_yd"]


def features_from_rollout(r):
    ok = [e for e in r["eps"] if e["contact"]]
    out = {"n_episodes": len(r["eps"]), "n_contact": len(ok)}
    for f in FEATS:
        v = np.array([e[f] for e in ok if f in e and e[f] == e[f]], float)
        out[f] = dict(median=float(np.median(v)), q25=float(np.percentile(v, 25)), q75=float(np.percentile(v, 75)), n=len(v)) if len(v) else None
    return out


def mason_profile():
    d = json.loads((ROOT / "data/references/mason_target_features.json").read_text())["mason"]["aggregate"]
    g = lambda k: d[k]
    m = {"tempo_ratio": g("tempo_ratio"), "backswing_s": g("backswing_s"), "downswing_s": g("downswing_s"), "wrist_minus_shoulder_s": g("sequencing.wrist_minus_shoulder_peak_lag_s")}
    return {k: dict(median=v["median"], iqr=v["iqr"], n=v["n"]) for k, v in m.items()}


def score_mason(feat, mp):
    rows = []
    for f, ref in mp.items():
        x = feat.get(f)
        if not x: rows.append(dict(feature=f, status="not measured")); continue
        lo, hi = ref["iqr"]
        st = "within Mason IQR" if lo <= x["median"] <= hi else ("below" if x["median"] < lo else "above")
        rows.append(dict(feature=f, sim_median=x["median"], mason_median=ref["median"], mason_iqr=[lo, hi], n_mason=ref["n"], status=st,
                         ratio_to_mason_median=float(x["median"] / ref["median"]) if ref["median"] else None))
    return rows


DEFAULT_MODELS = ["best_learned_yaw_s31", "ppo_v3flt_yaw_s32", "ppo_resid_v3_left_an3_s1", "ppo_resid_v3_left_fast2_s11",
                  "fast v3 Stage 6", "fast v2 lofted", "trainer cfg: left, loft 7"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--episodes", type=int, default=20); ap.add_argument("--seed", type=int, default=4000)
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
    mp = mason_profile(); out = {"generated": time.strftime("%Y-%m-%d %H:%M"), "episodes": a.episodes, "seed": a.seed, "mason_profile": mp,
                                 "published_profiles": {k: {"label": v["label"], "features": v["features"], "qualitative": v["qualitative"], "point_tolerance": POINT_TOL} for k, v in PROFILES.items()}, "models": {}}
    pro = load_pro_profiles()
    for n in a.models:
        try: r = collect(n, a.episodes, a.seed, True, a.force)
        except Exception as e: print("SKIP", n, type(e).__name__, e); continue
        feat = features_from_rollout(r); med = {f: (feat[f]["median"] if feat.get(f) else None) for f in FEATS}
        out["models"][r["meta"]["label"] if not r["meta"]["scripted"] else n] = dict(meta=r["meta"], features=feat, vs_mason=score_mason(feat, mp), vs_pro_style_profiles=score_pro_profiles(med, pro),
                                                                                    vs_published={k: score_profile(med, p) for k, p in PROFILES.items()})
        print("done", n, feat["n_contact"], "/", feat["n_episodes"])
    (RES / "swing_compare.json").write_text(json.dumps(out, indent=1))
    L = ["# Swing comparison: sim features vs Mason refs and published-stats profiles", "",
         f"{a.episodes} deterministic episodes per model, seeds {a.seed}+, evaluator protocol; medians over contact episodes. Feature definitions + caveats: docstring of `eval/swing_compare.py`. Generated {out['generated']} (box time, America/New_York).", "",
         "**Read this first:** (1) every learned/scripted row here is a boosted-actuator sim (force_scale 2 > 1 => HYPOTHETICAL ACTUATORS) so absolute speeds/tempo are not human-attainable evidence; (2) sim smash ~1.0 is a contact-model artifact; (3) sim X-factor is a chest-yaw proxy (pelvis fixed); (4) Mason features are 2D-video proxies, tempo +-15% at best, and Mason speed/launch/attack/X-factor are unavailable so are never scored; (5) published profiles are summary averages of populations, not any individual's swing; 'within' uses published range, or +-10% around a published point value (my tolerance choice).", "",
         "## Feature medians (sim)", "", "| Model | learned? | contact | " + " | ".join(FEATS) + " |", "|---|---|---|" + "---|" * len(FEATS)]
    f2 = lambda x: "-" if x is None else (f"{x['median']:.2f}" if abs(x['median']) < 100 else f"{x['median']:.0f}")
    for n, m in out["models"].items():
        L.append(f"| {n} | {'SCRIPTED (not learned)' if m['meta']['scripted'] else 'LEARNED (PPO residual on scripted base)'}{' / hypothetical actuators' if m['meta']['hypothetical_actuators'] else ''} | {m['features']['n_contact']}/{m['features']['n_episodes']} | " + " | ".join(f2(m['features'][f]) for f in FEATS) + " |")
    L += ["", "## vs Mason (target_features.json, v2 real-time clips; IQR of 11 swings)", "", "| Model | feature | sim median | Mason median [IQR] | status |", "|---|---|---|---|---|"]
    for n, m in out["models"].items():
        for r in m["vs_mason"]:
            if r["status"] == "not measured": L.append(f"| {n} | {r['feature']} | - | - | not measured |"); continue
            L.append(f"| {n} | {r['feature']} | {r['sim_median']:.3f} | {r['mason_median']:.3f} [{r['mason_iqr'][0]:.3f}, {r['mason_iqr'][1]:.3f}] | {r['status']} ({r['ratio_to_mason_median']:.2f}x median) |")
    for pk, p in PROFILES.items():
        L += ["", f"## vs {p['label']}", "", "Sources (per number):", ""]
        seen = set()
        for f, s in p["features"].items(): L.append(f"- `{f}` = {s.get('range', s.get('value'))}: {s['source']}" + (f" -- {s['note']}" if s.get("note") else ""))
        for q, s in p["qualitative"].items(): L.append(f"- qualitative `{q}`: {s}")
        L += ["", "| Model | " + " | ".join(p["features"]) + " | n within / scored |", "|---|" + "---|" * (len(p["features"]) + 1)]
        for n, m in out["models"].items():
            sp = m["vs_published"][pk]; cells = []
            for r in sp["rows"]:
                cells.append("-" if r["status"] == "not measured" else f"{r['sim_median']:.2f} ({r['status']}{'' if r['pct_outside'] is None else f' {r['pct_outside']:+.1f}{'deg' if r['feature'] in ('attack_deg', 'launch_deg') else '%'}'}{', ctx' if r['context_only'] else ''})")
            L.append(f"| {n} | " + " | ".join(cells) + f" | {sp['n_within']}/{sp['n_scored']} |")
    L += ["", "## vs Data Agent style profiles (data/references/pro_swing_profiles.json, schema pro_swing_profiles/v1, main a5df07b)", "",
          "STYLE PROFILES = statistical summaries of published numbers (some from single shots / 30 fps video / search snippets), NOT simulations or claims about any person; internal labels only (names are file ids, do not use externally; legal review before any external use - see the file's legal_likeness_cautions).",
          "Scoring: only features with a non-null target, `unverified` == false and confidence != none; weight high 1.0 / medium 0.6 / low 0.3 (my choice). Band = [min,max] if given else target +-10%. 'within' = confidence-weighted fraction of scored features inside the band; 'dev' = weighted mean |x-target|/half-band (0 = on target, 1 = band edge). Not scored: pelvis/thorax/X-factor/peak segment speeds (sim has no pelvis yaw; chest-yaw proxy only), spin (sim spin is ~60% high vs tour data: data/references/impact_physics_calibration.json), driving distance (total vs carry).",
          "Sim rows are boosted actuators (HYPOTHETICAL ACTUATORS) with sim smash ~1.0 (contact artifact) and sim tempo ~5:1, so low scores reflect those, not 'style'. Mason's inputs to the Data Agent's comparison are Instagram screen recordings (~30 fps): tempo is a loose band, durations are unreliable (see docs/MASON_VS_PROFILES.md); Mason is not scored here.",
          "Licensing note: reference MOTION data licences differ (data/references/mocap_dataset_licenses.json); only CMU (and 100STYLE, CC BY) are commercial-clean; Mason/MultiSense refs used for DTW/overlays here are internal diagnostics only.", "",
          "| Model | " + " | ".join(pro["profiles"]) + " |", "|---|" + "---|" * len(pro["profiles"])]
    for n, m in out["models"].items():
        L.append(f"| {n} | " + " | ".join("-" if m["vs_pro_style_profiles"][k]["weighted_within"] is None else f"{m['vs_pro_style_profiles'][k]['weighted_within']*100:.0f}% within, dev {m['vs_pro_style_profiles'][k]['weighted_norm_dev']:.2f} (n={m['vs_pro_style_profiles'][k]['n_scored']})" for k in pro["profiles"]) + " |")
    first = next(iter(out["models"].values()), None)
    if first:
        L += ["", "Skipped per profile (reason): " + "; ".join(f"{k}: " + ", ".join(f"{f} ({r})" for f, r in v["skipped"] if r not in ("no sim counterpart / proxy only",)) for k, v in first["vs_pro_style_profiles"].items())]
    (RES / "swing_compare.md").write_text("\n".join(L) + "\n"); print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
