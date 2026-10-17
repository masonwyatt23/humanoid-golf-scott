"""Provenance audit of committed training-result JSONs (read-only; never guesses missing values).

  python scripts/audit_provenance.py            # prints markdown table
  python scripts/audit_provenance.py --json     # machine-readable

For each results/<run>.json holding an `args` block (ppo_v3*, ppo_v4*, imit*), records which provenance fields exist.
"""
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PATTERNS = ["ppo_v3tiny_*", "ppo_v3flt_*", "ppo_v4yaw_*", "imit_w*", "imit2_*", "imit3_*"]


def commit_known(h):
    if not h:
        return None
    r = subprocess.run(["git", "cat-file", "-e", f"{h}^{{commit}}"], cwd=ROOT, capture_output=True)
    return r.returncode == 0


def on_main(h):
    if not h:
        return None
    r = subprocess.run(["git", "merge-base", "--is-ancestor", h, "HEAD"], cwd=ROOT, capture_output=True)
    return r.returncode == 0


def audit(name):
    d = json.loads((RES / f"{name}.json").read_text())
    a = d.get("args") or {}
    ek = d.get("env_kwargs_full")
    gate = RES / f"gate_{name}.json"
    g = json.loads(gate.read_text()) if gate.exists() else None
    row = {"run": name, "args_block": bool(a), "seed": a.get("seed"), "git_head": d.get("git_head"),
           "git_head_resolves": commit_known(d.get("git_head")), "git_head_on_current_branch": on_main(d.get("git_head")),
           "gate_json": bool(g), "gate_pass": (g or {}).get("gate_pass"),
           "force_scale": a.get("force_scale", (ek or {}).get("force_scale")),
           "tempo_scale": a.get("tempo_scale", (ek or {}).get("tempo_scale")),
           "style_ref_key": "style_ref" in a, "style_ref": a.get("style_ref"), "style_weight": a.get("style_weight"),
           "track_set_key": bool(ek) and "track_set" in ek, "track_set": (ek or {}).get("track_set"),
           "track_weight": (ek or {}).get("track_weight", a.get("track_weight")),
           "env_kwargs_full_in_run_json": bool(ek),
           "env_kwargs_in_gate_json": bool(g and g.get("env_kwargs")),
           "gate_track_set": ((g or {}).get("env_kwargs") or {}).get("track_set", "absent"),
           "model_xml": a.get("model_xml", (ek or {}).get("model_xml")),
           "config": a.get("config"), "contact_damp": a.get("contact_damp"), "impact_model": a.get("impact_model")}
    refs_used = bool(row["style_ref"]) or bool(row["track_set"])
    row["reference_manifest_recorded"] = bool(row["track_set"]) or (None if not refs_used else False)
    row["reference_manifest_hash_recorded"] = any(k in a for k in ("manifest_sha", "refset_sha", "manifest_hash"))
    row["model_checkpoint_hash_recorded"] = any(k in a for k in ("model_sha", "checkpoint_sha"))
    return row


def main():
    names = sorted({Path(p).stem for pat in PATTERNS for p in glob.glob(str(RES / f"{pat}.json"))})
    rows = [audit(n) for n in names]
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return
    for r in rows:
        print(r["run"], {k: v for k, v in r.items() if k != "run"})


if __name__ == "__main__":
    main()
