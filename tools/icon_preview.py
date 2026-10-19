#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Render the built icon theme at 64/48/32/22/16 px on the theme's dark view
colour and on cream, to build/icon-preview.png, for checking small sizes."""
import io
import sys

import resvg_py
from PIL import Image, ImageDraw

from common import BUILD, load_palette, rgb

SIZES = (64, 48, 32, 22, 16)


def render(path, size):
    png = resvg_py.svg_to_bytes(svg_path=str(path), width=size, height=size)
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def main():
    p = load_palette()
    theme = BUILD / "user/icons/openSUSE-halloween"
    files = sorted(theme.rglob("*.svg"))
    if not files:
        sys.exit("no icons built: run `make build` first")
    cols, w, h = 5, 210, 190
    sheet = Image.new("RGB", (cols * w + 10, -(-len(files) // cols) * h + 10), rgb(p["header"]))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        x, y = 10 + (i % cols) * w, 10 + (i // cols) * h
        draw.text((x, y), str(f.relative_to(theme)).removesuffix(".svg"), fill=rgb(p["cream"]))
        for row, bg in enumerate((p["view"], p["cream"])):
            tile = Image.new("RGBA", (w - 10, 80), rgb(bg) + (255,))
            tx = 4
            for s in SIZES:
                tile.alpha_composite(render(f, s), (tx, 8 + 64 - s))
                tx += s + 6
            sheet.paste(tile.convert("RGB"), (x, y + 14 + row * 84))
    out = BUILD / "icon-preview.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
