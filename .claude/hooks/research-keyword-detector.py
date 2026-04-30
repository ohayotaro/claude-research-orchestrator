#!/usr/bin/env python3
"""UserPromptSubmit hook: detect prompts that should clearly use Gemini or Codex
and surface a stronger hint than the generic agent-router.

Also warns when the suggested CLI is unavailable per .claude/logs/setup-status.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GEMINI_PATTERNS = [
    r"\bpaper(s)?\b",
    r"\bPDF\b",
    r"\bfigure(s)?\b",
    r"\bimage(s)?\b",
    r"\bchart(s)?\b",
    r"\bvideo(s)?\b",
    r"\baudio\b",
    r"\bscreenshot(s)?\b",
    r"先行研究",
    r"論文",
    r"図表?",
]

CODEX_PATTERNS = [
    r"\bproof\b",
    r"\breview\b",
    r"\bcritique\b",
    r"\bstatistic(s|al)?\b",
    r"\blogic(al)?\b",
    r"\bdebug(ging)?\b",
    r"\bstacktrace\b",
    r"\bexception\b",
    r"レビュー",
    r"論理",
    r"統計",
    r"デバッグ",
]


def cli_status() -> dict[str, bool]:
    p = Path(".claude/logs/setup-status.json")
    if not p.exists():
        return {"codex_available": True, "gemini_available": True}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return {
            "codex_available": bool(d.get("codex_available", True)),
            "gemini_available": bool(d.get("gemini_available", True)),
        }
    except json.JSONDecodeError:
        return {"codex_available": True, "gemini_available": True}


def matches(prompt: str, patterns: list[str]) -> list[str]:
    lowered = prompt.lower()
    hit: list[str] = []
    for pat in patterns:
        m = re.search(pat, lowered, re.IGNORECASE)
        if m:
            hit.append(m.group(0))
    return hit


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    prompt = payload.get("prompt", "")
    if not prompt.strip():
        return 0

    status = cli_status()
    gemini_hits = matches(prompt, GEMINI_PATTERNS)
    codex_hits = matches(prompt, CODEX_PATTERNS)

    msgs: list[str] = []
    if gemini_hits:
        if status["gemini_available"]:
            msgs.append(
                "[hint] Gemini への delegation を推奨します"
                f"（検出: {', '.join(set(gemini_hits[:3]))}）。"
            )
        else:
            msgs.append(
                "[hint] Gemini が必要と思われますが"
                f"（検出: {', '.join(set(gemini_hits[:3]))}）、"
                "gemini CLI が見つかりません。Claude WebFetch にフォールバックします。"
            )
    if codex_hits:
        if status["codex_available"]:
            msgs.append(
                "[hint] Codex への delegation を推奨します"
                f"（検出: {', '.join(set(codex_hits[:3]))}）。"
            )
        else:
            msgs.append(
                "[hint] Codex が必要と思われますが"
                f"（検出: {', '.join(set(codex_hits[:3]))}）、"
                "codex CLI が見つかりません。Claude subagent にフォールバックします。"
            )

    if msgs:
        print("\n".join(msgs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
