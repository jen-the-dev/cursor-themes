#!/usr/bin/env bash
# install.sh � install cursor-themes as a local Cursor extension
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PUBLISHER="jen-the-dev"
NAME="cursor-themes"
VERSION="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("package.json").read_text())["version"])
PY
)"
EXT_ID="${PUBLISHER}.${NAME}-${VERSION}"
CURSOR_EXT_DIR="${CURSOR_EXTENSIONS_DIR:-$HOME/.cursor/extensions}"
TARGET="${CURSOR_EXT_DIR}/${EXT_ID}"

log() { printf '%s\n' "$*"; }
err() { printf 'ERROR: %s\n' "$*" >&2; }

usage() {
  cat <<EOF
Usage: $(basename "$0") [--copy] [--dry-run] [--uninstall]

Installs this repo as an unpacked Cursor/VS Code theme extension.

Options:
  --copy        Copy instead of symlink (default: symlink)
  --dry-run     Show actions without changing anything
  --uninstall   Remove installed extension directory/symlink
EOF
}

MODE="symlink"
DRY_RUN=false
UNINSTALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown option: $1"; usage; exit 1 ;;
  esac
done

cd "$REPO_DIR"

if [[ ! -f package.json ]]; then
  err "package.json not found. Run: python3 scripts/zed_to_cursor.py"
  exit 1
fi

run() {
  if $DRY_RUN; then
    log "[dry-run] $*"
  else
    eval "$@"
  fi
}

if $UNINSTALL; then
  if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    run "rm -rf '$TARGET'"
    log "Removed $TARGET"
  else
    log "Nothing to uninstall at $TARGET"
  fi
  exit 0
fi

mkdir -p "$CURSOR_EXT_DIR"

if [[ -e "$TARGET" && ! -L "$TARGET" && "$MODE" == "symlink" ]]; then
  err "$TARGET exists and is not a symlink. Use --copy or --uninstall first."
  exit 1
fi

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  run "rm -rf '$TARGET'"
fi

if [[ "$MODE" == "symlink" ]]; then
  run "ln -s '$REPO_DIR' '$TARGET'"
else
  run "mkdir -p '$TARGET'"
  run "rsync -a --delete --exclude '.git' '$REPO_DIR/' '$TARGET/'"
fi

log "Installed to $TARGET"
log "Reload Cursor, then press Cmd+K Cmd+T to pick a theme."
log "Categories appear as: Cyberpunk - ... and Mtg - ..."
