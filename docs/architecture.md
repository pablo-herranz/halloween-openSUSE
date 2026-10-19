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
- **`art/crops.toml`** gives the box every crop of a wallpaper must keep in
  view (the chameleon, its hat and the lanterns), and the parts of the night
  wallpaper used for the splash backdrop and the Firefox header.
  `crop_to()` in `tools/imaging.py` crops to any aspect ratio around that
  box: as centrally as possible for Plasma's per-shape pictures, and centred
  on the box for the `zoomed` pictures that GNOME, Xfce and the login screens
  stretch over any screen.
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
| `sway` | sway | `build/user/openSUSE-halloween/{sway,waybar,swaync}/` |

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

Two checks guard the supported screens (README, "Supported screens"):
`check_resolutions` works out, for common screen sizes and shapes, how much of
the chameleon each desktop shows (with Plasma's own rule for picking a
wallpaper size), and `check_plymouth_layout` lays the boot splash out from 720p
to 4K and portrait and fails if the passphrase prompt, lantern or title would
cover the chameleon.

`make lint` checks the sources: ruff, ShellCheck, actionlint and zizmor for
the workflows, typos, editorconfig-checker and `reuse lint`.

CI (`.github/workflows/check.yml`) runs both on every pull request, as the
Lint and Build and check jobs. A final CI job passes only when both did; it
is the one check `main`'s ruleset requires.

## Install

`tools/install.py` (`make install`) copies the build into the system paths, as
an RPM's `%install` will: its `FILES` table maps each folder in `build/` to an
install path under `PREFIX` (`/usr`) or `LIBDIR`, honouring `DESTDIR`; the
files that name our own installed files (`.xml`, `.override`, `.conf`,
`.plymouth`) follow `PREFIX`. Every entry inside a mapped folder is ours, so `make uninstall`
removes exactly those. `--defaults` (`make install-defaults`) installs the
`DEFAULTS` table instead: declarative vendor files under `/usr`, an SDDM
`conf.d` drop-in in `/usr/lib/sddm/sddm.conf.d/` and a GSettings override,
that make the theme the default the way a separate defaults package would,
while an administrator's choice in `/etc` still wins. Nothing that is
installed changes settings. `check.py` stages an install and uninstall into a
temporary folder on every check, and one under another prefix.

`make dist` packs the release archive: every tracked file, art masters
included (the preferred form for rebuilding), and the build, so `make
install` works from it directly. `MANIFEST.sha256` lists every file the
build installs.

The SDDM theme links openSUSE's `breeze-openSUSE` QML with relative symlinks,
so updates of that package keep flowing in.

The Firefox theme goes to `LIBDIR/firefox/browser/extensions/`: openSUSE
builds Firefox with `--with-unsigned-addon-scopes=app`, so an unsigned add-on
only loads from Firefox's own folder, not from the shared
`/usr/share/mozilla/extensions/` (Firefox 157's `AppConstants` say
`MOZ_REQUIRE_SIGNING: true`, `MOZ_UNSIGNED_APP_SCOPE: true`,
`MOZ_UNSIGNED_SYSTEM_SCOPE: false`). Its package is therefore
architecture-specific, and it must be built for the machine's own
architecture: an i586 package puts the theme in `/usr/lib/firefox`, which a
64-bit Firefox never reads. A Mozilla-signed `.xpi` could use the shared folder.

The SDDM theme builds on openSUSE's `breeze-openSUSE`, as the theme is made
for openSUSE; another distribution would link plain `breeze` instead.

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
emblem glyph in place of its leaf, file types the page master with one on its
sheet, settings icons a glyph carved into the pumpkin master; other icons are
cleaned-up masters, their colours held to the palette by `normalise()`. Add
the SVG master to `art/source/vectors/` and map it to icon names in
`tools/vectors.py` (`FOLDER_EMBLEMS`, `APPS`, `DEVICES`, `SETTINGS`,
`MIME_EMBLEMS`, `SYMBOLIC`, `GNOME_SETTINGS`, `ALIASES`). Symbolic icons are
written in KDE's format so they follow the colour scheme, with a size and plain
coordinates for GTK's own parser, twice: hinted for 16 px in `16x16/`, where
their level edges sit on whole pixels, and exact in `scalable/` for every other
size. Settings icons also
come at 16 and 22 px (`16x16/apps`, `22x22/apps`), where the pumpkin fills the
icon and the glyph nearly fills the pumpkin. Plasma would show our icon for
any Breeze name that only extends one of ours (`tools/kde_lookup.py` mirrors
its lookup), so the Plasma theme's `kde/` folder links those to Breeze Dark's
own; the GNOME and Xfce variant leaves it out. Check the result with
`make icon-preview` and the design review in CONTRIBUTING.md.

## Changing colours

Edit `art/palette.toml` and run `make check`: every generated file picks up
the change, and the contrast checks tell you if a pair of colours became too
close. The Plasma style has no colour file of its own: it takes the colour
scheme's, so a scheme the user picks (high contrast, say) still applies.
