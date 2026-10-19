# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The Plymouth boot splash (two-step plugin): the chameleon as watermark and
a flickering lantern as throbber, on a gradient from the palette."""

import math

from PIL import Image

import placeholders as ph
from common import SHARED, SYSTEM, fill_tokens, write
from imaging import fit, save_png

DESKTOP = "shared"
ID = "openSUSE-halloween"
INSTALL_DIR = f"/usr/share/plymouth/themes/{ID}"


def build(ctx):
    p = ctx.palette
    src = SHARED / "plymouth" / ID
    out = SYSTEM / "plymouth" / ID
    hexes = {k: "0x" + v.lstrip("#").lower() for k, v in p.items()}
    write(out / f"{ID}.plymouth",
          fill_tokens((src / f"{ID}.plymouth.in").read_text(), {**hexes, "IMAGEDIR": INSTALL_DIR}))
    save_png(fit(ctx.hero, 300), out / "watermark.png")
    lit, unlit = ctx.lanterns
    size, frames = 64, 40
    small_lit, small_unlit = fit(lit, 48), fit(unlit, 48)
    for i in range(frames):
        t = i / frames * math.tau
        f = 0.72 + 0.28 * (0.5 + 0.5 * math.sin(2 * t + 0.7 * math.sin(3 * t)))
        frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        frame.alpha_composite(ph.glow(p, size, f))
        frame.alpha_composite(small_unlit, (8, 8))
        lit_f = small_lit.copy()
        lit_f.putalpha(lit_f.getchannel("A").point(lambda a: int(a * f)))
        frame.alpha_composite(lit_f, (8, 8))
        for prefix in ("throbber", "animation"):
            save_png(frame, out / f"{prefix}-{i + 1:04d}.png")
