# Contributing

Thanks for your interest. This is a research prototype (simulation only); honest, reproducible results matter more than big numbers.

## Ground rules

1. **Numbers come from committed files.** Any figure in the README or docs must point to a file in `results/` (or another committed source). Label every result as **scripted vs learned** and **deterministic vs stochastic**; never mix them in one row.
2. **Keep the caveats.** The strike-regime caveat, the unverified smash factor and "no trained model qualifies" stay until a committed result changes them.
3. **No big or private artefacts in git:** no videos or GIFs (`.mp4 .mov .gif ...`), zips, model checkpoints (`.zip .pt .pth`), logs, raw mocap, or files over 5 MB. `scripts/smoke_test.py` enforces this.
4. **Data needs a licence and consent.** Every new reference file must be tagged (`data/provenance.py`) and have its source, licence, and (for people) consent recorded. See the data-contribution issue template.
5. **No third-party likeness.** Do not add data, names or claims that imply a real player's swing, endorsement or measurements.
6. Unverified or hypothetical numbers must be marked as such.

## Setup and checks

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.pinned.txt
python3 scripts/smoke_test.py   # must pass
pytest tests                    # must pass (some tests skip without gitignored originals)
```

## Pull requests

- Small, focused commits; describe what changed and which results file backs any claim.
- If you changed `env/`, evaluation code or configs, re-run the gate or `eval/shot_dist` and commit the output JSON; state the protocol (episodes, seed, deterministic/stochastic).
- Do not commit checkpoints. Training scripts and the `args` block in `results/<name>.json` should be enough to reproduce a run.
- Be aware `np.load(..., allow_pickle=True)` is used for reference `.npz` files; only load files you trust.

## Good first areas

See [ROADMAP.md](ROADMAP.md): beating the Stage 6 scripted swing with a learned policy, retraining under the fixed strike regime, ball spin / face metrics, WHAM/GVHMR reconstruction, G1 model.
