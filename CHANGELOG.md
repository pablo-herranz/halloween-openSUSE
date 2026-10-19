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
- Plymouth boot splash `openSUSE-halloween`, with the disk passphrase prompt
  below the chameleon; it brings its own copy of Plymouth's prompt images
- GNOME edition: a GTK 3 theme built on adw-gtk3, a GNOME Shell stylesheet,
  the wallpaper in Settings (dusk light, night dark), and optional defaults
  (GSettings override with the orange accent; GDM accent through dconf)
- Xfce edition: the GTK 3 theme with panel styling, xfwm4's default theme in
  the palette at three scales, and a notification theme
- Icon theme `openSUSE-halloween-adwaita`: the same icons over Adwaita, for
  GNOME and Xfce, including GNOME's and Xfce's own file manager, terminal,
  settings, editor, image viewer, software, system monitor, archive,
  scanner, screenshot, passwords and characters apps
- Icons for the apps GNOME and Xfce ship by default and their KDE
  counterparts (calculator, clocks, contacts, maps, mail, music, videos,
  notes, logs and more), YaST, printers, phones, input devices, headphones,
  displays and computers, each with one seasonal touch; settings dialogs show
  their glyph carved into a pumpkin, so they tell apart at 16 px; Thunar's
  Home and Xfce's show-desktop button use the theme's one-colour glyphs, and
  the optional defaults turn IBus's blue layout indicator cream
- Firefox theme, with a header that stays sharp on HiDPI screens
- `make install`, which installs the theme like a package: it copies the files
  into the system paths and changes no settings; `make install-defaults` adds
  optional defaults (the login screen) and `make uninstall` removes both
- Development helpers in `tools/dev/` that apply, verify and screenshot the
  theme on a test machine, and a headless GNOME and Xfce test VM
  (`tools/dev/vm/`)
- Build tools that make every size and format from the art masters, with
  checks for contrast, sizes, Plasma compatibility and REUSE compliance
- Contributor documentation, AGENTS.md and continuous integration, with a
  design review checklist (CONTRIBUTING.md) whose measurable rules are checks:
  WCAG contrast for every text, focus, selection and on/off colour on Plasma,
  GTK, Firefox and the login screen's labels; one-colour icons that Qt can
  recolour; no GTK-only colour functions in the GNOME Shell stylesheet; and
  no unthemed colours in the boot splash's prompt
- Wallpapers for every common screen shape (16:9 to 5K, 16:10 to 4K, 3:2,
  21:9, 32:9, 4:3, 5:4 and portrait), cropped around the chameleon, and one
  16:10 picture per variant that GNOME and Xfce zoom to any screen
- Checks that the supported screens keep working: how much of the chameleon
  each desktop shows on common screens, and the boot splash's layout from
  720p to 4K
