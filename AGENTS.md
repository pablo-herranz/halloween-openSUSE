# AGENTS.md

Rules for AI coding agents changing halloween-openSUSE. People start with
[README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md); CONTRIBUTING.md
owns the process and the design rules, this file holds what an agent would
otherwise get wrong.

## Ground rules

- **Public content only.** No host names, IP addresses, user names, home
  paths, credentials or account balances of any service, in code, docs,
  commits or the dev helpers. Write `user@testbox`.
- **No AI attribution in commits**: no `Assisted-by:` or `Co-Authored-By:`
  trailers naming an AI. Name the tools in the pull request description.
- **Verify against upstream, not memory.** Keys, selectors, file locations and
  behaviour of KDE, GNOME, Xfce, Plymouth and Firefox come from their source
  or specification (pin it in `tools/upstream.toml`), and the check that relies
  on one says where it comes from.
- **Break it first.** A new check in `tools/check.py` is seen failing on the
  fault it guards against before it passes.
- **One owner per rule.** A rule is written once, where its topic lives; other
  places point at it.
- **Packageable.** Installing copies files and changes no settings, so the
  theme can be an openSUSE RPM. Defaults are declarative files
  (`make install-defaults`); helpers that change settings live in `tools/dev/`.

## Commands

```bash
git lfs install && git lfs pull   # the art masters; without them the build stops or uses placeholders
make check                        # build into build/ and validate it (creates tools/.venv)
make lint                         # ruff, ShellCheck, actionlint, zizmor, typos, editorconfig, reuse
make icon-preview                 # build/icon-preview.png: each icon at 16 to 64 px on dark, light and selection
make release-check                # make check, and fail while any placeholder is in use
make install DESTDIR=/tmp/stage   # install the build like a package would (also install-defaults, uninstall)
```

One file or one desktop at a time:

```bash
tools/.venv/bin/ruff check tools/check.py
tools/.venv/bin/shellcheck -x -P tools/dev tools/dev/verify.sh
tools/.venv/bin/reuse lint
tools/.venv/bin/python tools/build.py --desktop plasma   # the shared pieces plus Plasma's
```

`make check` downloads pinned upstream files into `build/cache/` on its first
run. CI runs the same checks on every pull request.

## Project

A cosy autumn Halloween theme for openSUSE Tumbleweed with KDE Plasma, GNOME
and Xfce. Python in `tools/` builds every installable file into `build/`, and
`tools/install.py` installs them; `docs/architecture.md` shows how it fits
together.

## Where things go

- Colours: only in `art/palette.toml`, by name. Generated files take them from
  the palette, never as hard-coded hex values.
- Hand-written sources: `shared/` for any desktop, `plasma/`, `gnome/` and
  `xfce/` for one. The GTK 3 theme GNOME and Xfce share is built from
  `shared/gtk/`.
- A new build target: copy `tools/targets/sddm.py`, set `DESKTOP`, and add it
  to `TARGETS` in `tools/targets/__init__.py`.
- New icons: an SVG master in `art/source/vectors/`, mapped to icon names in
  `tools/vectors.py`.
- Generated art: record how it was made in `art/prompts/`, in the format of
  the latest record there.
- Install paths: only in the table in `tools/install.py`.
- `build/` is output. `art/source/` holds the masters, in Git LFS.

Every new file starts with an SPDX header or gets a path in `REUSE.toml`:

```python
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
```

Tools and scripts are GPL-2.0-or-later, artwork CC-BY-SA-4.0, the Plasma style
and colour scheme LGPL-2.0-or-later, docs and small config CC0-1.0.

## Design review

Before a pull request that changes how anything looks, do the design review
in CONTRIBUTING.md, "Design review": its checklist is the one place the design
rules live. Do it adversarially, to find faults: one reviewer (a sub-agent,
if you have them) per area, each with the renders and the files:

- icons: `build/icon-preview.png`, `tools/vectors.py`, the masters;
- colours and states: `art/palette.toml`, the built colour scheme and CSS, the
  screenshots;
- the brief: the screenshots, wallpapers and icons against "cosy autumn
  Halloween";
- platform rules: the built files against the upstream source and
  specifications.

Check every finding in the files before acting on it. Fix what holds up, turn
what can be measured into a check (break it first), and list in the pull
request what you fixed and what you declined, with the reason.

## Always

- Run `make check` and `make lint` before committing.
- Keep the build reproducible: the same masters give the same
  `build/MANIFEST.sha256`.
- Keep the screens in the README's "Supported screens" working: crop
  wallpaper-based images with `crop_to()` (`tools/imaging.py`), and keep
  `check_resolutions` and `check_plymouth_layout` passing rather than relaxing
  them.
- Retake the README gallery with `make gallery` after a change that shows (it
  runs the test VM in `tools/dev/vm/`, so it is one of the `TARGET=` targets:
  ask first).

## Ask first

- The `make` targets that take `TARGET=user@host`: they change a real
  machine's settings over SSH.
- `sudo`, installing packages, or changing the user's desktop settings.
- Paid image generation beyond what the task asked for.
- Opening a pull request that isn't a draft, unless the user asked for the
  change to land: the owner's pull requests merge on their own once CI passes.

## Never

- Push to `main`; it is protected. Work on a branch and open a pull request.
- Edit files in `build/`, or hand-edit the masters in `art/source/`.
- Reproduce trademarks: the openSUSE logo, Firefox's logo, other projects'
  brand icons. Image prompts never say "openSUSE", "Geeko" or "logo".
- Relax a check to make it pass.

## Commits and pull requests

An imperative subject line, and a body that says what changed and why. Name
the AI tools you used in the pull request description, and fill in its
checklist.

## When unsure

Ask, or open a draft pull request and say what you're unsure about.

Keep this file short: add a rule only after an agent got something wrong.
