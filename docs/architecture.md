# Architecture

How halloween-openSUSE turns art masters into installable themes.

```
art/palette.toml ─┐
art/source/ (LFS) ─┼─▶ tools/build.py ─▶ tools/targets/*.py ─▶ build/ ─▶ install/*.sh
shared/, plasma/ ──┘                                             │
                                                    tools/check.py validates it
```

## Sources

- **`art/palette.toml`** defines every colour once, by name, and maps roles
  (such as `progress_fill`) to them. The colour scheme, Plasma style, splash,
  login screen, boot splash and Firefox theme are all generated from it.
- **`art/source/`** holds the art masters in Git LFS: the 4K wallpapers, the
  chameleon and lantern cut-outs, and in `vectors/` the SVG masters for icons
  and Plasma style ornaments. If a master is missing, the build draws a
  placeholder instead and lists it in `build/placeholders.txt`; `make
  release-check` fails while any placeholder is in use.
- **`art/crops.toml`** gives the focus points used when a wallpaper is cropped
  to another aspect ratio, and the parts of the night wallpaper used for the
  splash backdrop and the Firefox header.
- **`art/prompts/`** records how each master was made.
- **`shared/` and `plasma/`** hold the hand-written parts: metadata, templates
  with `@palette_name@` tokens, QML, `index.theme`, and the Firefox manifest
  template.

## Build

`tools/build.py` creates a `Context` (`tools/context.py`: the palette, the
masters, the placeholder list) and runs every target in
`tools/targets/__init__.py`. Each target module has:

- `DESKTOP`: `"shared"` for pieces any desktop can use, or a desktop name
- `build(ctx)`: writes its files into `build/`

| Target | Desktop | Output |
|---|---|---|
| `wallpapers` | shared | `build/user/wallpapers/openSUSEhalloween/` |
| `icons` | shared | `build/user/icons/openSUSE-halloween/` (via `tools/vectors.py`) |
| `plymouth` | shared | `build/root/plymouth/openSUSE-halloween/` |
| `firefox` | shared | `build/firefox/` (unpacked theme and `.xpi`) |
| `plasma` | plasma | colour scheme, Plasma style (via `tools/plasma_style.py`), global theme |
| `sddm` | plasma | `build/root/sddm/breeze-openSUSE-halloween/` |

`build.py --desktop plasma` builds the shared targets plus Plasma's.
`build/user/` installs to `~/.local/share`, `build/root/` to `/usr/share`,
and the install scripts are copied to `build/install/`.
`build/MANIFEST.sha256` lists every installable file; the same masters always
give the same manifest.

The Plasma style is not drawn from scratch: `tools/plasma_style.py` fetches
Breeze's SVGs pinned by hash in `tools/upstream.toml` and adds the ornaments,
so it stays compatible with Plasma's element IDs (which `check.py` verifies).

## Checks

`tools/check.py` runs after every build (`make check`): metadata syntax,
leftover tokens, colour contrast, image sizes and file size limits, the
Plasma style's element IDs, icon SVG sanity, the Firefox theme, and
`reuse lint`. CI runs it on every pull request, together with ruff and
ShellCheck.

## Install

`install/install-user.sh` copies `build/user/` and applies the theme with
Plasma's own tools; `install/install-root.sh` installs the login screen and
boot splash (with `--plymouth` making the boot splash the default and
rebuilding the initrds). Both save the previous settings, which the
`uninstall-*.sh` scripts restore. `install/verify.sh` reports what is active.

## Adding a desktop

GNOME and Xfce are planned; see [gnome/](../gnome/) and [xfce/](../xfce/).
To add one:

1. Put its hand-written sources in a top-level directory named after it.
2. Add target modules in `tools/targets/` with `DESKTOP = "<desktop>"`, and
   list them in `TARGETS`. Reuse `ctx.wallpapers`, `ctx.hero`, the palette and
   the helpers in `tools/imaging.py`.
3. Write the output under `build/user/` or `build/root/` in the paths the
   desktop expects.
4. Add install and verify scripts for it in `install/`.
5. Extend `tools/check.py` with checks for the new files.
6. Document it in the README's "What's included" table.

## Adding icons

Folder icons are the master folder (`art/source/vectors/folder.svg`) with an
emblem glyph in place of its leaf; other icons are cleaned-up masters. Add the
SVG master to `art/source/vectors/` and map it to icon names in
`tools/vectors.py` (`FOLDER_EMBLEMS`, `APPS`, `SYMBOLIC`, `ALIASES`). Symbolic
icons are written in KDE's format so they follow the colour scheme. Check the
result with `make icon-preview`.

## Changing colours

Edit `art/palette.toml` and run `make check`: every generated file picks up
the change, and the contrast checks tell you if a pair of colours became too
close.
