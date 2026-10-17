"""Course mode: Monte Carlo score estimates on a SYNTHETIC EXAMPLE course (not a real course).

LABEL: model-based estimate, not a real round. Everything here is an assumption-laden simulation:
 * Course: 18 invented holes (par 72) with invented yardages/fairway widths/hazards. Straight holes along +x, +y = left.
 * Driver shots use a dispersion profile (carry mean/sd, lateral sd, roll) taken from the simulator's measured data (results/leaderboard.json),
   or from a hypothetical scaling of that data to TrackMan-average carry; other clubs are fixed fractions of driver carry (assumed bag ratios).
 * Rough/bunker multipliers, chip proximity, putting make-probability, penalty rules are ASSUMED constants (see DEFAULTS), not fitted to data.
"""
from __future__ import annotations
import json, os, math
from dataclasses import dataclass, field
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LABEL = "model-based estimate, not a real round (synthetic example course; assumed short game)"

# ---- assumptions (all invented, documented) ----
DEFAULTS = dict(
    bag_fractions=[1.00, 0.92, 0.84, 0.77, 0.71, 0.65, 0.59, 0.53, 0.47, 0.40, 0.30],   # generic ladder of club carries as fractions of driver carry (assumed)
    rough_carry_mult=0.85, rough_disp_mult=1.3, bunker_carry_mult=0.60, bunker_disp_mult=1.6,
    green_radius_yd=14.0, chip_max_yd=45.0, ob_halfwidth_yd=45.0, max_strokes=12,
    chip_leave_sd_frac=0.10, chip_leave_min_ft=4.0, putt_scale_ft=8.0, putt_exp=2.5,
)


@dataclass
class Hole:
    n: int; par: int; yards: int; fw_halfwidth_yd: float
    hazards: list = field(default_factory=list)   # dicts: type 'bunker'|'water', x0,x1 (yd from tee), y0,y1 (yd, + left)


def example_course() -> list[Hole]:
    """SYNTHETIC example 18-hole yardage book (par 72, 7,0xx yd). Invented; not any real course."""
    spec = [(4, 430, 15), (5, 565, 17), (3, 185, 0), (4, 395, 14), (4, 455, 15), (3, 215, 0), (5, 590, 17), (4, 410, 14), (4, 440, 15),
            (4, 420, 15), (3, 175, 0), (5, 545, 16), (4, 470, 14), (4, 385, 13), (3, 230, 0), (4, 445, 15), (5, 600, 17), (4, 425, 15)]
    holes = []
    for i, (par, y, fw) in enumerate(spec, 1):
        hz = []
        if par >= 4:
            hz.append(dict(type="bunker", x0=y * (0.58 if par == 4 else 0.50), x1=y * (0.58 if par == 4 else 0.50) + 30, y0=(fw - 4) * (1 if i % 2 else -1) , y1=(fw + 8) * (1 if i % 2 else -1)))
        if i in (4, 12, 15):
            hz.append(dict(type="water", x0=y - 40, x1=y - 12, y0=-60 if i != 12 else 12, y1=-12 if i != 12 else 60))   # side water short of the green
        hz.append(dict(type="bunker", x0=y - 18, x1=y - 4, y0=10, y1=22))                                              # greenside bunker (left)
        holes.append(Hole(i, par, y, fw, hz))
    return holes


def _in_box(h, x, y):
    for hz in h.hazards:
        ya, yb = sorted((hz["y0"], hz["y1"]))
        if hz["x0"] <= x <= hz["x1"] and ya <= y <= yb: return hz["type"]
    return None


def lie_at(h: Hole, x, y, cfg):
    d_pin = math.hypot(h.yards - x, y)
    if abs(y) > cfg["ob_halfwidth_yd"]: return "ob"
    if d_pin <= cfg["green_radius_yd"]: return "green"
    hz = _in_box(h, x, y)
    if hz: return hz
    return "fairway" if abs(y) <= h.fw_halfwidth_yd or d_pin < 35 else "rough"


@dataclass
class Profile:
    name: str; driver_carry_yd: float; driver_carry_sd_yd: float; lateral_sd_yd: float; roll_frac: float; note: str


def profiles_from_leaderboard(path=None, model_names=None):
    """Build profiles from results/leaderboard.json for the best qualifying model (or model_names=[...]).
    A: 'sim as measured' (MuJoCo ball distance/lateral spread; episodes end at first landing so roll=0).
    B: HYPOTHETICAL: same RELATIVE spread (carry CV, lateral/carry ratio) scaled to the TrackMan PGA Tour average carry 275 yd and analytic-model roll (total/carry-1)."""
    d = json.load(open(path or os.path.join(ROOT, "results", "leaderboard.json")))
    names = model_names or d["best_qualifying"]
    m = next(m for m in d["models"] if names[0] in m["names"] and (len(names) < 2 or names[1] in m["names"]))
    det = m["modes"]["deterministic"]
    carry = det["mean_carry_yd"]; sd = det["std_distance"] * 1.09361; lat = det["lateral_std"] * 1.09361
    label = "/".join(names)
    val = json.load(open(os.path.join(ROOT, "results", "golf_simulator_validation.json")))
    roll = val["flight_from_published_launch"]["shot"]["total_yd"] / val["flight_from_published_launch"]["shot"]["carry_yd"] - 1
    cv, ang = sd / carry, lat / carry
    force = m["env_kwargs"].get("force_scale")
    note = f"{label} ({'scripted (not learned)' if m['scripted'] else 'learned'}); force_scale={force}"
    return [Profile(f"A: sim as measured - {label}", carry, sd, lat, 0.0, note + "; MuJoCo ball, smash~1.0 artifact; HYPOTHETICAL ACTUATORS" if force and force > 1 else note),
            Profile(f"B: HYPOTHETICAL - {label} spread scaled to 275 yd tour-avg carry", 275.0, 275.0 * cv, 275.0 * ang, roll,
                    f"carry CV {cv:.2f} and lateral/carry {ang:.3f} from {label}; roll from analytic model at TrackMan avg launch; not something the sim achieves")]


def _shot(rng, prof, cfg, club_frac, target_carry, lie, aim_y=0.0, roll=0.0):
    nominal = prof.driver_carry_yd * club_frac
    mult_c, mult_d = {"rough": (cfg["rough_carry_mult"], cfg["rough_disp_mult"]), "bunker": (cfg["bunker_carry_mult"], cfg["bunker_disp_mult"])}.get(lie, (1.0, 1.0))
    intended = min(target_carry, nominal * mult_c)
    sd_c = prof.driver_carry_sd_yd * club_frac * mult_d * (intended / max(nominal, 1e-9))
    carry = max(1.0, rng.normal(intended, sd_c))
    lat = rng.normal(aim_y, prof.lateral_sd_yd * (carry / max(prof.driver_carry_yd, 1e-9)) * mult_d)   # angular dispersion: sd scales with carry
    return carry, lat


def _putt(rng, d_ft, cfg):
    n = 0
    while True:
        n += 1
        if rng.random() < 1.0 / (1.0 + (d_ft / cfg["putt_scale_ft"]) ** cfg["putt_exp"]) or n >= 4: return n
        d_ft = max(1.0, rng.uniform(0.0, 0.3) * d_ft + 1.0)


def play_hole(h: Hole, prof: Profile, rng, cfg=DEFAULTS):
    x, y, strokes, lie, fw_hit, gir = 0.0, 0.0, 0, "tee", None, False
    while strokes < cfg["max_strokes"]:
        rem = math.hypot(h.yards - x, y)
        if lie == "green":
            strokes += _putt(rng, rem * 3.0, cfg); break
        if rem <= cfg["chip_max_yd"]:                       # chip/pitch/bunker shot to green
            strokes += 1; leave = abs(rng.normal(0, cfg["chip_leave_sd_frac"] * rem * 3.0)) + cfg["chip_leave_min_ft"] * (1.5 if lie in ("bunker", "rough") else 1.0)
            strokes += _putt(rng, leave, cfg); break
        # full shot: tee -> driver on par 4/5; otherwise club that carries the distance, else longest
        if lie == "tee" and h.par >= 4: frac = 1.0
        else:
            ok = [f for f in cfg["bag_fractions"] if prof.driver_carry_yd * f >= rem * (0.97 if lie not in ("rough", "bunker") else 1.1)]
            frac = min(ok) if ok else cfg["bag_fractions"][0]
            if not ok and rem > prof.driver_carry_yd * 1.0: frac = 1.0
        approach = frac * prof.driver_carry_yd >= rem * 0.97 and not (lie == "tee" and h.par >= 4)
        target = rem if approach else 1e9
        carry, lat = _shot(rng, prof, cfg, frac, target, lie)
        roll = 0.0 if approach or lie in ("rough", "bunker") else prof.roll_frac * frac
        nx, ny = x + carry * (1 + roll), y + lat
        strokes += 1
        nl = lie_at(h, nx, ny, cfg)
        if lie == "tee" and h.par >= 4: fw_hit = nl == "fairway"
        if nl in ("water", "ob"):
            strokes += 1; continue                           # penalty stroke, replay from same spot
        x, y, lie = nx, ny, nl
        if nl == "green" and strokes <= h.par - 2: gir = True
    return dict(strokes=min(strokes, cfg["max_strokes"]), fw_hit=fw_hit, gir=gir)


def play_round(course, prof, rng, cfg=DEFAULTS):
    return [play_hole(h, prof, rng, cfg) for h in course]


def simulate(course, prof, rounds=2000, seed=0, cfg=DEFAULTS):
    rng = np.random.default_rng(seed)
    S = np.zeros((rounds, len(course)), int); fw = []; gir = []
    for r in range(rounds):
        res = play_round(course, prof, rng, cfg)
        S[r] = [x["strokes"] for x in res]
        fw += [x["fw_hit"] for x in res if x["fw_hit"] is not None]; gir += [x["gir"] for x in res]
    tot = S.sum(1); par = sum(h.par for h in course)
    return dict(profile=prof.name, note=prof.note, rounds=rounds, par=par, mean_score=float(tot.mean()), sd_score=float(tot.std()),
                p10=float(np.percentile(tot, 10)), p90=float(np.percentile(tot, 90)), mean_vs_par=float(tot.mean() - par),
                fairways_hit_pct=float(100 * np.mean(fw)), gir_pct=float(100 * np.mean(gir)),
                hole_means=[float(v) for v in S.mean(0)], label=LABEL)


def run(rounds=2000, seed=0):
    course = example_course()
    sims = [simulate(course, p, rounds, seed) for p in profiles_from_leaderboard()]
    out = dict(label=LABEL, course="SYNTHETIC EXAMPLE (invented)", holes=[dict(n=h.n, par=h.par, yards=h.yards, fw_halfwidth_yd=h.fw_halfwidth_yd, hazards=h.hazards) for h in course],
               total_yards=sum(h.yards for h in course), par=sum(h.par for h in course), assumptions=DEFAULTS, results=sims)
    json.dump(out, open(os.path.join(ROOT, "results", "course_estimates.json"), "w"), indent=1)
    md = [f"# Course-mode score estimates: {LABEL}", "", f"Synthetic example course (invented): par {out['par']}, {out['total_yards']} yd. Monte Carlo, {rounds} rounds per profile, seed {seed}.", "",
          "| profile | mean score | vs par | sd | p10-p90 | fairways | GIR |", "|---|---|---|---|---|---|---|"]
    for s in sims: md.append(f"| {s['profile']} | {s['mean_score']:.1f} | {s['mean_vs_par']:+.1f} | {s['sd_score']:.1f} | {s['p10']:.0f}-{s['p90']:.0f} | {s['fairways_hit_pct']:.0f}% | {s['gir_pct']:.0f}% |")
    md += ["", "Profile notes:"] + [f"- {s['profile']}: {s['note']}" for s in sims]
    md += ["", "Assumptions (invented constants, see sim/course.py DEFAULTS): " + json.dumps(DEFAULTS), "",
           "Caveats: Gaussian dispersion (real/sim tails are heavier: the sim's lateral max was ~12 m), straight holes, fixed bag ratios, no wind, assumed putting/chipping. "
           "Profile A reflects the simulator as it is today (a ~120 yd driver); profile B is a what-if and is NOT achieved by any model."]
    open(os.path.join(ROOT, "results", "course_estimates.md"), "w").write("\n".join(md) + "\n")
    return out


if __name__ == "__main__":
    o = run()
    for s in o["results"]: print(s["profile"], round(s["mean_score"], 1), round(s["fairways_hit_pct"]), round(s["gir_pct"]))
