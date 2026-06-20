# Cursor Themes

Cyberpunk and Magic: The Gathering theme collections for **Cursor**, converted from [Zed](https://zed.dev) theme JSON.

## Categories

| Category | Themes | Zed source |
|----------|--------|------------|
| **cyberpunk** | 30 movie-inspired dark/light themes | [cyberpunk-zed-themes](https://github.com/jen-the-dev/cyberpunk-zed-themes) |
| **mtg** | 25 Magic color identity, guild, and shard themes | [zed-mtg-themes](https://github.com/jen-the-dev/zed-mtg-themes) |

Theme names in Cursor appear as `Cyberpunk - Blade Runner`, `Mtg - ...`, etc.

## Quick install

```bash
git clone https://github.com/jen-the-dev/cursor-themes.git
cd cursor-themes
./install.sh
```

Reload Cursor, then **Cmd+K Cmd+T** (or **Preferences: Color Theme**) and pick a theme.

## Rebuild from Zed sources

Cyberpunk Zed themes are symlinked from `../zed-themes/cyberpunk-zed-themes/themes/`.

```bash
python3 scripts/zed_to_cursor.py   # regenerate themes/ + package.json
./install.sh                         # reinstall extension symlink
```

To add MTG themes, drop JSON files into `sources/zed/mtg/` and rerun the converter.

## VSIX package (optional)

```bash
npm install -g @vscode/vsce
./build.sh
```

Install the generated `.vsix` via **Extensions ? Install from VSIXù**

## Uninstall

```bash
./install.sh --uninstall
```

## Layout

```
cursor-themes/
??? sources/zed/
?   ??? cyberpunk/     # symlinks to Zed source JSON
?   ??? mtg/           # drop MTG Zed JSON here
??? themes/
?   ??? cyberpunk/     # converted Cursor themes
?   ??? mtg/
?   ??? manifest.json
??? scripts/zed_to_cursor.py
??? install.sh
??? package.json
```

## License

MIT ù see [LICENSE](LICENSE).
