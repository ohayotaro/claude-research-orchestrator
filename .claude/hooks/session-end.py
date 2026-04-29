#!/usr/bin/env python3
"""SessionEnd hook. Append a one-line session summary to .claude/logs/sessions.log.

Does NOT modify Zone C — that is /checkpoint's job, run intentionally by the
orchestrator. We only persist a lightweight breadcrumb here so a human can
audit when each session ended.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    reason = payload.get("reason", "unknown")
    ts = datetime.now(timezone.utc).isoformat()
    log = Path(".claude/logs/sessions.log")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{ts} session_end reason={reason}\n")

    if reason == "logout":
        print(
            "📒 セッションを終えます。永続化が必要なら次回開始前に `/checkpoint` を実行してください。"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
