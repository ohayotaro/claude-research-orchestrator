---
name: discuss-results
description: Draft the discussion — implications, mechanisms, limitations, future work — connecting results back to the literature.
when_to_use: After /analyze-results.
inputs:
  - docs/research/analysis.md
  - docs/research/lit-review.md
  - docs/research/methodology.md
  - docs/research/hypotheses.md
outputs:
  - docs/research/discussion.md
delegated_agent: discussant
next_skill: /write-paper
---

# /discuss-results

## Steps for the orchestrator

1. **Launch** `discussant`. Provide pointers to all four research notes.
2. **Receive draft.** Cross-check that:
   - Every claim cites prior work where applicable.
   - Limitations include statistical power, generalizability, and reproducibility caveats specific to this run.
   - At least one future-work item is concrete enough that a different team could pick it up.
3. **User review.** Show the user (Japanese) the discussion summary and ask for additions / corrections before locking.
4. **Update Zone C**: `current_phase: discussion`, `next_action: "Run /write-paper"`.
