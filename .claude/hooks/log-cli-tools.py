#!/usr/bin/env python3
"""PreToolUse + PostToolUse hook on Bash that captures every `codex` and
`gemini` invocation into .claude/logs/cli/<ISO>-<tool>-<short>.md.

Both pre and post phases append to the same file, identified via a shared
session_id stored in the tool_input.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CLI_RE = re.compile(r"^\s*(codex|gemini)\b")
LOG_DIR = Path(".claude/logs/cli")


def slug(s: str, n: int = 24) -> str:
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^A-Za-z0-9._-]", "", s)
    return s[:n] or "x"


def call_id(cmd: str) -> str:
    return hashlib.sha1(cmd.encode()).hexdigest()[:8]


def log_path(tool: str, cmd: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    short = slug(cmd[:60])
    cid = call_id(cmd)
    return LOG_DIR / f"{ts}-{tool}-{short}-{cid}.md"


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    phase = payload.get("hook_event_name", "")
    inp = payload.get("tool_input", {})
    cmd = inp.get("command", "") or ""
    m = CLI_RE.match(cmd)
    if not m:
        return 0
    tool = m.group(1)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    p = log_path(tool, cmd)

    if phase == "PreToolUse":
        ts = datetime.now(timezone.utc).isoformat()
        p.write_text(
            f"# {tool} call\n"
            f"_started: {ts}_\n\n"
            f"## Command\n```\n{cmd}\n```\n\n"
            f"## Stdout\n_pending_\n\n"
            f"## Stderr\n_pending_\n",
            encoding="utf-8",
        )
        return 0

    if phase == "PostToolUse":
        # Find the matching pre-log by call_id suffix.
        cid = call_id(cmd)
        candidates = sorted(LOG_DIR.glob(f"*-{tool}-*-{cid}.md"))
        if not candidates:
            # Pre log was not captured (e.g. hooks misconfigured); create now.
            p2 = log_path(tool, cmd)
        else:
            p2 = candidates[-1]
        response = payload.get("tool_response", {})
        stdout = response.get("stdout", "") or ""
        stderr = response.get("stderr", "") or ""
        ec = response.get("exit_code")
        ts = datetime.now(timezone.utc).isoformat()
        try:
            existing = p2.read_text(encoding="utf-8")
        except FileNotFoundError:
            existing = ""
        finished_block = (
            f"\n_finished: {ts} (exit={ec})_\n\n"
            f"## Stdout\n```\n{stdout}\n```\n\n"
            f"## Stderr\n```\n{stderr}\n```\n"
        )
        # Replace the "_pending_" placeholders if present, else append.
        if "_pending_" in existing:
            existing = existing.replace("## Stdout\n_pending_\n\n## Stderr\n_pending_\n", "")
            existing = existing.rstrip() + finished_block
        else:
            existing = existing.rstrip() + finished_block
        p2.write_text(existing, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
