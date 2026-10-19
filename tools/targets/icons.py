# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The freedesktop icon theme: index.theme from shared/icons plus the SVGs
tools/vectors.py composes from the masters; drawn placeholders fill gaps.

openSUSE-halloween falls back to Breeze Dark, for Plasma. Plasma would show
our icons for Breeze names that only extend ours (tools/kde_lookup.py), so
the theme's kde/ folder links those to Breeze's own. GNOME and Xfce get
openSUSE-halloween-adwaita, which falls back to Adwaita instead: only its
index.theme differs (it leaves kde/ out), and its folders link to
openSUSE-halloween's."""

import os
import shutil

import kde_lookup
import placeholders as ph
import vectors
from common import SHARED, USER, write

DESKTOP = "shared"
ID = "openSUSE-halloween"
ADWAITA_ID = "openSUSE-halloween-adwaita"


def build(ctx):
    out = USER / "icons" / ID
    shutil.copytree(SHARED / "icons" / ID, out)
    for rel, svg in vectors.icons(ctx.palette).items():
        write(out / rel, svg)
    for rel, svg in ph.icon_svgs(ctx.palette).items():
        if not (out / rel).exists():
            write(out / rel, svg)
            ctx.placeholders.append(f"icon {rel}")
    breeze_links(out)
    adwaita_variant(out)


def breeze_links(out):
    """kde/<name> links to Breeze Dark's icon for each Breeze name Plasma
    would otherwise take from us (kde_lookup.plan)."""
    files = [f for f in out.rglob("*") if f.suffix in (".svg", ".png")]
    ours = {f.stem for f in files}
    one_colour = {f.stem for f in files if f.suffix == ".svg" and "ColorScheme-Text" in f.read_text()}
    (out / "kde").mkdir()
    for name, path in sorted(kde_lookup.plan(ours, one_colour).items()):
        os.symlink(f"../../breeze-dark/{path}", out / "kde" / (name + path[path.rfind("."):]))


def adwaita_variant(out):
    dest = out.parent / ADWAITA_ID
    lines = []
    for line in (out / "index.theme").read_text().splitlines():
        if line.startswith("Name="):
            line = "Name=openSUSE Halloween for GNOME and Xfce"
        elif line.startswith("Comment="):
            line = line.replace("over Breeze Dark", "over Adwaita")
        elif line.startswith("Inherits="):
            line = "Inherits=adwaita-xfce,Adwaita,AdwaitaLegacy,hicolor"
        elif line.startswith("FollowsColorScheme="):
            continue
        elif line.startswith("Directories="):
            line = line.replace(",kde", "")
        lines.append(line)
    write(dest / "index.theme", "\n".join(lines) + "\n")
    for child in sorted(out.iterdir()):
        if child.is_dir() and child.name != "kde":
            os.symlink(f"../{ID}/{child.name}", dest / child.name)
