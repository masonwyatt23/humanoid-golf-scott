#!/usr/bin/env python3
"""Dependency-light repo smoke test (stdlib only; no mujoco/torch needed).

Checks: (1) all tracked .py files compile, (2) no tracked video/zip/.pt/h5/MUJOCO_LOG
files and nothing over 5 MB, (3) every results/*.json parses, (4) README links to
local files/results that exist.  Run: python scripts/smoke_test.py
"""
import json, os, py_compile, re, subprocess, sys, tempfile

ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True,
                               cwd=os.path.dirname(os.path.abspath(__file__))).strip()
os.chdir(ROOT)
BAD_EXT = (".mp4", ".mov", ".avi", ".mkv", ".webm", ".gif", ".zip", ".tar", ".gz", ".7z",
           ".pt", ".pth", ".h5", ".hdf5")
MAX_BYTES = 5 * 1024 * 1024
errors = []
tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
tracked = [f for f in tracked if os.path.isfile(f)]

# 1. compile
n = 0
for f in tracked:
    if f.endswith(".py"):
        n += 1
        try:
            py_compile.compile(f, cfile=os.path.join(tempfile.gettempdir(), "smoke.pyc"), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"compile: {f}: {e.msg.strip()}")
print(f"[1] py_compile: {n} files")

# 2. hygiene
for f in tracked:
    low = f.lower()
    if low.endswith(BAD_EXT) or "mujoco_log" in os.path.basename(low):
        errors.append(f"forbidden file tracked: {f}")
    elif os.path.getsize(f) > MAX_BYTES:
        errors.append(f"file over 5 MB: {f} ({os.path.getsize(f)} bytes)")
print(f"[2] hygiene: {len(tracked)} tracked files checked")

# 3. results json
n = 0
for f in tracked:
    if f.startswith("results/") and f.endswith(".json"):
        n += 1
        try:
            with open(f) as fh:
                json.load(fh)
        except Exception as e:
            errors.append(f"bad json: {f}: {e}")
print(f"[3] results json: {n} files parsed")

# 4. README links
text = open("README.md", encoding="utf-8").read()
targets = set(re.findall(r"\]\(([^)\s]+)\)", text))
targets |= set(re.findall(r"`((?:results|docs|data|eval|train|env|scripts|tests|configs|imitation)/[\w./\-]+\.\w+)`", text))
n = 0
for t in sorted(targets):
    if re.match(r"^(https?:|mailto:|#)", t) or any(c in t for c in "*<>{}"):
        continue
    p = t.split("#")[0]
    if not p:
        continue
    n += 1
    if not os.path.exists(p):
        errors.append(f"README references missing path: {p}")
print(f"[4] README links: {n} local paths checked")

if errors:
    print("\nFAIL:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("\nOK: smoke test passed")
