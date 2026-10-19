#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Render the built icon theme for review: each distinct icon once (with how
many names share it) at 64/48/32/22/16 px on the theme's dark view colour,
on cream and on the ember selection, to build/icon-preview.png. See
CONTRIBUTING.md, "Design review"."""
import hashlib
import io
import sys
from collections import defaultdict

import resvg_py
from PIL import Image, ImageDraw

from common import BUILD, load_palette, rgb

SIZES = (64, 48, 32, 22, 16)
BACKGROUNDS = ("view", "cream", "ember")


def render(path, size):
    png = resvg_py.svg_to_bytes(svg_path=str(path), width=size, height=size)
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def main():
    p = load_palette()
    theme = BUILD / "user/icons/openSUSE-halloween"
    names = defaultdict(list)
    for f in sorted(theme.rglob("*.svg")):
        if not f.is_symlink():
            names[hashlib.sha256(f.read_bytes()).hexdigest()].append(f)
    if not names:
        sys.exit("no icons built: run `make build` first")
    icons = sorted(names.values(), key=lambda fs: str(fs[0].relative_to(theme)))
    cols, w, h = 5, 210, 14 + 84 * len(BACKGROUNDS) + 8
    sheet = Image.new("RGB", (cols * w + 10, -(-len(icons) // cols) * h + 10), rgb(p["header"]))
    draw = ImageDraw.Draw(sheet)
    for i, files in enumerate(icons):
        x, y = 10 + (i % cols) * w, 10 + (i // cols) * h
        label = str(files[0].relative_to(theme)).removesuffix(".svg")
        draw.text((x, y), label + (f" (+{len(files) - 1})" if len(files) > 1 else ""), fill=rgb(p["cream"]))
        for row, bg in enumerate(BACKGROUNDS):
            tile = Image.new("RGBA", (w - 10, 80), rgb(p[bg]) + (255,))
            tx = 4
            for s in SIZES:
                tile.alpha_composite(render(files[0], s), (tx, 8 + 64 - s))
                tx += s + 6
            sheet.paste(tile.convert("RGB"), (x, y + 14 + row * 84))
    out = BUILD / "icon-preview.png"
    sheet.save(out)
    print(out, f"{len(icons)} distinct icons")


if __name__ == "__main__":
    main()
