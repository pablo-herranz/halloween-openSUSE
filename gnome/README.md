# GNOME edition

What GNOME gets, next to the shared wallpapers, Plymouth boot splash and
Firefox theme:

| Piece | Installed as | Built by |
|---|---|---|
| GTK 3 theme: adw-gtk3-dark with the palette's colours | `/usr/share/themes/openSUSE-halloween/gtk-3.0/` | `tools/targets/gtk.py` from [`shared/gtk/`](../shared/gtk/) |
| GNOME Shell stylesheet for the User Themes extension | `/usr/share/themes/openSUSE-halloween/gnome-shell/` | `tools/targets/gnome.py` from [`gnome-shell/`](gnome-shell/) |
| Icons over Adwaita | `/usr/share/icons/openSUSE-halloween-adwaita/` | `tools/targets/icons.py` |
| Wallpaper entry for Settings, dusk (light) and night (dark) | `/usr/share/gnome-background-properties/openSUSEhalloween.xml` | `tools/targets/gnome.py` |

`make install-defaults` adds the optional defaults from [`defaults/`](defaults/):

- `30_openSUSE-halloween.gschema.override`: GTK and icon theme, dark style,
  orange accent, wallpaper and lock screen, and the Shell theme with the User
  Themes extension enabled. It sorts after openSUSE's
  `20_openSUSE-branding` override, and only applies to settings a user hasn't
  changed. Packages run `glib-compile-schemas` through a file trigger.
- a `gdm` dconf profile and `gdm.d/30-openSUSE-halloween`: the login screen
  with the orange accent and dark style (`dconf update` afterwards). GDM's
  background can't be changed without patching GNOME Shell.

libadwaita (GTK 4) apps keep GNOME's own colours and take the orange accent;
recolouring them would mean overwriting each user's `~/.config/gtk-4.0/gtk.css`,
which GNOME doesn't support.

Tested on Tumbleweed with GNOME 50, in the development VM (`tools/dev/vm/`).
