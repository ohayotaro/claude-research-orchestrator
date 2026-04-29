---
name: generate-hypothesis
description: Generate candidate hypotheses from gaps, critiqued by Codex, narrowed to 3–6 survivors.
when_to_use: After /identify-gaps.
inputs:
  - docs/research/gaps.md
  - docs/research/lit-review.md
outputs:
  - docs/research/hypotheses.md
  - .claude/logs/cli/<ISO>-codex-hypothesis-critique.md
delegated_agent: hypothesis-generator (full pipeline including Codex critique)
next_skill: /design-experiment
---

# /generate-hypothesis

## Steps for the orchestrator

1. **Pre-flight.** `gaps.md` must exist with at least one gap.
2. **Codex availability check.** If `.claude/logs/setup-status.json` shows `codex_available: false`, warn the user — the critique phase will fall back to a Claude subagent acting as a strict critic, which is weaker. Ask whether to proceed.
3. **Launch** `hypothesis-generator` agent in **full mode**:
   - Diverge: 10–15 candidates.
   - Codex critique.
   - Converge: 3–6 survivors.
4. **Confirm with user** (Japanese): present the 3–6 survivors and ask which to advance to `/design-experiment`. The user may pick one, several (parallel tracks), or ask for revisions.
5. **Update Zone B's `hypotheses` list** with the user-selected survivors.
6. **Update Zone C**: `current_phase: hypothesis`, `next_action: "Run /design-experiment for H<n>"`.
