# Language policy

There is exactly one Japanese-language surface in this repository: **the chat between the user and the orchestrator**. Everything else is English.

## Japanese (Japanese-speaking user only)

- Orchestrator's chat replies to the user.
- `AskUserQuestion` question text and option labels.
- `/init-research` interactive Q&A.
- Hook user-facing warning / status strings (e.g. citation-guard's "引用が見つかりません" message).
- Skill execution status output shown to the user.
- `session-start.py` / `session-end.py` screen output.

## English (everything else)

- All code: Python in `src/`, `tests/`, `scripts/`, hooks under `.claude/hooks/`. Including comments and variable names.
- All agent definitions under `.claude/agents/*.md` (frontmatter, body, handoff contracts).
- All skill definitions under `.claude/skills/**/SKILL.md`.
- All rules under `.claude/rules/*.md` including this file.
- `CLAUDE.md` (Zones A, B, C).
- `README.md` (a 2–3 line Japanese intro at the top is permitted; the rest is English).
- All `docs/research/*.md` (lit-review, gaps, hypotheses, methodology, analysis, discussion).
- All `docs/paper/*` (draft.md / main.tex / review-N.md / changelog.md / rebuttal.md).
- `docs/references.bib`.
- All agent → agent / agent → Codex / agent → Gemini delegation prompts and responses.
- All logs under `.claude/logs/`.
- `.codex/AGENTS.md`, `.gemini/GEMINI.md`.
- Keyword lists in `routing-keywords.json` (the literature being searched is largely English).
- Commit messages and PR descriptions.
- Agent scratch / chain-of-thought notes.

## Boundary cases

- **Hook code with user-facing strings.** Python source is English; only the literal user-facing string is Japanese. Example: `print("⚠️ 引用が見つかりません: " + claim_text)` — variable names and surrounding code stay English.
- **User free-text input.** When the user types a research theme or RQ in Japanese, store it verbatim in `CLAUDE.md` Zone B. Agents translate to English when they materialize content under `docs/research/`.
- **When unsure, choose English.** Keep the rule simple.

## Why this split

- Specialist agents are addressed by Codex / Gemini, which prefer English.
- Logs are searched by other agents; consistency matters.
- The paper is the artifact; it is in English (paper output language is configurable in Zone B but defaults to English).
- The user reads chat replies in their native language for speed.
