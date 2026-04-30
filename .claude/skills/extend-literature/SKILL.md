---
name: extend-literature
description: Append a focused subtopic survey to the existing lit-review.md without rewriting it. Useful when a new question emerges mid-project and the literature needs an incremental update.
when_to_use: After /literature-review has produced an initial survey, when you need to (a) drill into a subtopic that was skimmed, (b) add coverage of work published since the original review, or (c) integrate notes from /paper-deep-read.
inputs:
  - docs/research/lit-review.md (existing — required)
  - User-specified subtopic or scope (free-text)
  - Optional: list of paper notes from docs/research/papers/ to weave in
outputs:
  - docs/research/lit-review.md (extended; original sections untouched)
  - docs/references.bib (extended)
  - .claude/logs/cli/<ISO>-litrev-extend-*.{json,md}
delegated_agent: literature-reviewer (extend mode)
next_skill: /identify-gaps (if the new coverage suggests new gaps), or any
---

# /extend-literature

The diff-mode counterpart to `/literature-review`. Original lit-review.md content is **never modified**; new coverage is appended under a new dated section.

## Steps for the orchestrator

1. **Pre-flight.** `docs/research/lit-review.md` must exist and have at least one theme. If not, suggest `/literature-review` first.
2. **Clarify scope with the user** (Japanese):
   - Which subtopic? (Free-text or pick from existing themes.)
   - Time window (e.g. "since 2025-01") if updating for recency.
   - How many papers to add (default 5–15).
   - Any specific papers from `docs/research/papers/` to weave in.
3. **Launch** `literature-reviewer` agent in **extend mode** with the scope, the existing lit-review.md (read-only), and the references.bib cite-key list (so it does not duplicate entries).
4. **Agent behavior** (extend mode):
   - Performs the same Gemini-driven retrieval as `/literature-review` but limited to the scope.
   - Deduplicates against existing cite keys.
   - Writes a **new appended section** to `lit-review.md`:
     ```markdown
     ## Update <ISO date> — <subtopic name>

     _Scope: <description>; <N> new papers added._

     ### Synthesis
     <2–4 paragraphs>

     ### New papers
     | Cite key | Title | Venue | Year | Why added |

     ### Implications for our RQ
     <1–2 paragraphs>
     ```
   - Appends new BibTeX entries to `references.bib` (sorted; no in-place reordering of existing entries).
5. **Receive handoff**: number of new papers, whether any prior gap from `gaps.md` is now closed (suggesting `/identify-gaps` re-run).
6. **Update Zone C**: `last_skill_run: extend-literature`, `next_action` based on handoff.

## Hard rules

- **Never edit existing sections of `lit-review.md`.** Only append. If the user wants a clean rewrite, they should explicitly run `/literature-review` again (which overwrites).
- **Never delete BibTeX entries.** Only append.
- Cite keys must be unique. The agent must check `references.bib` before assigning new keys.
- If retrieval surfaces a paper that contradicts a finding cited in the existing review, flag it in the "Implications for our RQ" subsection rather than editing the original section.

## Common variants

- **Recency update**: scope = "papers published since <date> on <theme>".
- **Drill-down**: scope = "deepen coverage of <theme>; we currently cite N papers, get to 2N".
- **Integrate deep-reads**: scope = "weave the following paper-deep-read notes into the appropriate themes: <paths>".
