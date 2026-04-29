---
name: identify-gaps
description: Extract concrete, actionable research gaps from the literature review.
when_to_use: After /literature-review.
inputs:
  - docs/research/lit-review.md
outputs:
  - docs/research/gaps.md
delegated_agent: hypothesis-generator (gap-extraction phase)
next_skill: /generate-hypothesis
---

# /identify-gaps

## Steps for the orchestrator

1. **Pre-flight.** `docs/research/lit-review.md` must exist and have at least 3 themes. If not, suggest `/literature-review` first.
2. **Launch** `hypothesis-generator` agent in **gap mode** (a focused prompt that extracts gaps without yet generating hypotheses). The agent produces `docs/research/gaps.md` with:

```markdown
# Research gaps for: <RQ>

_Derived from lit-review.md as of <ISO>._

## G1: <gap>
- **Type**: empirical | theoretical | methodological | applied
- **Evidence in literature**: which themes / papers reveal it [@cite; @cite].
- **Why it matters**: ...
- **Tractability**: high | medium | low (and why).
- **Adjacent work**: closest existing approaches.

## G2: ...

## Summary
<2–4 sentences ranking the gaps by promise.>
```

3. **Update Zone C**: `current_phase: gap`, `next_action: "Run /generate-hypothesis"`.
4. **Report** to user (Japanese): list of gaps and tractability ranking.

## Hard rules

- A "gap" must be concrete enough to translate into a hypothesis. "More work is needed" is not a gap; "Whether X holds for population Y" is.
- Cite the literature sources for every claimed gap.
