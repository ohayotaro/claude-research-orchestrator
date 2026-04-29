# Claude Research Orchestrator

研究分野を問わず使える、Claude Code を司令塔とした **multi-agent research orchestrator** テンプレートです。

A field-agnostic research orchestrator template. Claude Code (Opus) coordinates a small team of specialized agents and external CLI partners (Codex, Gemini) across the full research lifecycle:

> **literature review → gap identification → hypothesis generation → experiment design → script-based verification → results analysis → discussion → paper writing → peer review → revision**

## Philosophy

- **Orchestrator delegates only — it does not implement.** The main Claude session preserves context and routes work to specialists.
- **Right tool for right task.**
  - **Claude Opus** — orchestration, hypothesis generation, large-context analysis & discussion
  - **Claude Sonnet** — light implementation, edits, formatting
  - **Codex CLI** — logical verification, statistical rigor, strict review, debugging
  - **Gemini CLI** — web research, paper PDFs, figures, multimodal exploration
- **Field-agnostic.** `/init-research` collects domain, theme, research question, and writes them into Zone B of `CLAUDE.md`. The same template works for physics, biology, social science, CS, etc.
- **English everywhere except the user-facing dialogue.** See `.claude/rules/language.md`.

## Quick start

```bash
# 1. Clone or copy this repo into your research project directory
# 2. Install dependencies
bash scripts/setup.sh
# 3. Open in Claude Code
claude
# 4. Inside Claude, initialize the research project
/init-research
```

`/init-research` will ask you (in Japanese) about the research domain, theme, RQ, paper output language, paper format (Markdown+BibTeX or LaTeX), and writes those into `CLAUDE.md` Zone B and `pyproject.toml`.

## Skills (the research pipeline)

Run them in order, or jump in at any phase:

| Skill | Purpose |
|---|---|
| `/init-research` | Initialize a new research project (writes Zone B, scaffolds `docs/`, `src/`, `data/`) |
| `/literature-review` | Gemini-driven prior-art survey → `docs/research/lit-review.md` + `references.bib` |
| `/identify-gaps` | Extract research gaps from the review |
| `/generate-hypothesis` | Generate solution candidates, critiqued by Codex |
| `/design-experiment` | Design experiment, choose statistics, sample size |
| `/run-experiment` | Implement and run Python scripts under `uv` with full reproducibility metadata |
| `/analyze-results` | Statistical tests, effect sizes, CIs, figures |
| `/discuss-results` | Implications, limitations, future work |
| `/write-paper` | Assemble IMRaD draft (Markdown or LaTeX, per Zone B) |
| `/peer-review` | Codex-driven strict review |
| `/revise` | Apply review comments, log changelog |
| `/checkpoint` | Persist current phase / next action into Zone C |

## Specialized agents

10 agents under `.claude/agents/`. See `.claude/rules/agent-routing.md` for the routing matrix.

## Requirements

- Claude Code (Opus 4.x)
- [`uv`](https://github.com/astral-sh/uv) for Python environment
- [Codex CLI](https://github.com/openai/codex) (recommended)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (recommended)

`setup.sh` detects what's available and falls back to Claude subagents when external CLIs are missing.

## Layout

```
.claude/        Orchestration layer (agents / skills / hooks / rules / configs)
.codex/         Codex CLI contract
.gemini/        Gemini CLI contract
docs/           Research notes (English) and paper drafts
src/            Experiment & analysis code (Python)
data/           raw / processed / results — raw and processed are gitignored
notebooks/      Optional Jupyter notebooks
tests/          pytest tests for src/
scripts/        setup.sh, update.sh
CLAUDE.md       3-zone config (immutable rules / project / session)
```

## Credits

Built on patterns from:
- [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) — agent harness pattern
- [`DeL-TaiseiOzaki/claude-code-orchestra`](https://github.com/DeL-TaiseiOzaki/claude-code-orchestra) — Codex / Gemini delegation contract
- [`ohayotaro/claude-orchestrator`](https://github.com/ohayotaro/claude-orchestrator) — domain-specialized 3-zone template
