# Contributing to halloween-openSUSE

Thanks for helping! Fixes, new icons, better artwork and new desktops are all
welcome. By taking part you agree to follow the
[code of conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report a bug** or a part of the desktop that still looks un-themed:
  open an issue with the bug form, with a screenshot if you can.
- **Propose artwork** (an icon, a wallpaper, an ornament): open an issue with
  the art request form first, so the idea can be agreed before work starts.
- **Add a desktop** (MATE, Cinnamon, …) or improve the GNOME and Xfce
  editions: read [docs/architecture.md](docs/architecture.md) and the notes in
  [gnome/](gnome/) and [xfce/](xfce/), then open an issue to coordinate.
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
make lint                         # ruff, ShellCheck, workflow, spelling and licence checks, as CI runs them
```

You need Python 3.11 or newer, `make` and Git LFS, and `rsvg-convert` for
`make icon-preview` (`librsvg2-tools` on openSUSE, `librsvg` on Homebrew).
`make check` downloads the pinned upstream files in `tools/upstream.toml`
(Breeze SVGs, adw-gtk3, xfwm4, Plymouth's prompt images) on its first run
and keeps them in `build/cache/`; a file already there with the pinned
SHA-256 is used as it is, so a package build can put them there from its
sources and build offline.

## Layout

| Path | What it holds |
|---|---|
| `shared/` | Desktop-neutral pieces: wallpapers, icon theme, Plymouth boot splash, Firefox theme, the GTK 3 colours |
| `plasma/` | KDE Plasma: colour scheme, Plasma style, global theme with splash, SDDM login theme |
| `gnome/` | GNOME: Shell stylesheet, defaults (GSettings override) |
| `xfce/` | Xfce: window manager colours, notification theme |
| `art/` | The palette, crop focus points, prompt records, and the art masters (`source/`, Git LFS) |
| `tools/` | The build (`build.py`, `targets/`), checks (`check.py`), the installer (`install.py`) and helpers |
| `tools/dev/` | Development helpers for a test machine: apply, verify and screenshot the theme; `vm/` runs a GNOME and Xfce test VM |
| `docs/` | Architecture notes and the README screenshots |

Never edit anything in `build/`: it is generated. See
[docs/architecture.md](docs/architecture.md) for how the pieces fit together.

## Workflow

`main` is protected: every change goes through a pull request, and a pull
request can only be merged when its `CI` check passes, which means both jobs
passed: Lint (`make lint`) and Build and check (`make check`). The
maintainer's own pull requests and Dependabot's merge by themselves once CI
passes; everyone else's are reviewed and merged by the maintainer. Pull
requests are rebased onto `main` (no merge or squash commits), so keep each
commit meaningful and self-contained.

1. Fork the repository and create a branch for one change.
2. Make the change, then run `make check` and `make lint`.
3. If it changes how something looks, do the [design review](#design-review)
   and add before/after screenshots to the pull request.
4. Open the pull request and fill in its checklist.

Keep pull requests focused: one icon set, one fix, one feature.

### Trying it on a machine

`make install` only copies files, as a package does (see the README). For a
quick round trip while developing, the helpers in `tools/dev/` also apply the
theme to a Plasma session, save the previous settings and restore them on
uninstall. They change settings, so use them only on a test machine. The
`make` targets that take `TARGET=user@host` build here, copy `build/` and the
helpers to the test machine over SSH and run them there:

```bash
make install-user TARGET=user@testbox   # and install-root, plymouth
make verify TARGET=user@testbox
make screens TARGET=user@testbox && make fetch-screenshots TARGET=user@testbox
make previews   # turn the screenshots into package previews and README images
```

For GNOME and Xfce, `tools/dev/vm/vm.sh` runs a throwaway Tumbleweed VM with
both desktops on any Linux machine with KVM, headless, and takes screenshots
through QEMU. Install a release tarball into it like a package would:

```bash
tools/dev/vm/vm.sh create                 # once: image, disk, both desktops
make check && tools/dist.sh
tools/dev/vm/vm.sh install dist/halloween-openSUSE-*.tar.gz
tools/dev/vm/vm.sh desktop xfce           # or gnome; reboots and logs in
tools/dev/vm/vm.sh shot xfce              # ~/vm-halloween/shots/xfce.png
```

The README's screenshots all come from that VM. After a change that shows,
retake them all in one go: `make gallery TARGET=user@host` builds a release
tarball, installs it in the VM on that host, takes every screenshot on Plasma,
GNOME and Xfce at 1920x1080, copies them to `art/screenshots/` and remakes
the README images in `docs/screenshots/`. Commit both with the change.

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
  enforces contrast (see the [design review](#design-review)) and size limits.
- **Masters go in `art/source/`** (Git LFS): raster masters as PNG, icon and
  ornament masters as SVG in `art/source/vectors/`. The build makes every size
  and format from them; don't commit generated sizes.
- **Record provenance** in `art/prompts/NN-short-name.md`: model, settings,
  the full prompt, references, which variant was chosen and why, and any
  post-processing. See [`art/prompts/README.md`](art/prompts/README.md).
- **Respect trademarks.** Never reproduce or modify the openSUSE logo (the
  chameleon is an original character) or other projects' logos, such as
  Firefox's. Prompts never say "openSUSE", "Geeko" or "logo".

Everything has to work on the screens listed under "Supported screens" in
the README, from 1366x768 to 5K, 3:2, ultrawide and portrait, at 100% to 200%
scaling. Crop pictures made from the wallpaper with `crop_to()`, which keeps
the chameleon box in `art/crops.toml` in view, and check unusual shapes and
scales in the test VM (`HALLOWEEN_VM_RES=2256x1504 tools/dev/vm/vm.sh boot`).

### Adding icons

Icons are composed by [`tools/vectors.py`](tools/vectors.py) from the SVG
masters: folder icons are the master folder plus an emblem glyph, file types
the page master plus one, settings icons a glyph carved into the pumpkin
master. The mapping from masters to icon names is in `FOLDER_EMBLEMS`, `APPS`,
`DEVICES`, `SETTINGS`, `MIME_EMBLEMS`, `SYMBOLIC` and `ALIASES` there, and
`normalise()` holds every colour master to the palette. Generate colour icons
with the master folder as style reference, so they stay one family (see the
latest record in `art/prompts/`). `make icon-preview` renders each distinct
icon at 16 to 64 px on the dark, light and selection colours into
`build/icon-preview.png`, for the design review.

## Design review

Every pull request that changes how something looks gets a design review
before it is opened: art, icons, colours, CSS, layouts. Review it to find
faults, not to approve it: for each point below, look for the case where it
fails, on `build/icon-preview.png`, the screenshots from `make gallery` and the
built files. Most of the measurable rules are tests in `make check`; the rest
need eyes. Put what you looked at, what you found, what you fixed and what
you left (and why) in the pull request.

### The brief

- **Cosy autumn Halloween**: warm, friendly and seasonal (pumpkins, candles,
  lanterns, moons, leaves, acorns, bats, the chameleon), never gory or really
  scary, and still a desktop for every day.
- **One seasonal accent per icon, at most**, and it never hides what the icon
  is. Prefer autumn (a leaf, an acorn, a candle, a pumpkin); bats on no more
  than about one icon in five. Nothing from another season (gifts, snow).
- **One family**: the flat style of the master folder, `art/source/vectors/folder.svg`:
  a few large flat shapes, two tones per colour, a front view, no outlines,
  gradients, textures or shadows.
- **No brand marks**: nothing that reads as the openSUSE logo, Firefox's, the
  Bluetooth rune or another project's mark, even by accident (a rounded square
  with a ring and a corner dot is Instagram's).

### Icons

- Legible at 16, 22 and 32 px on the dark panel, a light background and the
  ember selection. A detail smaller than a pixel goes.
- The picture fits every name it is mapped to. If it doesn't fit one, map
  fewer names and let Breeze or Adwaita show theirs. Two apps that sit side by
  side never share an icon.
- Action and status names (`system-search`, `go-*`, `edit-*`, `*-symbolic`)
  stay one colour; apps, places, devices and file types may be in colour.
- One-colour icons take the colour scheme's text colour: the class
  `ColorScheme-Text` and `fill="currentColor"` on the same element, or Qt
  draws them black (`make check`), and straight edges on the 16 px grid.
- Colours come from the palette (`normalise()` in `tools/vectors.py`).

### Colours and states

- Contrast as in WCAG 2.2, measured by `make check` wherever it can: 7:1 for
  body text here, 4.5:1 for other text (links, status colours, text on the
  selection), 3:1 for focus rings, the selection, on/off states and the edges
  of fields. Text over a picture (login, lock screen, splash) is measured too,
  over the picture as it is shown; add a scrim where it falls short.
- One role, one colour on every desktop: hover is a plum tint, keyboard focus
  a pumpkin ring, selected and checked ember behind white text, levels and
  sliders pumpkin, links apricot and visited links plum. Focus never looks
  like hover.
- The status colours (olive, candle, cranberry) mean status only: no
  decoration in them, and status is never shown by colour alone.

### Screens and platforms

- Everything works on the screens in the README's "Supported screens" (see
  [Artwork](#artwork)).
- Follow the platform's own rules, checked in its source or specification
  rather than from memory: the KDE and GNOME guidelines, the freedesktop icon
  naming specification, what GNOME Shell's CSS understands (no `alpha()`),
  what Plymouth's two-step plugin does. Pin what you rely on in
  `tools/upstream.toml`.

### Turning a finding into a check

When a finding can be measured, add a test to `tools/check.py` so it stays
fixed. Break it first: a check that has never failed is not yet a check. Run
it on the build that has the fault and watch it fail, then fix the fault and
watch it pass.

## Releasing (maintainers)

Versions are calendar-based, `YEAR.MONTH.PATCH`, with the month written
without a leading zero (`2026.10.0`, `2027.3.1`): the version also goes into
the Firefox theme, and Firefox rejects version numbers with leading zeros.
`make check` checks the form. A package built from a git snapshot names it
after the release it relates to: `2026.10.0+git20261020.1a2b3c4` for a commit
after 2026.10.0, `2026.11.0~git20261020.1a2b3c4` for one on the way to
2026.11.0. RPM and zypper sort `+` after the release and `~` before it
(`zypper vcmp` shows it), so users always get the release itself.

1. In a pull request, set `VERSION` in `tools/common.py` and move the
   `[Unreleased]` notes in `CHANGELOG.md` under the new version.
2. After it is merged, tag `main` and push the tag:
   `git tag v2026.10.0 && git push origin v2026.10.0`.
3. The release workflow checks that the tag matches `VERSION`, runs
   `make release-check` (which fails while placeholders are in use), builds
   the archives with `make dist` (the sources with the masters, and the
   build), attests their build provenance and publishes a GitHub release
   with them.

Releases are immutable, and release tags can't be moved or deleted: a broken
release needs a new version. `make dist` builds the same archives locally,
into `dist/`. To check that a downloaded archive was built by the release
workflow:

```bash
gh attestation verify halloween-openSUSE-2026.10.0.tar.gz --repo plusky/halloween-openSUSE
```

## AI-assisted contributions

AI tools are welcome for code and art, as long as you say so:

- Mention the tools in the pull request.
- Don't credit them in commits: no `Assisted-by:` or `Co-Authored-By:`
  trailers naming an AI tool.
- You are responsible for the result: review it, test it, and make sure you
  have the right to contribute it under the project's licences.

AI coding agents should follow [AGENTS.md](AGENTS.md).
