# Contributing to halloween-openSUSE

Thanks for helping! Fixes, new icons, better artwork and new desktops are all
welcome. By taking part you agree to follow the
[code of conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report a bug** or a part of the desktop that still looks un-themed:
  open an issue with the bug form, with a screenshot if you can.
- **Propose artwork** (an icon, a wallpaper, an ornament): open an issue with
  the art request form first, so the idea can be agreed before work starts.
- **Add a desktop** (GNOME, Xfce): read [docs/architecture.md](docs/architecture.md)
  and the notes in [gnome/](gnome/) or [xfce/](xfce/), then open an issue to
  coordinate.
- **Improve the build tools or install scripts.**

Security problems go privately, as described in [SECURITY.md](SECURITY.md).

## Development setup

Building works on any Linux or macOS machine; trying the theme needs openSUSE
Tumbleweed with KDE Plasma 6.8 or newer.

```bash
git clone https://github.com/<you>/halloween-openSUSE.git
cd halloween-openSUSE
git lfs install && git lfs pull   # the art masters in art/source/ are in Git LFS
make check                        # creates tools/.venv, builds into build/, validates it
make lint                         # ruff and ShellCheck, as CI runs them
```

You need Python 3.11 or newer, `make` and Git LFS. `make check` downloads a
few pinned Breeze SVGs from invent.kde.org on its first run and caches them in
`build/cache/`.

## Layout

| Path | What it holds |
|---|---|
| `shared/` | Desktop-neutral pieces: wallpapers, icon theme, Plymouth boot splash, Firefox theme |
| `plasma/` | KDE Plasma: colour scheme, Plasma style, global theme with splash, SDDM login theme |
| `gnome/`, `xfce/` | Notes for the planned editions |
| `art/` | The palette, crop focus points, prompt records, and the art masters (`source/`, Git LFS) |
| `tools/` | The build (`build.py`, `targets/`), checks (`check.py`) and helpers |
| `install/` | Install, uninstall, verify and screenshot scripts, copied to `build/install/` |
| `docs/` | Architecture notes and the README screenshots |

Never edit anything in `build/`: it is generated. See
[docs/architecture.md](docs/architecture.md) for how the pieces fit together.

## Workflow

`main` is protected: every change goes through a pull request, and a pull
request can only be merged when CI passes (ShellCheck, Ruff, REUSE and Build
and check).

1. Fork the repository and create a branch for one change.
2. Make the change, then run `make check` and `make lint`.
3. If it changes how something looks, add before/after screenshots to the
   pull request.
4. Open the pull request and fill in its checklist.

Keep pull requests focused: one icon set, one fix, one feature.

### Trying it on a machine

On the openSUSE machine itself, use the scripts in `build/install/` as the
README describes. While developing on another computer, the `make` targets
that take `TARGET=user@host` build here, copy `build/` to the test machine over
SSH and run the same scripts there:

```bash
make install-user TARGET=user@testbox
make verify TARGET=user@testbox
make screens TARGET=user@testbox && make fetch-screenshots TARGET=user@testbox
make previews   # turn the screenshots into package previews and README images
```

## Commit messages

Write the subject in the imperative mood ("Add folder icons for videos"),
keep it under about 70 characters, and use the body to explain what changed
and why. Mention the issue it fixes, for example `Fixes #12`.

## Licensing

Contributions are accepted under the licence of the files they change
(inbound = outbound); there is no CLA. The project is
[REUSE](https://reuse.software)-compliant, and CI fails if a file has no
licence:

- New source files get an SPDX header, like the existing ones.
- Files that can't carry a header (images, generated SVGs) are covered by
  `REUSE.toml`; add a path there if needed, or run
  `reuse annotate --copyright "Your Name <you@example.org>" --license <SPDX-ID> <file>`.

| Area | Licence |
|---|---|
| Artwork: wallpapers, icons, art masters, screenshots, Firefox theme | CC-BY-SA-4.0 |
| Plasma style and colour scheme (derived from Breeze) | LGPL-2.0-or-later |
| Look-and-feel, splash, Plymouth theme, tools and scripts | GPL-2.0-or-later |
| Documentation and small configuration files | CC0-1.0 |

## Artwork

- **Agree on the idea first** in an art request issue.
- **Use the palette** in [`art/palette.toml`](art/palette.toml). `make check`
  enforces contrast (7:1 for text, 4.5:1 for the rest) and size limits.
- **Masters go in `art/source/`** (Git LFS): raster masters as PNG, icon and
  ornament masters as SVG in `art/source/vectors/`. The build makes every size
  and format from them; don't commit generated sizes.
- **Record provenance** in `art/prompts/NN-short-name.md`: model, settings,
  the full prompt, references, which variant was chosen and why, and any
  post-processing. See [`art/prompts/README.md`](art/prompts/README.md).
- **Respect trademarks.** Never reproduce or modify the openSUSE logo (the
  chameleon is an original character) or other projects' logos, such as
  Firefox's. Prompts never say "openSUSE", "Geeko" or "logo".

### Adding icons

Icons are composed by [`tools/vectors.py`](tools/vectors.py) from the SVG
masters: folder icons are the master folder plus an emblem glyph, and the
mapping from masters to icon names is in `FOLDER_EMBLEMS`, `APPS`, `SYMBOLIC`
and `ALIASES` there. `make icon-preview` renders the whole set at 16 to 64 px
into `build/icon-preview.png`; check the small sizes before opening a pull
request.

## AI-assisted contributions

AI tools are welcome for code and art, as long as you say so:

- Mention the tools in the pull request.
- Add an `Assisted-by: <tool or model>` trailer to the commits.
- You are responsible for the result: review it, test it, and make sure you
  have the right to contribute it under the project's licences.

AI coding agents should follow [AGENTS.md](AGENTS.md).
