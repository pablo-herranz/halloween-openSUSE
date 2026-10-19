# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The freedesktop icon theme: index.theme from shared/icons plus the SVGs
tools/vectors.py composes from the masters; drawn placeholders fill gaps.

openSUSE-halloween falls back to Breeze Dark, for Plasma. GNOME and Xfce get
openSUSE-halloween-adwaita, which falls back to Adwaita instead: only its
index.theme differs, and its folders link to openSUSE-halloween's."""

import os
import shutil

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
    adwaita_variant(out)


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
        lines.append(line)
    write(dest / "index.theme", "\n".join(lines) + "\n")
    for child in sorted(out.iterdir()):
        if child.is_dir():
            os.symlink(f"../{ID}/{child.name}", dest / child.name)
