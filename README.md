# halloween-openSUSE

A cosy autumn Halloween edition of the openSUSE desktop: warm candle-lit
colours, falling leaves, carved pumpkins, and a friendly chameleon inspired by
openSUSE's Geeko. It currently covers KDE Plasma 6 on openSUSE Tumbleweed;
the layout leaves room for other desktops.

> **Status:** work in progress. All artwork is in place; testing on a real
> machine and screenshots come before the first release.

## What's included

| Piece | ID | Where it applies |
|---|---|---|
| Wallpaper (dusk by day, moonlit by night) | `openSUSEhalloween` | desktop and lock screen |
| Plasma style: autumn colours, leaf trim, ember tooltip glow, pumpkin clock | `openSUSE-halloween` | panel, popups, widgets |
| Colour scheme | `openSUSEHalloween` | applications |
| Look-and-feel with pumpkin splash | `org.openSUSE.halloween.desktop` | ties the above together |
| Icons (places, trash, launcher, KDE apps, app menu and power actions) over Breeze Dark | `openSUSE-halloween` | any freedesktop desktop |
| Login screen | `breeze-openSUSE-halloween` | SDDM |
| Boot splash | `openSUSE-halloween` | Plymouth |

openSUSE's green and blue are replaced by an all-autumn palette
([`art/palette.toml`](art/palette.toml)); openSUSE green appears only on the
chameleon.

## Requirements

- openSUSE Tumbleweed with Plasma 6.8 or newer and the openSUSE branding
  (`breeze-openSUSE` SDDM theme, `plymouth`)
- systemd-boot with `sdbootutil`, for the boot splash
- To build: Python 3.12+, `make`, `rsync`, and `git lfs` for the art masters

## Install

Build on any machine and deploy to the target over SSH:

```bash
make install-user TARGET=user@host   # wallpaper, Plasma style, colours, icons, splash
make install-root TARGET=user@host   # login screen; installs the boot splash (asks for sudo)
make plymouth TARGET=user@host       # after testing it: activate the boot splash
make verify TARGET=user@host         # report what is active
```

Or on the machine itself, from a copy of `build/`:

```bash
build/install/install-user.sh
sudo build/install/install-root.sh
sudo build/install/install-root.sh --plymouth
```

`install-root.sh --files` installs without switching anything, for testing
the login screen first. The boot splash only becomes active with
`--plymouth`, which also rebuilds the initrds; until then a kernel update
can't pick it up by surprise.

The user install keeps your panels and widgets. It saves the previous
settings on first run, and `install/uninstall-user.sh` restores them;
`sudo install/uninstall-root.sh` restores the login screen and boot splash.

### If the boot splash causes trouble

- Press <kbd>Esc</kbd> during boot to see the text log.
- Hold <kbd>Space</kbd> at power-on to open the systemd-boot menu and pick an
  older snapshot, or press <kbd>e</kbd> and add `plymouth.enable=0`.
- From a text console (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>F3</kbd>), run
  `sudo build/install/uninstall-root.sh`.

## Build

```bash
make check      # build into build/ and validate it
make release-check   # also fails while placeholders are in use
```

`tools/build.py` makes every size and format from the masters in
`art/source/` (Git LFS). Missing masters are replaced by drawn placeholders,
listed in `build/placeholders.txt`. The Plasma style is generated from
Breeze's SVGs, pinned to libplasma v6.8.0 by hash in `tools/upstream.toml`.

`tools/check.py` validates metadata, colour contrast (7:1 for text, 4.5:1
for the rest), image sizes, file budgets, the Plasma style's SVG element IDs,
icon SVGs, and REUSE compliance.

## Roadmap

- Generated artwork replacing the placeholders
- A fully recoloured Breeze icon set
- GNOME, Xfce and GTK themes, sharing the wallpapers, icons and boot splash

## About the artwork

The artwork is made with generative AI (Picsart), then selected, retouched
and assembled by hand. Every prompt, model and setting is recorded in
[`art/prompts/`](art/prompts/).

## Trademarks

openSUSE and the openSUSE logo are trademarks of SUSE LLC. This project is
not affiliated with or endorsed by SUSE or the openSUSE Project. The
chameleon here is an original character inspired by the Geeko; it is not the
openSUSE logo or a modification of it.

## Credits

- KDE Visual Design Group: Breeze, the Breeze Plasma style and splash
- openSUSE KDE team: the `breeze-openSUSE` login theme and Plasma branding
- Plymouth: the two-step plugin and the spinner theme's dialog images

## Licence

[REUSE](https://reuse.software)-compliant; see [`REUSE.toml`](REUSE.toml)
and the file headers.

- Artwork: CC-BY-SA-4.0
- Plasma style: LGPL-2.0-or-later (derived from Breeze)
- Colour scheme: LGPL-2.0-or-later (derived from Breeze Dark)
- Splash, look-and-feel, Plymouth theme, tools and scripts: GPL-2.0-or-later
- Small config and docs: CC0-1.0
