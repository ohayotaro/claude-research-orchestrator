---
name: run-experiment
description: Implement the methodology as a Python script under uv, execute, and capture full reproducibility metadata.
when_to_use: After /design-experiment. Re-runnable for replications (different seeds).
inputs:
  - docs/research/methodology.md
  - data/raw/* (as referenced by methodology)
outputs:
  - src/experiments/<name>.py
  - data/results/<run_id>/{metadata.json,results.*,log.txt}
delegated_agent: experiment-runner
next_skill: /analyze-results
---

# /run-experiment

## Steps for the orchestrator

1. **Pre-flight.**
   - Methodology locked (`methodology.md` exists; user-approved).
   - Working tree clean (`git status` empty) — strongly preferred. If dirty, warn the user; the run will be marked `git_clean: false`.
   - `uv` available.
2. **Launch** `experiment-runner` with:
   - Pointer to `methodology.md`.
   - Suggested script name (slug from hypothesis label).
   - Locked seed.
3. **The agent will**:
   - Implement `src/experiments/<name>.py`.
   - Add tests under `tests/` if any non-trivial logic was introduced.
   - Run `uv run python src/experiments/<name>.py --seed <N>`.
   - The `reproducibility-check` hook validates `metadata.json` post-run and blocks the run from completing if metadata is incomplete.
4. **On error**: the `error-to-codex` hook routes the traceback to `codex-debugger`. The orchestrator surfaces the resulting debug report to the user; user decides whether the runner agent applies the fix.
5. **On success**: report `run_id`, key output paths, wall-clock time. **Update Zone C**: `current_phase: experiment`, `last_run_id`, `next_action: "Run /analyze-results"`.

## Replication

To replicate with new seeds, re-invoke this skill with `--seed <N>`. Each seed gets its own `run_id`. Methodology requires ≥ 3 seeds for nondeterministic experiments (see `reproducibility.md`).
