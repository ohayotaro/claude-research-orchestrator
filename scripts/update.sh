#!/usr/bin/env bash
# Update the orchestrator template layer (.claude/, .codex/, .gemini/) while preserving
# Zone B of CLAUDE.md (the user's project configuration).
#
# Usage: bash scripts/update.sh [--source <path>]
# If --source is omitted, the script assumes you have already pulled fresh template files
# into a sibling directory and points to it interactively.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

bold() { printf "\033[1m%s\033[0m\n" "$*"; }
warn() { printf "\033[33m[warn]\033[0m %s\n" "$*"; }
ok()   { printf "\033[32m[ok]\033[0m %s\n" "$*"; }
err()  { printf "\033[31m[err]\033[0m %s\n" "$*" >&2; }

SOURCE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --source) SOURCE="$2"; shift 2 ;;
        *) err "unknown arg: $1"; exit 2 ;;
    esac
done

if [[ -z "$SOURCE" ]]; then
    err "Pass --source <path-to-fresh-template-checkout>"
    exit 2
fi
if [[ ! -d "$SOURCE/.claude" ]]; then
    err "$SOURCE does not look like a claude-research-orchestrator checkout (no .claude/)."
    exit 2
fi

BACKUP_DIR=".claude/logs/update-backup-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

# --- Extract Zone B from current CLAUDE.md ---------------------------
bold "Backing up Zone B (project config)"
python3 - "$BACKUP_DIR" <<'PY'
import re, sys, pathlib
backup = pathlib.Path(sys.argv[1])
src = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
m = re.search(r"<!-- ZONE_B_BEGIN -->(.*?)<!-- ZONE_B_END -->", src, re.DOTALL)
if not m:
    raise SystemExit("ZONE_B markers not found in current CLAUDE.md")
(backup / "ZONE_B.md").write_text(m.group(1), encoding="utf-8")
PY
ok "Saved Zone B to $BACKUP_DIR/ZONE_B.md"

# --- Overlay template ------------------------------------------------
bold "Overlaying template from $SOURCE"
for d in .claude .codex .gemini scripts; do
    if [[ -d "$SOURCE/$d" ]]; then
        cp -R "$BACKUP_DIR/" "$BACKUP_DIR/" 2>/dev/null || true   # noop touch
        rsync -a --delete "$SOURCE/$d/" "./$d/"
        ok "synced $d/"
    fi
done
cp "$SOURCE/CLAUDE.md" CLAUDE.md
ok "replaced CLAUDE.md (Zone B will be restored)"

# --- Restore Zone B --------------------------------------------------
bold "Restoring Zone B"
python3 - "$BACKUP_DIR" <<'PY'
import re, sys, pathlib
backup = pathlib.Path(sys.argv[1])
zb = (backup / "ZONE_B.md").read_text(encoding="utf-8")
src = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
new = re.sub(
    r"(<!-- ZONE_B_BEGIN -->).*?(<!-- ZONE_B_END -->)",
    lambda m: m.group(1) + zb + m.group(2),
    src, count=1, flags=re.DOTALL,
)
pathlib.Path("CLAUDE.md").write_text(new, encoding="utf-8")
PY
ok "Zone B restored from backup"

echo
ok "Update complete. Backup at $BACKUP_DIR"
