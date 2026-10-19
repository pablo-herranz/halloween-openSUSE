# Changelog

All notable changes are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions are
calendar-based: `YYYY.MM.patch`.

## [Unreleased]

The first release, 2026.10.0, is being prepared.

### Added

- Wallpaper `openSUSEhalloween`: a storybook birch forest with the chameleon,
  in a dusk (light) and a night (dark) variant at common screen sizes
- KDE Plasma:
  - colour scheme `openSUSEHalloween`
  - Plasma style `openSUSE-halloween` with a leaf sprig on popups, an ember
    tooltip glow and a pumpkin analog clock
  - global theme `org.openSUSE.halloween.desktop` with a splash screen whose
    lanterns light up as the session starts
  - SDDM login theme `breeze-openSUSE-halloween`
- Icon theme `openSUSE-halloween` over Breeze Dark: folders and places, file
  types, drives and removable media, trash, the launcher, KDE apps, an
  original web-browser icon used for Firefox too, the app menu's categories
  and the power and session actions; symbolic icons follow the colour scheme
- Plymouth boot splash `openSUSE-halloween`
- GNOME edition: a GTK 3 theme built on adw-gtk3, a GNOME Shell stylesheet,
  the wallpaper in Settings (dusk light, night dark), and optional defaults
  (GSettings override with the orange accent; GDM accent through dconf)
- Xfce edition: the GTK 3 theme with panel styling, xfwm4's default theme in
  the palette at three scales, and a notification theme
- Icon theme `openSUSE-halloween-adwaita`: the same icons over Adwaita, for
  GNOME and Xfce
- Firefox theme
- `make install`, which installs the theme like a package: it copies the files
  into the system paths and changes no settings; `make install-defaults` adds
  optional defaults (the login screen) and `make uninstall` removes both
- Development helpers in `tools/dev/` that apply, verify and screenshot the
  theme on a test machine, and a headless GNOME and Xfce test VM
  (`tools/dev/vm/`)
- Build tools that make every size and format from the art masters, with
  checks for contrast, sizes, Plasma compatibility and REUSE compliance
- Contributor documentation, AGENTS.md and continuous integration
