"""
Compare policies trained on different pure-swing styles.

Usage:
    python -m eval.compare_styles [--episodes 20] [--styles scott rory] \
        [--models-dir models] [--out-dir eval/results] [--seed 0]

Writes eval/results/style_comparison.md and .json. Styles without a model are
listed as "no model" and never given numbers.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

STYLES = ["scott", "scheffler", "rory", "average"]


def _f(x, fmt):
    return "n/a" if x != x else format(x, fmt)  # NaN-safe


def make_table(results: List[Dict]) -> str:
    hdr = ("| Style | Episodes | Contact rate | Mean dist (m) | Std dist (m) | Max dist (m) "
           "| Dist CV | Club path dispersion (m) | True contact | Carry (landed) | Peak ball speed (m/s) | DTW style match (rad) |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for r in results:
        if r.get("status") == "no_model":
            rows.append(f"| {r['style']} | – | no model | – | – | – | – | – | – | – | – | – |")
        else:
            rows.append(
                f"| {r['style']} | {r['episodes']} | {r['contact_rate']*100:.0f}% "
                f"| {_f(r['mean_distance'], '.2f')} | {_f(r['std_distance'], '.2f')} "
                f"| {_f(r['max_distance'], '.2f')} | {_f(r['cv_distance'], '.3f')} "
                f"| {_f(r['path_dispersion'], '.4f')} | {r.get('true_contact_rate', float('nan'))*100:.0f}% "
                f"| {_f(r.get('mean_carry_landed', float('nan')), '.2f')} ({r.get('carry_landed_rate', float('nan'))*100:.0f}% landed) "
                f"| {_f(r.get('mean_peak_ball_speed', float('nan')), '.2f')} "
                f"| {_f(r['style_match_dtw'], '.3f') if r.get('style_match_dtw') is not None else 'n/a'} |")
    return "\n".join([hdr] + rows)


def best(results: List[Dict]) -> str:
    ok = [r for r in results if "mean_distance" in r]
    if not ok:
        return "No trained models found; nothing to rank."
    d = max(ok, key=lambda r: r["mean_distance"])
    c = max(ok, key=lambda r: r["contact_rate"])
    s = min((r for r in ok if r["path_dispersion"] == r["path_dispersion"]),
            key=lambda r: r["path_dispersion"], default=None)
    lines = [f"- Best mean distance: {d['style']} ({d['mean_distance']:.2f} m)",
             f"- Best contact rate: {c['style']} ({c['contact_rate']*100:.0f}%)"]
    if s:
        lines.append(f"- Most consistent club path: {s['style']} ({s['path_dispersion']:.4f} m)")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--episodes", type=int, default=20)
    p.add_argument("--styles", nargs="+", default=STYLES)
    p.add_argument("--models-dir", default="models")
    p.add_argument("--out-dir", default="eval/results")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--stochastic", action="store_true")
    args = p.parse_args(argv)
    if args.episodes < 1:
        p.error("--episodes must be >= 1")

    results = []
    for style in args.styles:
        mp = Path(args.models_dir) / f"ppo_{style}"
        if not mp.with_suffix(".zip").exists():
            results.append({"style": style, "status": "no_model"})
            continue
        from eval.evaluate import evaluate_model
        results.append(evaluate_model(str(mp), style, args.episodes, args.seed, not args.stochastic))

    table = make_table(results)
    md = (f"# Style comparison\n\nEpisodes per style: {args.episodes}, seed base {args.seed}, "
          f"{'stochastic' if args.stochastic else 'deterministic'} actions.\n"
          "Distance = final ball x (m), not true carry. Dist CV = std/mean. "
          "Path dispersion = mean 3D std of club head across episodes.\n\n"
          f"{table}\n\n{best(results)}\n")
    print(md)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "style_comparison.md").write_text(md)
    (out / "style_comparison.json").write_text(json.dumps(results, indent=2))
    print(f"Saved to {out}/style_comparison.md")


if __name__ == "__main__":
    main()
