---
name: paper-deep-read
description: Deep-read a single paper (URL / DOI / local PDF) via Gemini and persist a structured note under docs/research/papers/<slug>.md. Optionally append a BibTeX entry.
when_to_use: When you need a thorough understanding of one specific paper without running a full /literature-review.
inputs:
  - URL, DOI, or local PDF path (required)
  - Optional: cite key suggestion (auto-derived if omitted)
outputs:
  - docs/research/papers/<slug>.md (structured note)
  - docs/references.bib (appended, if user accepts)
  - .claude/logs/cli/<ISO>-gemini-deepread-*.md
delegated_agent: gemini-explore (with the literature-reviewer agent for the BibTeX append step)
next_skill: /extend-literature (to weave the finding into lit-review.md), or any
---

# /paper-deep-read

Produces a single structured note for one paper. Complementary to `/literature-review` (which surveys many shallowly) and `/ask-gemini` (which is one-shot, no persistence).

## Steps for the orchestrator

1. **Resolve the paper.** Accept any of: URL, DOI (`10.xxxx/...`), arXiv ID (`2401.xxxxx`), or local file path.
2. **Derive a slug** for the filename. Pattern: `<firstauthor-lower><year>-<3-word-tag>`. e.g. `vaswani2017-attention-is-all-you-need.md`. If a `papers/<slug>.md` already exists, ask the user whether to overwrite or append a "Reread <date>" section.
3. **Ensure `docs/research/papers/` exists.** Create if missing.
4. **Invoke Gemini** to extract a structured note. Prompt scaffold:
   ```
   You are reading a single research paper for a careful note. Return ONLY
   markdown matching the schema below. Cite every numerical claim with the
   section / table / figure number from the paper.

   ## Bibliographic
   - Title:
   - Authors:
   - Year:
   - Venue:
   - DOI / arXiv ID / URL:
   - Preprint: yes/no

   ## TL;DR (3 sentences)

   ## Problem and motivation

   ## Approach (methods, in 1-2 paragraphs)

   ## Key results (with paper-internal references)
   - ...

   ## Strengths

   ## Weaknesses / open questions

   ## Most-cited claims (those a downstream paper would cite this for)
   - claim: ...
     where in paper: §X / Table Y

   ## Datasets / artifacts mentioned
   - name | url | license

   ## How this relates to <our RQ from CLAUDE.md Zone B>
   - 2-4 sentences

   PAPER:
   <attach via --file, OR paste URL>
   ```
   ```bash
   gemini -p "<above>" --file <pdf-or-url>
   ```
5. **Save the note** to `docs/research/papers/<slug>.md`. Add a YAML frontmatter:
   ```yaml
   ---
   cite_key: <derived>
   source: <url-or-path>
   read_at: <ISO date>
   reader: paper-deep-read skill (Gemini)
   ---
   ```
6. **Offer to add a BibTeX entry** to `docs/references.bib`. If the user accepts, hand off to `literature-reviewer` agent's BibTeX-append routine (it will dedupe by DOI).
7. **Suggest next step**: `/extend-literature` to weave this paper into the running lit-review.md, or just leave it as a standalone note.
8. **Update Zone C** lightly: append the slug to `recent_artifacts`. Do not change `current_phase`.

## Hard rules

- Never overwrite an existing `papers/<slug>.md` without confirmation.
- If Gemini cannot access the source (paywall, 404), report that and ask the user to provide a local PDF.
- Numerical claims in the note must be tied to a section/table/figure number in the paper. If Gemini cannot do that, mark the claim with `[location unverified]`.
- The note is **English** (per `language.md`). The orchestrator translates the TL;DR to Japanese for the user when reporting.
