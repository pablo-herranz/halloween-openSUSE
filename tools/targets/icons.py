# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The freedesktop icon theme: index.theme from shared/icons plus the SVGs
tools/vectors.py composes from the masters; drawn placeholders fill gaps."""

import shutil

import placeholders as ph
import vectors
from common import SHARED, USER, write

DESKTOP = "shared"
ID = "openSUSE-halloween"


def build(ctx):
    out = USER / "icons" / ID
    shutil.copytree(SHARED / "icons" / ID, out)
    for rel, svg in vectors.icons(ctx.palette).items():
        write(out / rel, svg)
    for rel, svg in ph.icon_svgs(ctx.palette).items():
        if not (out / rel).exists():
            write(out / rel, svg)
            ctx.placeholders.append(f"icon {rel}")
