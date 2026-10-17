"""ADDITIVE launch-monitor-style report over eval_gate JSONs. Read-only: never changes gate pass/fail, never edits inputs.
Uses the PureGolf Data Agent's data/launch_output.py (branch launch-output-layer d6d0f0e) for unit conversion and flags.
Smash here = mean ball speed / mean impact club speed (ratio of means). The gate JSON's smash_factor_mean is a mean of per-episode ratios
(not a true ratio of the reported speeds), so it is shown separately. Spin = gate backspin_rpm_mean: for the power tier it is HAND-SET by the
env impact model (spin_k), not simulated from contact.
Target row = published TrackMan 120 mph driver row: 178 ball mph / smash 1.483 / launch 9.3 deg / 2890 rpm / 296 yd. 130/132 mph rows are
extrapolated upper bounds only. Smash/spin thresholds (fail >1.50, warn >1.49 or <1.30; spin pass 1800-3000) are DERIVED, not published.
Usage: python -m eval.launch_report [gate.json ...]  -> results/launch_report.md"""
import glob, json, sys
from pathlib import Path
from data import launch_output as lo
ROOT = Path(__file__).resolve().parent.parent
TARGET = dict(club_mph=120, ball_mph=178, smash=1.483, launch_deg=9.3, spin_rpm=2890, carry_yd=296)
DEFAULT = ["results/imit_private/gain120/gate_imit18_power_dart_s51.json", "results/imit_private/gain102/gate_imit18_power_dart_s51.json",
           "results/imit_private/gate_imit18_power_dart_s51.json", "results/imit_private/gate_imit18_power_dart_s52.json",
           "results/gate_imit15_dart_s52_seed4000.json", "results/imit_private/gate_imit15_dart_s53.json", "results/imit_private/gate_imit19_masonmapped_dart_s51.json",
           "results/imit_private/gate_ppo15_stoch_s71.json", "results/imit_private/gate_ppo15_bcreg_s62.json"]

def row(path):
    j = json.load(open(path)); p = j["policy_det"]; ek = j.get("env_kwargs", {})
    ball = p.get("mean_peak_ball_speed"); club = p.get("impact_club_speed_mean")
    gain = ek.get("impact_gain") or (ek.get("impact_model") or {}).get("gain")
    s = dict(carry=p.get("mean_carry"), mean_peak_ball_speed=ball, impact_club_speed=club, launch_elev_mean_deg=p.get("launch_elev_mean_deg"),
             spin_rpm=(p.get("backspin_rpm_mean") if p.get("backspin_rpm_mean") == p.get("backspin_rpm_mean") else None), contact_rate=p.get("contact_rate"), peak_club_mph_mean=p.get("peak_club_mph_mean"))
    if ball and club: s["smash_factor_mean"] = ball / club
    r = lo.shot_row(0, s, label="policy_det")
    r.update(src=Path(path).name if "gain" not in path else "/".join(Path(path).parts[-2:]), seed=j.get("seed"), gain=gain, force_scale=ek.get("force_scale"),
             gate_pass=j.get("gate_pass"), gate_smash_mean=p.get("smash_factor_mean"), lat_std=p.get("lateral_std"))
    if r["spin_rpm"] is not None and gain: r["spin_source"] = "hand-set by env impact model (no spin model)"
    return r

def md(rows):
    L = ["# Launch-monitor-style report (ADDITIVE; gate pass/fail unchanged)", "",
         "Source: `eval/launch_report.py` over eval_gate JSONs (det policy, 100 eps/seed). Unit/flag logic: `data/launch_output.py` (Data Agent, d6d0f0e). All rows are MODEL-BASED simulation, not measurements of a person.", "",
         f"**Target (published TrackMan driver row)**: {TARGET['club_mph']} mph club -> {TARGET['ball_mph']} ball mph, smash {TARGET['smash']}, launch {TARGET['launch_deg']} deg, spin {TARGET['spin_rpm']} rpm, {TARGET['carry_yd']} yd carry. "
         "The 130 and 132 mph rows are extrapolated upper bounds only (not published), so the 132 mph power tier has no published row to match. Smash/spin thresholds are derived, not published.", "",
         "Smash column = ball mph / impact club mph. `gate smash_mean` is the gate JSON's smash_factor_mean (mean of per-episode ratios; not a true ratio of the speeds shown).", "",
         "| gate file | seed | gain | fs | club mph | ball mph | smash | gate smash_mean | launch deg | spin rpm (source) | carry yd | det lat std m | gate | flags |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda v, n=1: "-" if v is None else (round(v, n) if isinstance(v, float) else v)
    for r in rows:
        L.append(f"| {r['src']} | {r['seed']} | {f(r['gain'],2)} | {r['force_scale']} | {f(r['club_mph'])} | {f(r['ball_mph'])} | {f(r['smash'],3)} | {f(r['gate_smash_mean'],3)} | {f(r['launch_deg'])} | {f(r['spin_rpm'],0)} ({'absent' if r['spin_rpm'] is None else r['spin_source'] if 'hand-set' in r['spin_source'] else 'in input'}) | {f(r['carry_yd'],0)} | {f(r['lat_std'],2)} | {'PASS' if r['gate_pass'] else 'FAIL'} | {'; '.join(r['flags']) or 'ok'} |")
    return "\n".join(L) + "\n"

HELD = "Trainer-reported, file held"
HEADER = "| gate file | seed | gain | fs | club mph | ball mph | smash | gate smash_mean | launch deg | spin rpm (source) | carry yd | det lat std m | gate | flags |"
SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

def held_rows(paths, old_md):
    """Rows whose gate JSON is NOT in this checkout (held under results/imit_private/, never committed): keep the previously
    committed table row verbatim and label it. They cannot be recomputed from main alone."""
    out = []
    for p in paths:
        if (ROOT / p).exists() or Path(p).exists():
            continue
        src = "/".join(Path(p).parts[-2:]) if "gain" in p else Path(p).name
        for line in old_md.splitlines():
            if line.startswith(f"| {src} |"):
                if HELD not in line:
                    cells = line.rstrip().rstrip("|").rstrip()
                    cells = cells[:-2] + HELD if cells.endswith("| ok") else cells + f"; {HELD}"
                    line = cells + " |"
                out.append(line)
                break
    return out

if __name__ == "__main__":
    out_md = ROOT / "results/launch_report.md"
    old_md = out_md.read_text() if out_md.exists() else ""
    names = sys.argv[1:] or DEFAULT
    paths = [str(ROOT / p) for p in names if (ROOT / p).exists() or Path(p).exists()]
    rows = [row(p) for p in paths]
    text = md(rows)
    held = held_rows(DEFAULT, old_md) if not sys.argv[1:] else []
    if held:
        text += ("\nRows below: the gate JSONs are held locally under `results/imit_private/` (not in the repo). Values are copied from the previous "
                 "report and are **Trainer-reported, file held**; they cannot be regenerated from `main` alone.\n\n" + "\n".join([HEADER, SEP] + held) + "\n")
    out_md.write_text(text); print(text)
