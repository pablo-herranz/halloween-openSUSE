# Xfce edition

What Xfce gets, next to the shared wallpapers, Plymouth boot splash and
Firefox theme:

| Piece | Installed as | Built by |
|---|---|---|
| GTK 3 theme, also styling the panel | `/usr/share/themes/openSUSE-halloween/gtk-3.0/` | `tools/targets/gtk.py` from [`shared/gtk/`](../shared/gtk/) |
| Window manager theme: xfwm4's default theme with the palette's colours, at 1×, 1.5× and 2× | `/usr/share/themes/openSUSE-halloween{,-hdpi,-xhdpi}/xfwm4/` | `tools/targets/xfce.py` from [`xfwm4/`](xfwm4/) |
| Notification theme | `/usr/share/themes/openSUSE-halloween/xfce-notify-4.0/` | `tools/targets/xfce.py` from [`xfce-notify-4.0/`](xfce-notify-4.0/) |
| Icons over Adwaita | `/usr/share/icons/openSUSE-halloween-adwaita/` | `tools/targets/icons.py` |

There are no defaults to install: Xfce's defaults and the LightDM greeter's
configuration belong to openSUSE's branding packages, and a theme package
can't replace them without file conflicts. Users pick the pieces in
*Appearance*, *Window Manager*, *Notifications* and *Desktop*; the
[README](../README.md#install) has the steps, including the LightDM settings
an administrator can change.

The window manager theme reuses xfwm4's own default theme (GPL-2.0-or-later),
pinned in `tools/upstream.toml`: `xfwm4/colors.in` sets the colours its images
are drawn with.

Tested on Tumbleweed with Xfce 4.20, in the development VM (`tools/dev/vm/`).
