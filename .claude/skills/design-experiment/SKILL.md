---
name: design-experiment
description: Specify variables, sample size, statistical test, and reproducibility controls for a hypothesis. Validated by Codex.
when_to_use: After /generate-hypothesis. Once per hypothesis being tested.
inputs:
  - docs/research/hypotheses.md (specific H<n>)
  - CLAUDE.md Zone B (ethics, data sensitivity)
outputs:
  - docs/research/methodology.md (or appended section per hypothesis)
  - .claude/logs/cli/<ISO>-codex-methodology.md
delegated_agent: methodology-designer
next_skill: /run-experiment
---

# /design-experiment

## Steps for the orchestrator

1. **Disambiguate which hypothesis.** If `hypotheses.md` lists multiple survivors, ask the user (Japanese) which H<n> to design for, or whether to design parallel methodologies.
2. **Launch** `methodology-designer` with the chosen hypothesis.
3. **Iterate with Codex.** The agent will loop until Codex returns no high-severity issues, or surface unfixable issues to the orchestrator.
4. **Final user confirmation.** Show the user (Japanese) the locked methodology summary: variables, n, test, seed, expected runtime. **The methodology is now pre-registered** — once accepted, do not change the primary outcome or test without recording the change in methodology.md as a deviation.
5. **Update Zone B**: increment a `methodology_locked_at` timestamp.
6. **Update Zone C**: `current_phase: design`, `next_action: "Run /run-experiment"`.

## Hard rules

- Once `methodology.md` is locked and the user has approved, any later change is a **deviation** and must be added under a "Deviations from pre-registration" heading with a timestamped reason.
