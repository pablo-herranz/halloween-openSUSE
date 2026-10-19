# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""GNOME: the Shell stylesheet (in the shared theme folder, for the User Themes
extension), the wallpaper entry for Settings, and the optional defaults: a
GSettings override, which also covers the login screen (GDM)."""

from xml.sax.saxutils import escape

from common import DEFAULTS, ROOT, USER, fill_tokens, write
from targets.gtk import THEME

DESKTOP = "gnome"
# GNOME zooms one picture to fill every screen: the zoomed pictures from
# targets/wallpapers.py (see check_resolutions in tools/check.py)
BACKGROUNDS = "/usr/share/backgrounds/openSUSEhalloween"
LIGHT = f"{BACKGROUNDS}/dusk.jpg"
DARK = f"{BACKGROUNDS}/night.jpg"


def background_xml(p):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>
  <wallpaper deleted="false">
    <name>{escape("openSUSE Halloween")}</name>
    <filename>{LIGHT}</filename>
    <filename-dark>{DARK}</filename-dark>
    <options>zoom</options>
    <shade_type>solid</shade_type>
    <pcolor>{p["night"]}</pcolor>
    <scolor>{p["night"]}</scolor>
  </wallpaper>
</wallpapers>
"""


def build(ctx):
    src = ROOT / "gnome"
    tokens = {**ctx.palette, "LIGHT": LIGHT, "DARK": DARK}
    shell = fill_tokens((src / "gnome-shell/gnome-shell.css.in").read_text(), tokens)
    write(THEME / "gnome-shell/gnome-shell.css", shell)
    write(USER / "gnome-background-properties/openSUSEhalloween.xml", background_xml(ctx.palette))

    override = "30_openSUSE-halloween.gschema.override"
    write(DEFAULTS / "glib-2.0/schemas" / override,
          fill_tokens((src / "defaults" / f"{override}.in").read_text(), tokens))
