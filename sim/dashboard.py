"""Build docs/dashboard.html: static, self-contained (inline CSS, no JS/network). python -m sim.dashboard
Reads results/leaderboard.json, results/golf_simulator_validation.json, results/course_estimates.json."""
import json, os, html, math, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
J = lambda p: json.load(open(os.path.join(ROOT, p)))
e = html.escape


def f(v, nd=1, suf=""):
    return "-" if v is None or (isinstance(v, float) and not math.isfinite(v)) else f"{v:.{nd}f}{suf}"


def build():
    lb, val, crs = J("results/leaderboard.json"), J("results/golf_simulator_validation.json"), J("results/course_estimates.json")
    rows = []
    for m in lb["models"]:
        d, s = m["modes"]["deterministic"], m["modes"]["stochastic"]
        name = m["names"][0] if not m["scripted"] else m["names"][0]
        scripted = bool(m["scripted"]); fs = m["env_kwargs"].get("force_scale")
        cr = (d["contact_rate"] + s["contact_rate"]) / 2
        carry = d.get("mean_carry_yd"); carry = 0.0 if carry is None or not math.isfinite(carry) else carry
        rows.append((cr, carry, m, d, s, name, scripted, fs))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    best = lb["best_qualifying"]
    tr = []
    for i, (cr, carry, m, d, s, name, scripted, fs) in enumerate(rows, 1):
        tag = '<span class="b sc">SCRIPTED (not learned)</span>' if scripted else '<span class="b ln">learned</span>'
        hyp = '<span class="b hy">hypothetical actuators (force_scale %g)</span>' % fs if fs and fs > 1 else ("" if fs else '<span class="b">default env</span>')
        star = " &#9733;" if (not scripted and m["names"][:1] == best[:1] and best[1] in m["names"]) else ""
        tr.append(f"<tr><td>{i}</td><td>{e(' / '.join(m['names']))[:110]}{star}<br>{tag} {hyp}</td><td>{f(d['contact_rate']*100,0,'%')} / {f(s['contact_rate']*100,0,'%')}</td>"
                  f"<td>{f(d.get('mean_carry_yd'),0)}</td><td>{f(d.get('mean_total_yd'),0)}</td><td>{f(d.get('lateral_std'),2)}</td><td>{f(d.get('launch_elev_mean_deg'),1)}</td>"
                  f"<td>{f(d.get('peak_club_mph_mean'),0)}</td><td>{f(d.get('smash_factor_mean'),2)}</td></tr>")
    vt = []
    for blk, title in (("flight_from_published_launch", "Flight model from published launch conditions"), ("impact_model", "Impact model (club speed to ball)")):
        for c in val[blk]["checks"]:
            err = f"{c['error']*100:+.1f}%" if c["error_kind"].startswith("%") else f"{c['error']:+.1f}"
            vt.append(f"<tr><td>{title}</td><td>{c['metric']}</td><td>{c['model']:.2f}</td><td>{c['published']:.2f}</td><td>{err}</td><td class=\"{'ok' if c['passed'] else 'bad'}\">{'PASS' if c['passed'] else 'FAIL'}</td></tr>")
    ct = "".join(f"<tr><td>{e(r['profile'])}</td><td>{r['mean_score']:.1f}</td><td>{r['mean_vs_par']:+.1f}</td><td>{r['p10']:.0f}-{r['p90']:.0f}</td><td>{r['fairways_hit_pct']:.0f}%</td><td>{r['gir_pct']:.0f}%</td></tr>" for r in crs["results"])
    book = "".join(f"<tr><td>{h['n']}</td><td>{h['par']}</td><td>{h['yards']}</td><td>{h['fw_halfwidth_yd']*2:g}</td></tr>" for h in crs["holes"])
    sc = val["flight_from_published_launch"]["shot"]
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Humanoid golf dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
body{{font:15px/1.45 system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 14px;color:#1a2a1a;background:#f6f8f4}}
h1{{margin:.2em 0}} h2{{border-bottom:2px solid #6a9a5a;padding-bottom:3px;margin-top:1.6em}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:13px}} th,td{{border:1px solid #ccd6c6;padding:4px 7px;text-align:left;vertical-align:top}} th{{background:#e4eddf}}
.b{{display:inline-block;font-size:11px;padding:1px 6px;border-radius:9px;background:#ddd;margin:1px 2px}} .sc{{background:#ffd9a8}} .ln{{background:#bfe5b5}} .hy{{background:#f5b7b1}}
.ok{{color:#176b17;font-weight:700}} .bad{{color:#b00020;font-weight:700}} .note{{background:#fff7d6;border-left:4px solid #e0b000;padding:8px 12px;margin:10px 0}}
</style></head><body>
<h1>Humanoid golf: evaluation dashboard</h1>
<p>Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} (America/New_York) from <code>results/leaderboard.json</code>, <code>results/golf_simulator_validation.json</code>, <code>results/course_estimates.json</code>. Regenerate: <code>python -m sim.dashboard</code>.</p>
<div class="note"><b>Honest labels.</b> Every leaderboard row uses boosted actuators (force_scale &gt; 1) unless marked otherwise: <b>hypothetical actuators</b>, not a real robot. Rows tagged SCRIPTED are a hand-written swing, not learned. Leaderboard yards use the MuJoCo-physics ball (smash about 1.0, a known artifact). Launch-monitor and course numbers are <b>model-based</b> (analytic ball model / Monte Carlo), not measured.</div>
<h2>Leaderboard (ranked by true contact, then mean carry; star = best qualifying learned model)</h2>
<table><tr><th>#</th><th>Model</th><th>Contact det / stoch</th><th>Carry yd (det)</th><th>Total yd (det)</th><th>Lateral std m</th><th>Launch deg</th><th>Peak club mph</th><th>Smash</th></tr>{''.join(tr)}</table>
<p>Episodes per row: {lb['episodes']}, seed base {lb['seed_base']}. Total equals carry when the episode ends at first landing (no roll). Qualification: {e(json.dumps(lb['qualify_criterion']))}.</p>
<h2>Launch-monitor validation (analytic ball model vs TrackMan PGA Tour driver average)</h2>
<p>Benchmark: 113 mph club, 167 mph ball, smash 1.48, 10.9&deg; launch, 2686 rpm, 32 yd apex, 38&deg; landing, <b>275 yd carry</b> (TrackMan published PGA Tour averages; USGA Equipment Specifications Research, Table&nbsp;2). Model from those launch conditions: carry {sc['carry_yd']:.0f} yd, total {sc['total_yd']:.0f} yd, apex {sc['apex_yd']:.0f} yd.</p>
<table><tr><th>Check</th><th>Metric</th><th>Model</th><th>Published</th><th>Error</th><th>Result</th></tr>{''.join(vt)}</table>
<p>The simple impact model over-predicts backspin (FAIL rows above are reported, not hidden). One benchmark row only; spot check, not a full calibration.</p>
<h2>Course-mode estimates ({e(crs['label'])})</h2>
<p>Synthetic example course (invented), par {crs['par']}, {crs['total_yards']} yd. Dispersion from the simulator's leaderboard data; putting, chipping, rough and hazard effects are assumed constants. Profile B is a what-if (sim spread scaled to tour-average carry), not an achieved result.</p>
<table><tr><th>Profile</th><th>Mean score</th><th>vs par</th><th>p10-p90</th><th>Fairways</th><th>GIR</th></tr>{ct}</table>
<details><summary>Yardage book (synthetic example course)</summary><table><tr><th>Hole</th><th>Par</th><th>Yards</th><th>Fairway width yd</th></tr>{book}</table></details>
</body></html>"""
    out = os.path.join(ROOT, "docs", "dashboard.html")
    open(out, "w").write(page)
    return out


if __name__ == "__main__":
    print(build())
