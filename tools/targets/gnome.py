# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""GNOME: the Shell stylesheet (in the shared theme folder, for the User Themes
extension), the wallpaper entry for Settings, and the optional defaults: a
gsettings override and GDM's dconf database."""

from xml.sax.saxutils import escape

from common import DEFAULTS, ROOT, USER, fill_tokens, write
from targets.gtk import THEME

DESKTOP = "gnome"
WALLPAPERS = "/usr/share/wallpapers/openSUSEhalloween/contents"
LIGHT = f"{WALLPAPERS}/images/3840x2160.jpg"
DARK = f"{WALLPAPERS}/images_dark/3840x2160.jpg"


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
    write(DEFAULTS / "dconf/profile/gdm", (src / "defaults/gdm-profile").read_text())
    write(DEFAULTS / "dconf/db/gdm.d/30-openSUSE-halloween",
          fill_tokens((src / "defaults/30-openSUSE-halloween.in").read_text(), tokens))
