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
| `icons` | shared | `build/user/icons/openSUSE-halloween/` (via `tools/vectors.py`) and `openSUSE-halloween-adwaita/` |
| `plymouth` | shared | `build/root/plymouth/openSUSE-halloween/` |
| `firefox` | shared | `build/firefox/` (unpacked theme and `.xpi`) |
| `plasma` | plasma | colour scheme, Plasma style (via `tools/plasma_style.py`), global theme |
| `sddm` | plasma | `build/root/sddm/breeze-openSUSE-halloween/` |
| `gtk` | gnome, xfce | `build/user/themes/openSUSE-halloween/gtk-3.0/` (adw-gtk3-dark, recoloured) |
| `gnome` | gnome | Shell stylesheet, `gnome-background-properties/`, defaults in `build/defaults/` |
| `xfce` | xfce | `build/user/themes/openSUSE-halloween{,-hdpi,-xhdpi}/xfwm4/`, notification theme |

`build.py --desktop plasma` builds the shared targets plus Plasma's. A
target's `DESKTOP` can also be a tuple, for a piece several desktops share.
`build/user/` holds what goes to `share/` (themes, icons, wallpapers),
`build/root/` the login screen and boot splash, `build/firefox/` the Firefox
theme and `build/defaults/` the optional defaults.
`build/MANIFEST.sha256` lists every installable file; the same masters always
give the same manifest.

The GTK 3 theme and the xfwm4 theme aren't drawn from scratch either:
`upstream_archive()` in `tools/common.py` fetches adw-gtk3's and xfwm4's
release archives, pinned by SHA-256 in `tools/upstream.toml`, and the targets
set their named colours from the palette.

The Plasma style is not drawn from scratch: `tools/plasma_style.py` fetches
Breeze's SVGs pinned by hash in `tools/upstream.toml` and adds the ornaments,
so it stays compatible with Plasma's element IDs (which `check.py` verifies).

## Checks

`tools/check.py` runs after every build (`make check`): metadata syntax,
leftover tokens, the Plasma `metadata.json` files against KDE's KPlugin
schema (pinned in `tools/upstream.toml`), colour contrast, image sizes and
file size limits, the Plasma style's element IDs, the icon theme's
`index.theme` and SVGs, the Firefox theme, and `reuse lint`.

`make lint` checks the sources: ruff, ShellCheck, actionlint and zizmor for
the workflows, typos, editorconfig-checker and `reuse lint`.

CI (`.github/workflows/check.yml`) runs both on every pull request, as the
Lint and Build and check jobs. A final CI job passes only when both did; it
is the one check `main`'s ruleset requires.

## Install

`tools/install.py` (`make install`) copies the build into the system paths, as
an RPM's `%install` will: its `FILES` table maps each folder in `build/` to an
install path under `PREFIX` (`/usr`), `LIBDIR` or `SYSCONFDIR`, honouring
`DESTDIR`. Every entry inside a mapped folder is ours, so `make uninstall`
removes exactly those. `--defaults` (`make install-defaults`) installs the
`DEFAULTS` table instead: declarative files, such as an SDDM `conf.d`
drop-in, that make the theme the default the way a separate defaults package
would. Nothing that is installed changes settings. `check.py` stages an
install and uninstall into a temporary folder on every check.

The SDDM theme links openSUSE's `breeze-openSUSE` QML with relative symlinks,
so updates of that package keep flowing in.

The Firefox theme goes to `LIBDIR/firefox/browser/extensions/`: openSUSE
builds Firefox with `--with-unsigned-addon-scopes=app`, so an unsigned add-on
only loads from Firefox's own folder, not from the shared
`/usr/share/mozilla/extensions/`. Its package is therefore
architecture-specific; a Mozilla-signed `.xpi` could use the shared folder.

The development helpers in `tools/dev/` do change settings: they apply the
theme to a Plasma session, save and restore the previous settings, and switch
the login screen and boot splash, for trying changes on a test machine.
`verify.sh` reports what is active.

## Adding a desktop

Plasma, GNOME and Xfce are built; [gnome/](../gnome/) and [xfce/](../xfce/)
describe the newer two. To add another:

1. Put its hand-written sources in a top-level directory named after it.
2. Add target modules in `tools/targets/` with `DESKTOP = "<desktop>"`, and
   list them in `TARGETS`. Reuse `ctx.wallpapers`, `ctx.hero`, the palette and
   the helpers in `tools/imaging.py`.
3. Write the output under `build/user/` or `build/root/` in the paths the
   desktop expects.
4. Map its output folders to install paths in `tools/install.py`; put its
   defaults in `build/defaults/` and the `DEFAULTS` table.
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
