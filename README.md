# halloween-openSUSE

A cosy autumn Halloween theme for openSUSE Tumbleweed with KDE Plasma, GNOME
and Xfce: warm candle-lit colours, falling leaves, carved pumpkins and a
friendly chameleon in a witch hat.

[![Check](https://github.com/plusky/halloween-openSUSE/actions/workflows/check.yml/badge.svg?branch=main)](https://github.com/plusky/halloween-openSUSE/actions/workflows/check.yml)
[![Licence: multiple (REUSE)](https://img.shields.io/badge/licence-multiple_(REUSE)-blue)](#licence)
[![KDE Plasma 6.8+](https://img.shields.io/badge/KDE_Plasma-6.8%2B-1d99f3)](https://kde.org/plasma-desktop/)
[![GNOME 50+](https://img.shields.io/badge/GNOME-50%2B-4a86cf)](https://www.gnome.org/)
[![Xfce 4.20+](https://img.shields.io/badge/Xfce-4.20%2B-2284f2)](https://www.xfce.org/)
[![openSUSE Tumbleweed](https://img.shields.io/badge/openSUSE-Tumbleweed-73ba25)](https://get.opensuse.org/tumbleweed/)

<img src="docs/screenshots/desktop.jpg" width="100%" alt="KDE Plasma desktop with a storybook wallpaper: a green chameleon in a purple witch hat and striped scarf sits on a mossy branch beside three glowing jack-o'-lanterns, birch trees and a rising harvest moon at dusk. The panel at the bottom shows the chameleon launcher and pumpkin-orange app icons.">

| | |
|---|---|
| <img src="docs/screenshots/launcher.jpg" alt="The application launcher in dark plum colours, with Halloween icons for apps, categories and power actions"> | <img src="docs/screenshots/dolphin.jpg" alt="Dolphin file manager with orange folders, each carrying an emblem such as a scroll, an acorn or a film reel"> |
| App launcher | Dolphin with the folder icons |
| <img src="docs/screenshots/desktop-night.jpg" alt="The same wallpaper at night, with stars and the lanterns glowing"> | <img src="docs/screenshots/login.jpg" alt="Login screen over a blurred night version of the wallpaper"> |
| The wallpaper at night | Login screen (SDDM) |
| <img src="docs/screenshots/file-types.jpg" alt="Dolphin showing file icons: cream pages with pumpkin emblems for text, PDF, images, music, video, archives, web pages and scripts"> | <img src="docs/screenshots/firefox.jpg" alt="Firefox with plum toolbars and the moonlit forest behind the tabs"> |
| File types | Firefox theme |
| <img src="docs/screenshots/splash.jpg" alt="Splash screen: the chameleon hugging a jack-o'-lantern above five small lanterns lighting up one by one"> | <img src="docs/screenshots/clock.jpg" alt="An analog clock widget with a carved pumpkin face on the desktop"> |
| Splash screen | Pumpkin clock |
| <img src="docs/screenshots/gnome.jpg" alt="GNOME with the night wallpaper: Files shows orange folders with emblems, and the quick settings menu has plum panels with ember-orange toggles"> | <img src="docs/screenshots/xfce.jpg" alt="Xfce with the night wallpaper: Thunar in dark plum with orange folders, plum window title bar, a dark panel with a pumpkin task button and a Halloween notification"> |
| GNOME | Xfce |

## What's included

| Piece | ID | Works with |
|---|---|---|
| Wallpaper: dusk by day, moonlit by night | `openSUSEhalloween` | Plasma, GNOME (light and dark), Xfce |
| Plasma style: autumn colours, leaf sprig on popups, ember tooltip glow, pumpkin clock | `openSUSE-halloween` | Plasma |
| Colour scheme | `openSUSEHalloween` | Plasma and KDE apps |
| Global theme with a pumpkin splash screen | `org.openSUSE.halloween.desktop` | Plasma |
| Icon theme over Breeze Dark: folders, file types, drives, trash, KDE apps, a web-browser icon (also for Firefox), app-menu and power icons | `openSUSE-halloween` | Plasma |
| The same icons over Adwaita | `openSUSE-halloween-adwaita` | GNOME, Xfce |
| GTK 3 theme: night colours with ember and pumpkin accents, built on [adw-gtk3](https://github.com/lassekongo83/adw-gtk3) | `openSUSE-halloween` | GNOME, Xfce, GTK 3 apps |
| GNOME Shell theme: top bar, menus, quick settings, calendar | `openSUSE-halloween` | GNOME with the User Themes extension |
| Window manager theme, also at 1.5× and 2× | `openSUSE-halloween`, `-hdpi`, `-xhdpi` | Xfce (xfwm4) |
| Notification theme | `openSUSE-halloween` | Xfce (xfce4-notifyd) |
| Login screen, built on openSUSE's `breeze-openSUSE` | `breeze-openSUSE-halloween` | SDDM |
| Boot splash | `openSUSE-halloween` | Plymouth |
| Firefox theme: plum toolbars, pumpkin accents, the moonlit forest behind the tabs | `openSUSE-halloween@pluskal.org` | Firefox |

openSUSE's green and blue are replaced by an all-autumn palette
([`art/palette.toml`](art/palette.toml)); openSUSE green appears only on the
chameleon. All the pieces are dark, like the night they're named after;
libadwaita apps on GNOME keep their own colours but take the orange accent.
See [gnome/](gnome/) and [xfce/](xfce/) for what each edition covers.

## Requirements

- openSUSE Tumbleweed with KDE Plasma 6.8, GNOME 50 or Xfce 4.20, or newer
- For the GNOME Shell theme, the User Themes extension
  (`gnome-shell-extension-user-theme`)
- For the login screen, openSUSE's `breeze-openSUSE` SDDM theme
  (`plasma6-sddm-theme-openSUSE`), which it builds on
- To build: Python 3.11 or newer, `make` and [Git LFS](https://git-lfs.com/)

## Install

The theme installs like a package: `make install` only copies its files into
the system folders and changes no settings. You then choose the pieces you
want. RPM packages for openSUSE are planned and will do the same.

```bash
git lfs install && git lfs pull
make check                   # build into build/ and validate it
sudo make install            # copy the theme to /usr/share and /usr/lib64
sudo make install-defaults   # optional: make it the default (login screen, GNOME)
```

Then pick it:

- **Plasma:** System Settings → *Colors & Themes* → *Global Theme* →
  *openSUSE Halloween*. It brings the Plasma style, colours, icons, splash
  screen and wallpaper; leave *Use desktop layout from theme* unticked to
  keep your panels.
- **Login screen:** System Settings → *Colors & Themes* → *Login Screen
  (SDDM)* → *openSUSE Halloween*, or `make install-defaults`, which adds
  `/etc/sddm.conf.d/zz-openSUSE-halloween.conf`.
- **GNOME:** in Settings → *Appearance*, pick the dark style, the orange
  accent and the *openSUSE Halloween* background. In GNOME Tweaks →
  *Appearance*, pick `openSUSE-halloween` for *Legacy Applications* and *Shell*
  (with the User Themes extension enabled), and `openSUSE-halloween-adwaita`
  for *Icons*. Or let `make install-defaults` do it for everyone who hasn't
  chosen otherwise: it adds a GSettings override (run
  `glib-compile-schemas /usr/share/glib-2.0/schemas` after it) and gives the
  login screen (GDM) the orange accent through dconf (run `dconf update`).
  GDM's background can't be changed.
- **Xfce:** in Settings → *Appearance* pick `openSUSE-halloween` (style) and
  `openSUSE-halloween-adwaita` (icons); in *Window Manager* pick
  `openSUSE-halloween` (or `-hdpi` / `-xhdpi` with display scaling); in
  *Notifications* pick `openSUSE-halloween`; and choose the wallpaper in
  *Desktop* from `/usr/share/wallpapers/openSUSEhalloween/contents/images_dark/`.
  Xfce's defaults come from openSUSE's branding packages, so there are none
  to install. For the login screen (LightDM), an administrator can set
  `theme-name=openSUSE-halloween`, `icon-theme-name=openSUSE-halloween-adwaita`
  and a `background=` from the wallpaper in `/etc/lightdm/lightdm-gtk-greeter.conf`.
- **Boot splash:** note the current theme (`plymouth-set-default-theme`), then
  switch and rebuild the initrds:

  ```bash
  sudo plymouth-set-default-theme openSUSE-halloween
  sudo sdbootutil mkinitrd        # systemd-boot; with GRUB: sudo dracut -f --regenerate-all
  ```

- **Firefox:** `make install` puts the theme into openSUSE Firefox's own
  add-on folder. Restart Firefox and pick it in `about:addons` → *Themes*.
  See [Firefox](#firefox) for other Firefox builds.

### Uninstall

Switch the global theme, login screen and boot splash back first (their files
go away), then:

```bash
sudo make uninstall   # removes every installed file, the defaults included
```

### If the boot splash causes trouble

- Press <kbd>Esc</kbd> during boot to see the text log.
- Hold <kbd>Space</kbd> at power-on to open the systemd-boot menu and pick an
  older snapshot, or press <kbd>e</kbd> and add `plymouth.enable=0`.
- From a text console (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>F3</kbd>), switch
  back with `plymouth-set-default-theme` and rebuild the initrds as above.

### Firefox

The theme only recolours Firefox; Firefox's own logo stays as it is. The
`.xpi` (`build/firefox/openSUSE-halloween.xpi`) isn't signed by Mozilla, and
regular Firefox releases only install signed add-ons:

- **openSUSE's Firefox:** it is built to load unsigned add-ons only from its
  own folder, which is where `make install` puts the theme
  (`/usr/lib64/firefox/browser/extensions/openSUSE-halloween@pluskal.org.xpi`).
  Only put files there that you built or trust.
- **Firefox Developer Edition, Nightly or ESR:** set
  `xpinstall.signatures.required` to `false` in `about:config`, then choose
  ⚙ → *Install Add-on From File…* in `about:addons`.
- **Any Firefox, until it restarts:** choose *Load Temporary Add-on…* in
  `about:debugging#/runtime/this-firefox`.

## Contributing

Contributions are welcome: new icons, fixes, other desktops. Start with
[CONTRIBUTING.md](CONTRIBUTING.md), which covers the development setup, how
the build works and how to propose artwork. AI coding agents should read
[AGENTS.md](AGENTS.md). Everyone is expected to follow the
[code of conduct](CODE_OF_CONDUCT.md).

```bash
make check   # build everything into build/ and validate it
make lint    # ruff, ShellCheck, workflow, spelling and licence checks
```

How the pieces fit together is in [docs/architecture.md](docs/architecture.md).

## Roadmap

- openSUSE RPM packages, built in the Open Build Service, for the
  distribution

## About the artwork

The artwork is made with generative AI (Picsart: Flux 2 Pro, Nano Banana 2 and
Recraft), then selected, cut out, retouched and composed by hand: every folder
icon is assembled from a master folder and an emblem, crops and colours are
adjusted by the build tools. Every prompt, model, setting and choice is
recorded in [`art/prompts/`](art/prompts/).

Purely AI-generated material may not be protected by copyright in some
countries (see the US Copyright Office's 2025 report on copyrightability). The
licence below covers the human selection, composition and editing.

## Trademarks

openSUSE and the openSUSE logo are trademarks of SUSE LLC. This project is
not affiliated with or endorsed by SUSE or the openSUSE Project. The chameleon
is an original character inspired by the Geeko; it is not the openSUSE logo
or a modification of it.

Firefox is a trademark of the Mozilla Foundation. The Firefox theme only sets
colours and a header image, and the icon theme's web-browser icon is an
original drawing, not Firefox's logo.

## Credits

- KDE Visual Design Group: Breeze, the Breeze Plasma style and splash
- openSUSE KDE team: the `breeze-openSUSE` login theme and Plasma branding
- Plymouth: the two-step plugin and the spinner theme's dialog images
- lassekongo83 and the adw-gtk3 contributors: adw-gtk3, which the GTK 3 theme
  is built on
- Olivier Fourdan and the Xfce team: xfwm4's default theme, which the window
  manager theme recolours

## Licence

[REUSE](https://reuse.software)-compliant: every file's licence is in its
header or in [`REUSE.toml`](REUSE.toml), and the texts are in
[`LICENSES/`](LICENSES/).

- Artwork, including the icons and the Firefox theme: CC-BY-SA-4.0
- Plasma style and colour scheme: LGPL-2.0-or-later (derived from Breeze)
- GTK 3 theme: LGPL-2.1-or-later (derived from adw-gtk3, LGPL-2.1)
- Splash, look-and-feel, Plymouth theme, GNOME Shell stylesheet, Xfce window
  manager and notification themes, tools and scripts: GPL-2.0-or-later
- Documentation and small configuration files: CC0-1.0
