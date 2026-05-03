# Agent routing

The orchestrator is Claude Opus. It does **not** implement; it integrates results from specialists. This file is the canonical routing matrix.

## Specialists

| Agent | Backed by | Best at |
|---|---|---|
| `literature-reviewer` | Opus + Gemini CLI | Survey, citation graph, BibTeX entry generation |
| `gemini-explore` | Gemini CLI | Multimodal: PDFs, figures, videos, web pages |
| `hypothesis-generator` | Opus (+ Codex critique) | Diverging from gaps to candidate hypotheses; framing contributions |
| `methodology-designer` | Opus (+ Codex check) | Experiment design, statistical test choice, sample size |
| `experiment-runner` | Sonnet | Writing Python, running under `uv`, capturing reproducibility metadata |
| `data-analyst` | Opus | Statistical analysis, effect sizes, CIs, plotting |
| `discussant` | Opus | Implications, limitations, future work |
| `paper-writer` | Opus | IMRaD assembly, voice consistency, narrative |
| `peer-reviewer` | Codex | Strict logical / statistical / citation review (paper draft level) |
| `script-reviewer` | Codex | Strict pre-run review of experiment / analysis scripts (statistics, leakage, reproducibility, numerical edge cases, test coverage) |
| `codex-debugger` | Codex | Root-cause analysis of script failures |

## Routing triggers

The `agent-router` hook (`.claude/hooks/agent-router.py`) reads `.claude/routing-keywords.json` and suggests agents based on user prompts.

| Trigger | Suggested agent |
|---|---|
| "find papers", "prior work", "literature", "survey", "PDF" | `literature-reviewer` (delegates to Gemini) |
| "figure", "image", "chart", "screenshot", "video", "audio" | `gemini-explore` |
| "hypothesis", "idea", "what if", "novel approach", "gap" | `hypothesis-generator` |
| "experiment design", "sample size", "power", "statistical test" | `methodology-designer` |
| "implement", "script", "run", "code this up", "execute" | `experiment-runner` |
| "analyze", "statistics", "p-value", "effect size", "plot" | `data-analyst` |
| "limitations", "implications", "future work", "discuss" | `discussant` |
| "paper", "draft", "introduction", "abstract", "IMRaD" | `paper-writer` |
| "review this draft", "critique", "find flaws", "rebut" | `peer-reviewer` (delegates to Codex) |
| "review my script", "code review", "leakage", "before running" | `script-reviewer` (delegates to Codex) |
| "error", "exception", "stacktrace", "doesn't work", "debug" | `codex-debugger` |

## When to NOT delegate

The orchestrator handles these directly:
- Short clarifying Q&A with the user.
- Choosing between two paths the user has presented.
- Reading Zone B / Zone C of `CLAUDE.md`.
- Routing decisions (which agent next).
- Anything under ~10 lines of output that doesn't require deep context.

## Parallelism

- `literature-reviewer` and `hypothesis-generator` can run in parallel during early-stage exploration: one surveys while the other brainstorms.
- `data-analyst` and `paper-writer` can run in parallel once analysis is locked: writer drafts methods/intro while analyst handles results.
- `peer-reviewer` is always serial (it reads a finished draft).

## Fallbacks

If `codex` or `gemini` CLIs are unavailable (see `.claude/logs/setup-status.json`), the affected agents fall back to running in-process via Claude. The hook `research-keyword-detector.py` checks this and warns the user.
