---
name: peer-review
description: Strict, structured peer review of the current draft via Codex. Produces docs/paper/review-N.md.
when_to_use: After /write-paper, before submission, and after each major revision.
inputs:
  - docs/paper/draft.md or docs/paper/main.tex
  - docs/research/{methodology,analysis}.md
  - docs/references.bib
outputs:
  - docs/paper/review-<n>.md
  - .claude/logs/cli/<ISO>-codex-review-<n>.md
delegated_agent: peer-reviewer
next_skill: /revise
---

# /peer-review

## Steps for the orchestrator

1. **Pre-flight.** Draft exists. Codex available — if not, warn the user that the review will fall back to a Claude critic and is weaker.
2. **Launch** `peer-reviewer`. The agent picks the next `review-<n>.md` filename, drives Codex, and verifies Codex's claims against the actual files.
3. **Receive** the structured review. Surface to the user (Japanese):
   - Overall recommendation (accept / minor / major / reject).
   - Counts: blockers, majors, minors, nits.
   - Top 3 issues to address first.
4. **Update Zone C**: `current_phase: review`, `next_action: "Run /revise to address review-<n>.md"`.
