# GNOME edition

What GNOME gets, next to the shared wallpapers, Plymouth boot splash and
Firefox theme:

| Piece | Installed as | Built by |
|---|---|---|
| GTK 3 theme: adw-gtk3-dark with the palette's colours | `/usr/share/themes/openSUSE-halloween/gtk-3.0/` | `tools/targets/gtk.py` from [`shared/gtk/`](../shared/gtk/) |
| GNOME Shell stylesheet for the User Themes extension | `/usr/share/themes/openSUSE-halloween/gnome-shell/` | `tools/targets/gnome.py` from [`gnome-shell/`](gnome-shell/) |
| Icons over Adwaita | `/usr/share/icons/openSUSE-halloween-adwaita/` | `tools/targets/icons.py` |
| Wallpaper entry for Settings, dusk (light) and night (dark), pointing at the 16:10 pictures in `/usr/share/backgrounds/openSUSEhalloween/` | `/usr/share/gnome-background-properties/openSUSEhalloween.xml` | `tools/targets/gnome.py`, `wallpapers.py` |

`make install-defaults` adds the optional defaults from [`defaults/`](defaults/):

- `30_openSUSE-halloween.gschema.override`: dark style and orange accent,
  for the session and, in a `GNOME-Greeter` group, the login screen (GDM);
  the wallpaper; the Shell theme's name for the User Themes extension; and
  IBus's keyboard layout indicator in cream (on every desktop where IBus
  runs; blue otherwise). It leaves the GTK and icon theme to the user (GNOME
  Tweaks), as openSUSE's glib2 branding asks them to match `gtk3-branding`,
  and it doesn't touch the list of enabled Shell extensions. It sorts after
  openSUSE's
  `20_openSUSE-branding` override, and only applies to settings a user hasn't
  changed. Packages run `glib-compile-schemas` through a file trigger.

GDM's background can't be changed without patching GNOME Shell.

libadwaita (GTK 4) apps keep GNOME's own colours and take the orange accent;
recolouring them would mean overwriting each user's `~/.config/gtk-4.0/gtk.css`,
which GNOME doesn't support.

The edition is dark only, like the Plasma colour scheme: the Shell stylesheet
and the GTK 3 theme have no light variant. With GNOME's light style the Shell's
menus stay dark while libadwaita apps turn light.

Tested on Tumbleweed with GNOME 50, in the development VM (`tools/dev/vm/`).
