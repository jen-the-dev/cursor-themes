#!/usr/bin/env python3
"""Convert Zed theme JSON files to VS Code / Cursor color themes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources" / "zed"
THEMES_OUT = ROOT / "themes"

VENDOR_SOURCE_DIRS: dict[str, list[Path]] = {
    "cyberpunk": [
        ROOT / "sources" / "vendor" / "cyberpunk-zed-themes" / "themes",
        ROOT.parent / "zed-themes" / "cyberpunk-zed-themes" / "themes",
    ],
    "mtg": [
        ROOT / "sources" / "vendor" / "zed-mtg-themes" / "themes",
        ROOT.parent / "zed-themes" / "zed-mtg-themes" / "themes",
    ],
}

UI_MAP: dict[str, str] = {
    "editor.background": "editor.background",
    "editor.foreground": "editor.foreground",
    "editor.active_line.background": "editor.lineHighlightBackground",
    "editor.line_number": "editorLineNumber.foreground",
    "editor.active_line_number": "editorLineNumber.activeForeground",
    "editor.gutter.background": "editorGutter.background",
    "background": "sideBar.background",
    "foreground": "foreground",
    "text": "foreground",
    "text.muted": "descriptionForeground",
    "text.accent": "list.highlightForeground",
    "surface.background": "sideBar.background",
    "element.background": "dropdown.background",
    "element.hover": "list.hoverBackground",
    "border": "panel.border",
    "border.focused": "focusBorder",
    "tab_bar.background": "editorGroupHeader.tabsBackground",
    "tab.active_background": "tab.activeBackground",
    "tab.inactive_background": "tab.inactiveBackground",
    "panel.background": "panel.background",
    "title_bar.background": "titleBar.activeBackground",
    "status_bar.background": "statusBar.background",
    "terminal.background": "terminal.background",
    "terminal.foreground": "terminal.foreground",
}

ANSI_MAP = {
    "terminal.ansi.black": "terminal.ansiBlack",
    "terminal.ansi.red": "terminal.ansiRed",
    "terminal.ansi.green": "terminal.ansiGreen",
    "terminal.ansi.yellow": "terminal.ansiYellow",
    "terminal.ansi.blue": "terminal.ansiBlue",
    "terminal.ansi.magenta": "terminal.ansiMagenta",
    "terminal.ansi.cyan": "terminal.ansiCyan",
    "terminal.ansi.white": "terminal.ansiWhite",
    "terminal.ansi.bright_black": "terminal.ansiBrightBlack",
    "terminal.ansi.bright_red": "terminal.ansiBrightRed",
    "terminal.ansi.bright_green": "terminal.ansiBrightGreen",
    "terminal.ansi.bright_yellow": "terminal.ansiBrightYellow",
    "terminal.ansi.bright_blue": "terminal.ansiBrightBlue",
    "terminal.ansi.bright_magenta": "terminal.ansiBrightMagenta",
    "terminal.ansi.bright_cyan": "terminal.ansiBrightCyan",
    "terminal.ansi.bright_white": "terminal.ansiBrightWhite",
}

SYNTAX_SCOPES: dict[str, list[str]] = {
    "keyword": ["keyword", "storage.type", "storage.modifier"],
    "string": ["string", "string.quoted", "string.template"],
    "comment": ["comment", "punctuation.definition.comment"],
    "function": ["entity.name.function", "support.function", "meta.function-call"],
    "type": ["entity.name.type", "support.type", "entity.other.inherited-class"],
    "number": ["constant.numeric"],
    "boolean": ["constant.language.boolean"],
    "operator": ["keyword.operator"],
    "variable": ["variable", "variable.other.readwrite"],
    "property": ["variable.other.property", "support.variable.property"],
    "constant": ["constant", "constant.language"],
    "punctuation": ["punctuation"],
    "tag": ["entity.name.tag"],
    "attribute": ["entity.other.attribute-name"],
    "constructor": ["entity.name.function", "support.class"],
    "embedded": ["string.other.embedded", "meta.embedded"],
    "link": ["markup.underline.link", "string.other.link"],
    "emphasis": ["markup.italic", "emphasis"],
    "strong": ["markup.bold", "strong"],
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "theme"


def font_style(style: dict) -> str | None:
    parts: list[str] = []
    if style.get("font_style") == "italic":
        parts.append("italic")
    weight = style.get("font_weight")
    if weight and int(weight) >= 600:
        parts.append("bold")
    if style.get("underline"):
        parts.append("underline")
    return " ".join(parts) if parts else None


def convert_ui(style: dict) -> dict[str, str]:
    colors: dict[str, str] = {}
    for zed_key, vscode_key in UI_MAP.items():
        value = style.get(zed_key)
        if isinstance(value, str) and value:
            colors[vscode_key] = value
    for zed_key, vscode_key in ANSI_MAP.items():
        value = style.get(zed_key)
        if isinstance(value, str) and value:
            colors[vscode_key] = value

    if "editor.background" not in colors and style.get("background"):
        colors["editor.background"] = style["background"]
    if "editor.foreground" not in colors and style.get("foreground"):
        colors["editor.foreground"] = style["foreground"]

    colors.setdefault("activityBar.background", colors.get("sideBar.background", colors.get("editor.background", "#1e1e1e")))
    colors.setdefault("sideBarTitle.foreground", colors.get("foreground", colors.get("editor.foreground", "#cccccc")))
    colors.setdefault("editorCursor.foreground", colors.get("editor.foreground", colors.get("foreground", "#ffffff")))
    colors.setdefault("selection.background", colors.get("text.accent", "#264f78"))
    return colors


def convert_syntax(style: dict) -> list[dict]:
    syntax = style.get("syntax")
    if not isinstance(syntax, dict):
        return []

    token_colors: list[dict] = []
    for key, scopes in SYNTAX_SCOPES.items():
        entry = syntax.get(key)
        if not isinstance(entry, dict):
            continue
        settings: dict[str, str] = {}
        if entry.get("color"):
            settings["foreground"] = entry["color"]
        style_value = font_style(entry)
        if style_value:
            settings["fontStyle"] = style_value
        if settings:
            token_colors.append({"scope": scopes, "settings": settings})
    return token_colors


def convert_zed_file(path: Path, category: str) -> dict | None:
    payload = json.loads(path.read_text())
    variants = payload.get("themes")
    if not isinstance(variants, list) or not variants:
        return None

    variant = variants[0]
    style = variant.get("style")
    if not isinstance(style, dict):
        return None

    raw_name = variant.get("name") or payload.get("name") or path.stem
    display_name = raw_name
    category_prefix = category.replace("-", " ")
    for prefix in (category_prefix, category.replace("-", " ").title(), category.title()):
        if display_name.lower().startswith(f"{prefix.lower()} "):
            display_name = display_name[len(prefix) + 1 :]
            break
        if display_name.lower().startswith(f"{prefix.lower()}-"):
            display_name = display_name[len(prefix) + 1 :]
            break
    if display_name == path.stem:
        stem = path.stem
        if stem.startswith(f"{category}-"):
            stem = stem[len(category) + 1 :]
        display_name = " ".join(part.capitalize() for part in stem.split("-"))
    appearance = variant.get("appearance", "dark")
    theme_type = "light" if appearance == "light" else "dark"
    ui_theme = "vs" if theme_type == "light" else "vs-dark"
    category_label = category.replace("-", " ").title()
    label = f"{category_label} - {display_name}"

    slug = slugify(path.stem)
    out_dir = THEMES_OUT / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"{slug}-color-theme.json"
    out_path = out_dir / out_name

    theme_json = {
        "name": label,
        "type": theme_type,
        "colors": convert_ui(style),
        "tokenColors": convert_syntax(style),
    }
    out_path.write_text(json.dumps(theme_json, indent=2) + "\n")

    return {
        "label": label,
        "uiTheme": ui_theme,
        "path": f"./themes/{category}/{out_name}",
        "category": category,
        "source": str(path),
    }


def discover_sources() -> list[tuple[str, Path]]:
    pairs: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def add(category: str, path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        pairs.append((category, path))

    if SOURCES.exists():
        for category_dir in sorted(SOURCES.iterdir()):
            if not category_dir.is_dir():
                continue
            for path in sorted(category_dir.glob("*.json")):
                add(category_dir.name, path)

    for category, directories in VENDOR_SOURCE_DIRS.items():
        for directory in directories:
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("*.json")):
                add(category, path)

    return pairs


def generate_package(entries: list[dict]) -> None:
    package = {
        "name": "cursor-themes",
        "displayName": "Jen the Dev Cursor Themes",
        "description": "Cyberpunk and MTG theme collections for Cursor, converted from Zed themes.",
        "version": "1.0.0",
        "publisher": "jen-the-dev",
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/jen-the-dev/cursor-themes",
        },
        "engines": {"vscode": "^1.80.0"},
        "categories": ["Themes"],
        "contributes": {
            "themes": [
                {"label": entry["label"], "uiTheme": entry["uiTheme"], "path": entry["path"]}
                for entry in entries
            ]
        },
    }
    (ROOT / "package.json").write_text(json.dumps(package, indent=2) + "\n")


def write_manifest(entries: list[dict]) -> None:
    manifest = {
        "categories": {},
        "themes": entries,
    }
    for entry in entries:
        manifest["categories"].setdefault(entry["category"], []).append(entry["label"])
    (ROOT / "themes" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> int:
    entries: list[dict] = []
    for category, path in discover_sources():
        converted = convert_zed_file(path, category)
        if converted:
            entries.append(converted)
            print(f"converted {category}/{path.name} -> {converted['path']}")

    generate_package(entries)
    write_manifest(entries)
    print(f"generated package.json with {len(entries)} themes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
