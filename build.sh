#!/usr/bin/env bash
# build.sh � regenerate Cursor themes from Zed sources and optionally package a VSIX
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

python3 scripts/zed_to_cursor.py

if command -v vsce >/dev/null 2>&1; then
  vsce package --out dist/
  echo "VSIX written to dist/"
else
  echo "Install @vscode/vsce to package: npm install -g @vscode/vsce"
fi
