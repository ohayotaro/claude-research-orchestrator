---
name: init-research
description: Bootstrap a new research project. Interactively collects domain, theme, RQ, paper format, runtime; writes CLAUDE.md Zone B; scaffolds docs/, src/, data/, notebooks/, tests/. Run this first.
when_to_use: First skill in a fresh project. Also re-runnable to update Zone B.
inputs: User answers via AskUserQuestion (Japanese)
outputs:
  - CLAUDE.md (Zone B updated)
  - docs/research/{lit-review,gaps,hypotheses,methodology,analysis,discussion}.md (placeholders)
  - docs/paper/draft.md or docs/paper/main.tex (placeholder)
  - docs/references.bib (empty)
  - src/{experiments,analysis,utils}/__init__.py
  - data/{raw,processed,results}/.gitkeep
  - tests/test_smoke.py
  - notebooks/.gitkeep
  - .claude/paper-template-config.json
delegated_agent: orchestrator (no subagent)
next_skill: /literature-review
---

# /init-research

Initializes a research project from the orchestrator template. The orchestrator runs this directly — no subagent.

## Steps

1. **Read** `CLAUDE.md` and `.claude/logs/setup-status.json` (if present).
2. **Ask the user** (Japanese) for the project parameters via `AskUserQuestion`. Suggested questions and defaults:
   - 研究分野（domain）— free text. Examples: computer-science, biology, social-science.
   - 研究テーマ（theme）— free text, one line.
   - リサーチクエスチョン（RQ）— free text, one sentence. Translate to English internally.
   - サブクエスチョン（sub_questions）— optional, free text list.
   - 既存の仮説があれば（hypotheses）— optional, free text list.
   - 論文出力言語（output_language.paper）— en (default) / ja / other.
   - 論文フォーマット（paper_format）— `markdown_bibtex` (default) / `latex`.
   - 実行環境のPythonバージョン（runtime.python_version）— default 3.12.
   - 想定投稿先（target_venue）— optional.
   - データ機微度（ethics.data_sensitivity）— none / low / medium / high.
   - IRB必要か（ethics.irb_required）— bool.
3. **Build a Zone B YAML** from the answers. Preserve the user's free-text RQ verbatim (Japanese OK in Zone B). Keep `status: initialized`.
4. **Write Zone B** by replacing the content between `<!-- ZONE_B_BEGIN -->` and `<!-- ZONE_B_END -->` in `CLAUDE.md`. Do not touch Zone A or Zone C.
5. **Scaffold directories** (idempotent):
   ```
   docs/research/
   docs/paper/
   src/experiments/  src/analysis/  src/utils/
   data/raw/  data/processed/  data/results/
   notebooks/
   tests/
   ```
6. **Create placeholder files** (only if they do not exist):
   - `docs/research/lit-review.md` — header only.
   - `docs/research/gaps.md`, `hypotheses.md`, `methodology.md`, `analysis.md`, `discussion.md` — header only.
   - `docs/references.bib` — empty.
   - If `paper_format == markdown_bibtex`: `docs/paper/draft.md` with the front matter from `paper-writer` agent's contract.
   - If `paper_format == latex`: `docs/paper/main.tex` with a minimal article preamble + `\bibliography{../references}`.
   - `src/experiments/__init__.py`, `src/analysis/__init__.py`, `src/utils/__init__.py` (empty).
   - `src/utils/repro.py` — copy verbatim from `.claude/templates/repro.py`. Reproducibility helper used by every experiment script.
   - `src/utils/viz.py` — copy verbatim from `.claude/templates/viz.py`. Publication / presentation matplotlib styling and palette helpers (`apply_publication_style`, `apply_presentation_style`, `save_figure`, `OKABE_ITO`).
   - `tests/test_smoke.py` — imports each src module to check the package is wired.
   - `data/raw/.gitkeep`, `data/processed/.gitkeep`, `data/results/.gitkeep`, `notebooks/.gitkeep`.
7. **Write `.claude/paper-template-config.json`** with `{"paper_format": "...", "target_venue": "..."}`.
8. **Append** to `.claude/logs/init-research.log` an ISO-stamped record of the run.
9. **Update Zone C** of `CLAUDE.md` to set `current_phase: literature` and `next_action: "Run /literature-review"`.
10. **Report** to the user (Japanese) a summary: paths created, next suggested skill.

## Idempotence rules

- Re-running `/init-research` is allowed and **only** rewrites Zone B and `paper-template-config.json`. It does **not** overwrite any existing `docs/research/*.md` content (only creates them if absent).
- It does **not** touch existing files under `src/`, `data/`, `tests/`.

## Hard rules

- Do not delete user content. If a placeholder already has more than the header, leave it alone.
- Do not change Zone A.
- The `git_clean` check in any later experiment requires this repo to be a git repo. After scaffold, suggest `git init && git add -A && git commit -m "init research scaffold"` — but do not run it without user confirmation.

## Source of starter scripts

`src/utils/repro.py` and `src/utils/viz.py` are copied verbatim from
`.claude/templates/`. The orchestrator template tracks them as real Python
files under `.claude/templates/` so they can be linted and tested in the
template repo without having to maintain inline copies in this SKILL.md.

| Copy from | Copy to |
|---|---|
| `.claude/templates/repro.py` | `src/utils/repro.py` |
| `.claude/templates/viz.py`   | `src/utils/viz.py` |

If these template files are absent (e.g. an old-template install), fall back
to fetching from the upstream repo at the same paths and warn the user.
