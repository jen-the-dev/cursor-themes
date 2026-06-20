#!/usr/bin/env python3
"""Validate package.json and converted theme JSON files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    package = json.loads((ROOT / "package.json").read_text())
    themes = package.get("contributes", {}).get("themes", [])
    if not themes:
        print("ERROR: no themes registered in package.json")
        return 1

    errors = 0
    for entry in themes:
        path = ROOT / entry["path"].removeprefix("./")
        if not path.exists():
            print(f"ERROR: missing theme file: {path}")
            errors += 1
            continue
        data = json.loads(path.read_text())
        for key in ("name", "type", "colors", "tokenColors"):
            if key not in data:
                print(f"ERROR: {path} missing key: {key}")
                errors += 1

    manifest = ROOT / "themes" / "manifest.json"
    if manifest.exists():
        manifest_data = json.loads(manifest.read_text())
        if len(manifest_data.get("themes", [])) != len(themes):
            print("ERROR: manifest theme count does not match package.json")
            errors += 1

    if errors:
        print(f"Validation failed with {errors} error(s)")
        return 1

    print(f"Validated {len(themes)} themes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
