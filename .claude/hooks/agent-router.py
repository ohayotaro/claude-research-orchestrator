#!/usr/bin/env python3
"""UserPromptSubmit hook: suggest a specialized agent based on prompt keywords.

Reads .claude/routing-keywords.json and prints a short user-facing hint when
the user's prompt looks like it should be delegated.

Strict on language: comments and code are English; the user-facing string is
Japanese (project policy in .claude/rules/language.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_routing_table() -> dict[str, list[str]]:
    p = Path(".claude/routing-keywords.json")
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def find_matches(prompt: str, table: dict[str, list[str]]) -> list[tuple[str, str]]:
    lowered = prompt.lower()
    hits: list[tuple[str, str]] = []
    for agent, keywords in table.items():
        for kw in keywords:
            if kw.lower() in lowered:
                hits.append((agent, kw))
                break
    return hits


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    prompt = payload.get("prompt", "")
    if not prompt.strip():
        return 0

    table = load_routing_table()
    if not table:
        return 0

    hits = find_matches(prompt, table)
    if not hits:
        return 0

    # User-facing hint (Japanese).
    lines = ["💡 推奨エージェント:"]
    for agent, kw in hits[:3]:
        lines.append(f"  - {agent}（キーワード: {kw}）")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
