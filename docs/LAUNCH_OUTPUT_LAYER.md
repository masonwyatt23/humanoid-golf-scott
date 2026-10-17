# Launch-monitor / hole-play output layer

`python -m data.launch_output <shots_*.json|gate_*.json ...> [--hole-yd 450] [--ref-spin] [--json out.json] [--md out.md]` (tests: `tests/test_launch_output.py`). Read-only on inputs; new files only under data/ docs/ tests/.

**Inputs found in repo (inspected read-only):**
- Per-shot list (`results/shots_*.json`): carry_yd/total_yd (also carry, total_dist in m), launch_elev_deg, ball_speed_sep and peak_ball_speed (m/s), impact_club_speed (m/s), final_y (m), true_contact. **No spin.**
- `eval.eval_gate` JSON (`results/gate_*.json`): aggregates only per policy (policy_det / policy_stoch / scripted_zero_residual): mean_carry, mean_distance (metres, total), launch_elev_mean_deg, smash_factor_mean, peak_club_mph_mean, contact_rate. No per-shot rows, no spin. These give one AGGREGATE row per policy, not shots.

**Output per row:** carry_yd, total_yd, spin_rpm (null, spin_source "absent" unless the input has spin_rpm/backspin_rpm; `--ref-spin` adds a reference-table value labelled reference_lookup, never measured), launch_deg, smash, ball_mph, club_mph, optional remaining_to_pin_yd and lateral (with `--hole-yd`), flags.

**Flags** (limits from docs/LAUNCH_TARGETS_120_132.md on branch launch-tables-only; published ceiling, derived warn bands): smash FAIL > 1.50, WARN > 1.49, WARN < 1.30; spin PASS 1800-3000, WARN 1500-1800/3000-3500, FAIL <1200 or >4000 (derived); launch WARN outside the eval_gate 5-20 deg window.

**Findings on current repo data (not fixes; the layer only reports):**
- `smash_factor_mean` in gate JSONs is 0.90-0.91 for imit8 policy and 10.2 for the scripted baseline; these are not ball-separation smash ratios (scripted baseline impact club speed ~0.2 m/s), so the layer flags them. Treat that metric as unreliable.
- `shots_v4power_8000.json` (132 mph club): ball_speed_sep gives smash 0.78-1.35, carry up to 356 yd, above the extrapolated TrackMan 332 yd at 132 mph; ball_speed_sep is the env separation velocity, so the smash/carry mismatch points to env impact-model issues, not to a real result.
- `peak_ball_speed` is used only when separation speed is missing, and the row notes it.
