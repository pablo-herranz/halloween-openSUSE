# AGENTS.md

Instructions for AI coding agents working on halloween-openSUSE. People should
start with [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Project

A desktop theme for openSUSE Tumbleweed: wallpapers, a KDE Plasma style,
colour scheme, global theme with splash, a freedesktop icon theme, an SDDM
login theme, a Plymouth boot splash and a Firefox theme. Python scripts in
`tools/` build every installable file into `build/` from the art masters in
`art/source/` (Git LFS) and the sources in `shared/` and `plasma/`. Bash
scripts in `install/` install them.

## Setup and commands

```bash
git lfs install && git lfs pull   # without the masters, the build stops or uses placeholders
make check                        # build into build/ and validate it; must pass before every commit
make lint                         # ruff (tools/) and ShellCheck (install/, tools/*.sh)
make icon-preview                 # build/icon-preview.png, every icon at 16 to 64 px
tools/.venv/bin/python tools/build.py --desktop plasma   # shared pieces plus one desktop
```

`make check` uses the network once, to fetch pinned Breeze SVGs into
`build/cache/`. The `make` targets that take `TARGET=user@host` need SSH access
to a test machine; never run them unless the user asks.

## Layout

- `shared/`: desktop-neutral sources (wallpapers, icons, Plymouth, Firefox)
- `plasma/`: KDE Plasma sources (colour scheme, Plasma style, global theme, SDDM)
- `gnome/`, `xfce/`: notes for planned editions; no code yet
- `tools/build.py`: runs the targets in `tools/targets/` (one module per
  piece, with `DESKTOP` and `build(ctx)`); `tools/context.py` holds the
  palette and masters; `tools/imaging.py` the image helpers
- `tools/check.py`: everything `make check` validates
- `tools/vectors.py`: composes icons and ornaments from the SVG masters
- `art/palette.toml`: the only place colours are defined
- `art/prompts/`: provenance of every generated asset
- `docs/architecture.md`: how it fits together

## Conventions

- Python 3.11+, formatted for ruff's rules in `pyproject.toml` (line length
  120). Bash with `set -euo pipefail`, clean under ShellCheck.
- Colours come from `art/palette.toml`, never hard-coded hex values in
  generated files. Keep the contrast rules in `tools/check.py` passing.
- Generated SVG icons must stay under 60 kB, with no text, scripts, embedded
  images or external links.
- Keep the build reproducible: the same masters give the same
  `build/MANIFEST.sha256`.

## Licensing

Every new file needs an SPDX header or a path in `REUSE.toml`; `make check`
runs `reuse lint`. Artwork is CC-BY-SA-4.0, the Plasma style and colour
scheme LGPL-2.0-or-later, tools and scripts GPL-2.0-or-later, docs and small
config CC0-1.0.

## Don't

- Edit anything in `build/`, or hand-edit LFS masters in `art/source/`.
- Commit generated sizes of art; the build makes them.
- Reproduce or modify trademarks: the openSUSE logo, Firefox's logo, other
  projects' brand icons. Image prompts never say "openSUSE", "Geeko" or "logo".
- Use `sudo`, install packages or change the user's desktop settings, unless
  the user asks.
- Push to `main`: it is protected. Work on a branch and open a pull request;
  CI (ShellCheck, Ruff, REUSE, Build and check) must pass before it can merge.

## Commits and pull requests

Imperative subject line, a body that says what changed and why, and an
`Assisted-by:` trailer naming the agent. Record new generated art in
`art/prompts/`. Fill in the pull request checklist.
