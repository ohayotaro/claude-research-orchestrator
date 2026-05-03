#!/usr/bin/env bash
# Update the orchestrator template layer (.claude/, .codex/, .gemini/, scripts/)
# while preserving:
#   - Zone B of CLAUDE.md  (the user's project configuration)
#   - .claude/logs/        (runtime logs from prior sessions)
#
# Usage: bash scripts/update.sh --source <path-to-fresh-template-checkout>

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
if [[ ! -f "$SOURCE/CLAUDE.md" ]]; then
    err "$SOURCE has no CLAUDE.md."
    exit 2
fi

# Backup directory MUST live outside any rsync target. We use the repo root
# with a clearly-named timestamped directory; .gitignore excludes it.
BACKUP_DIR=".update-backup-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"

# --- Extract Zone B from the current CLAUDE.md -----------------------
bold "Backing up Zone B (project config) and CLAUDE.md"
cp CLAUDE.md "$BACKUP_DIR/CLAUDE.md.before"
python3 - "$BACKUP_DIR" <<'PY'
import re, sys, pathlib
backup = pathlib.Path(sys.argv[1])
src = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
m = re.search(r"<!-- ZONE_B_BEGIN -->(.*?)<!-- ZONE_B_END -->", src, re.DOTALL)
if not m:
    raise SystemExit("ZONE_B markers not found in current CLAUDE.md")
(backup / "ZONE_B.md").write_text(m.group(1), encoding="utf-8")
PY
if [[ ! -s "$BACKUP_DIR/ZONE_B.md" ]]; then
    err "Zone B backup is empty or missing — aborting before any destructive sync."
    exit 3
fi
ok "Saved Zone B to $BACKUP_DIR/ZONE_B.md"

# --- Verify the source CLAUDE.md has the markers we will restore into
python3 - "$SOURCE" <<'PY'
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]) / "CLAUDE.md"
text = src.read_text(encoding="utf-8")
if "<!-- ZONE_B_BEGIN -->" not in text or "<!-- ZONE_B_END -->" not in text:
    raise SystemExit("template CLAUDE.md is missing ZONE_B markers; refusing to overlay")
PY

# --- Overlay template ------------------------------------------------
bold "Overlaying template from $SOURCE"
for d in .claude .codex .gemini scripts; do
    if [[ -d "$SOURCE/$d" ]]; then
        if [[ "$d" == ".claude" ]]; then
            # Preserve runtime logs that the template never ships.
            rsync -a --delete \
                --exclude='logs/' \
                --exclude='logs/**' \
                "$SOURCE/$d/" "./$d/"
        else
            rsync -a --delete "$SOURCE/$d/" "./$d/"
        fi
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
zb_path = backup / "ZONE_B.md"
if not zb_path.exists():
    raise SystemExit(f"backup file vanished: {zb_path}")
zb = zb_path.read_text(encoding="utf-8")
src = pathlib.Path("CLAUDE.md").read_text(encoding="utf-8")
if "<!-- ZONE_B_BEGIN -->" not in src or "<!-- ZONE_B_END -->" not in src:
    raise SystemExit("post-overlay CLAUDE.md is missing ZONE_B markers; refusing to write")
new = re.sub(
    r"(<!-- ZONE_B_BEGIN -->).*?(<!-- ZONE_B_END -->)",
    lambda m: m.group(1) + zb + m.group(2),
    src, count=1, flags=re.DOTALL,
)
pathlib.Path("CLAUDE.md").write_text(new, encoding="utf-8")
PY
ok "Zone B restored from backup"

echo
ok "Update complete."
echo "  Backup: $BACKUP_DIR/  (safe to delete once you have verified the update)"
echo "  Tip: diff your CLAUDE.md against $BACKUP_DIR/CLAUDE.md.before to review."
