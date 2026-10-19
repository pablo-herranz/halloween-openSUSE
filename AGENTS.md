# AGENTS.md

Instructions for AI coding agents working on halloween-openSUSE. People should
start with [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Commands

```bash
git lfs install && git lfs pull   # the art masters; without them the build stops or uses placeholders
make check                        # build into build/ and validate it (creates tools/.venv)
make lint                         # ruff, ShellCheck, actionlint, zizmor, typos, editorconfig, reuse
make icon-preview                 # build/icon-preview.png: every icon at 16 to 64 px
make release-check                # make check, and fail while any placeholder is in use
```

One file or one desktop at a time:

```bash
tools/.venv/bin/ruff check tools/check.py
tools/.venv/bin/shellcheck -x -P install install/verify.sh
tools/.venv/bin/reuse lint
tools/.venv/bin/python tools/build.py --desktop plasma   # the shared pieces plus Plasma's
```

`make check` downloads pinned Breeze SVGs into `build/cache/` on its first
run. CI runs the same checks on every pull request.

## Project

A Halloween desktop theme for openSUSE Tumbleweed and KDE Plasma 6. Python in
`tools/` builds every installable file into `build/`; bash in `install/`
installs it.

## Where things go

- Colours: only in `art/palette.toml`, by name. Generated files take them from
  the palette, never as hard-coded hex values.
- Hand-written sources: `shared/` for any desktop, `plasma/` for KDE Plasma.
  `gnome/` and `xfce/` are plans with no code yet.
- A new build target: copy `tools/targets/sddm.py`, set `DESKTOP`, and add it
  to `TARGETS` in `tools/targets/__init__.py`.
- New icons: an SVG master in `art/source/vectors/`, mapped to icon names in
  `tools/vectors.py`.
- Generated art: record how it was made in `art/prompts/`, in the format of
  `art/prompts/08-more-icons.md`.
- `build/` is output. `art/source/` holds the masters, in Git LFS.

Every new file starts with an SPDX header or gets a path in `REUSE.toml`:

```python
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
```

Tools and scripts are GPL-2.0-or-later, artwork CC-BY-SA-4.0, the Plasma style
and colour scheme LGPL-2.0-or-later, docs and small config CC0-1.0.

## Always

- Run `make check` and `make lint` before committing.
- Keep the build reproducible: the same masters give the same
  `build/MANIFEST.sha256`.
- After changing art or icons, run `make icon-preview` and look at
  `build/icon-preview.png`.
- Add before/after screenshots to pull requests that change how something
  looks.

## Ask first

- The `make` targets that take `TARGET=user@host`: they install on a real
  machine over SSH.
- `sudo`, installing packages, or changing the user's desktop settings.
- Opening a pull request that isn't a draft, unless the user asked for the
  change to land: the owner's pull requests merge on their own once CI passes.

## Never

- Push to `main`; it is protected. Work on a branch and open a pull request.
- Edit files in `build/`, or hand-edit the masters in `art/source/`.
- Reproduce trademarks: the openSUSE logo, Firefox's logo, other projects'
  brand icons. Image prompts never say "openSUSE", "Geeko" or "logo".
- Credit AI tools in commits: no `Assisted-by:` or `Co-Authored-By:` trailers
  naming an AI.

## Commits and pull requests

An imperative subject line, and a body that says what changed and why. Name
the AI tools you used in the pull request description, and fill in its
checklist.

## When unsure

Ask, or open a draft pull request and say what you're unsure about.

Keep this file short: add a rule only after an agent got something wrong.
