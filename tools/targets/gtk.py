# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The GTK 3 theme GNOME and Xfce share: adw-gtk3-dark (pinned in
tools/upstream.toml) with its named colours set from the palette. The theme
folder also takes the GNOME Shell and Xfce pieces (targets/gnome.py, xfce.py)."""

import shutil

from common import SHARED, USER, fill_tokens, upstream_archive, write

DESKTOP = ("gnome", "xfce", "sway")
ID = "openSUSE-halloween"
THEME = USER / "themes" / ID
FOCUS = "alpha(@accent_color,0.5)"


def build(ctx):
    src = upstream_archive("adw-gtk3") / "adw-gtk3-dark/gtk-3.0"
    out = THEME / "gtk-3.0"
    shutil.copytree(src / "assets", out / "assets")
    ours = fill_tokens((SHARED / "gtk/halloween.css.in").read_text(), ctx.palette)
    for name in ("gtk.css", "gtk-dark.css"):
        # Focus rings and focused entries at half-transparent pumpkin are
        # below 3:1 against the night background; draw them solid
        upstream = (src / name).read_text().replace(FOCUS, "@accent_color")
        write(out / name, upstream.rstrip("\n") + "\n\n" + ours)
    for name in ("index.theme", "README"):
        shutil.copyfile(SHARED / "gtk" / name, THEME / name)
