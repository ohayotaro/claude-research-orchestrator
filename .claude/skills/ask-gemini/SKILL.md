---
name: ask-gemini
description: Ad-hoc one-shot Gemini call for quick web/multimodal lookups. Does NOT update lit-review.md or references.bib — use /literature-review for formal surveys.
when_to_use: "Quick: find me 3 papers on X" / "describe this figure" / "what does this PDF say" — anything multimodal that does not warrant a full lit-review pass.
inputs:
  - User prompt (free-text)
  - Optional: file path (PDF / image / audio / video)
outputs:
  - Gemini response shown inline to the user (Japanese-translated summary by orchestrator)
  - .claude/logs/cli/<ISO>-gemini-*.md (full I/O captured by log-cli-tools hook)
delegated_agent: gemini-explore (or direct gemini CLI call from orchestrator)
next_skill: any
---

# /ask-gemini

A lightweight escape hatch to Gemini outside the formal `/literature-review` pipeline. **Does not modify any `docs/` file** — pure read-only retrieval.

## Steps for the orchestrator

1. **Check Gemini availability.** Read `.claude/logs/setup-status.json`. If `gemini_available: false`, warn the user and offer to fall back to Claude `WebFetch` (less capable for PDFs / images).
2. **Translate the user's intent into a structured Gemini prompt.** Always specify output format. Defaults:
   - "find papers on X" → request a JSON list of 3–10 papers with `title, authors, year, venue, doi_or_url, one_paragraph_summary, key_finding`. Mark preprints.
   - "describe this figure / image" → markdown with axis labels, units, key trends, numerical values where extractable.
   - "summarize this PDF" → markdown with sections: abstract, methods, key findings, limitations.
3. **Invoke Gemini.**
   ```bash
   gemini -p "<structured prompt>" [--file <path>]
   ```
   The `log-cli-tools.py` hook captures both prompt and response to `.claude/logs/cli/`.
4. **Translate the result for the user** (Japanese summary), and **show the cli log path** so they can read the full English response if needed.
5. **Do not write to `docs/`.** If the user wants the result persisted into the formal lit review, suggest `/extend-literature` or `/paper-deep-read`.

## Hard rules

- One-shot only. Do not chain multiple Gemini calls within one `/ask-gemini` invocation; if you need a multi-step retrieval, use `/literature-review` or `/extend-literature`.
- If Gemini returns no source URL/DOI for a factual claim, surface that clearly to the user — do not silently treat it as fact.
- Never modify `docs/references.bib` from this skill. Use `/extend-literature` for that.

## Examples

| User says (Japanese) | Orchestrator dispatches |
|---|---|
| "diffusion model の最新サーベイ論文を3本だけ" | structured JSON request, 3 papers, sorted by recency |
| "この PDF（path）の methods だけ要約して" | summarize-PDF prompt scoped to methods section, with `--file` |
| "この図（path）の y 軸の単位は？" | image-description prompt, focused question |
