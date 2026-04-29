#!/usr/bin/env python3
"""PostToolUse hook on Bash. When a `python` / `pytest` / `uv run` command exits
non-zero with a recognizable Python traceback, suggest delegating to
codex-debugger.

We do not auto-launch the agent — only nudge. Auto-launch would surprise users
during routine debugging.
"""

from __future__ import annotations

import json
import re
import sys

PY_TB = re.compile(r"Traceback \(most recent call last\):", re.MULTILINE)
RUNNER_RE = re.compile(r"\b(uv\s+run\s+python|python3?|pytest)\b")


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    inp = payload.get("tool_input", {})
    cmd = inp.get("command", "")
    response = payload.get("tool_response", {})
    stderr = response.get("stderr", "") or ""
    stdout = response.get("stdout", "") or ""
    exit_code = response.get("exit_code")

    if exit_code in (0, None):
        return 0
    if not RUNNER_RE.search(cmd):
        return 0

    combined = stderr + "\n" + stdout
    if not PY_TB.search(combined):
        return 0

    last_lines = "\n".join(combined.strip().splitlines()[-6:])
    print(
        "🩺 Python 実行が失敗しました。`codex-debugger` に root-cause 解析を依頼することを推奨。\n"
        f"末尾抜粋:\n{last_lines}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
