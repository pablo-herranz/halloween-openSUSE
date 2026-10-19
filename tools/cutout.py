#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Turn a background-removed cut-out into a trimmed master for art/source/.

usage: cutout.py CUT OUT [--pad N]
       cutout.py CUT OUT --colour-from SRC [--pad N]

CUT is the transparent PNG from picsart_remove_bg. The second form keeps
CUT's alpha but takes the colours from SRC, an edit of the same picture
with the same outline (the unlit lantern), so both masters line up exactly.
"""
import argparse

from PIL import Image

NOISE = 16  # alpha at or below this is stray speckle from the matting


def despill(img):
    """Pull the magenta backdrop's tint out of the soft edge pixels."""
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if 0 < a < 255:
                spill = min(r, b) - g
                if spill > 0:
                    px[x, y] = (r - spill // 2, g, b - spill, a)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cut")
    ap.add_argument("out")
    ap.add_argument("--colour-from", metavar="SRC")
    ap.add_argument("--pad", type=int, default=16)
    args = ap.parse_args()

    cut = Image.open(args.cut).convert("RGBA")
    alpha = cut.getchannel("A").point(lambda v: 0 if v <= NOISE else v)
    if args.colour_from:
        img = Image.open(args.colour_from).convert("RGBA")
        if img.size != cut.size:
            raise SystemExit(f"{args.colour_from} is {img.size}, {args.cut} is {cut.size}")
    else:
        img = cut
    img.putalpha(alpha)
    despill(img)

    x0, y0, x1, y1 = alpha.getbbox()
    box = (max(x0 - args.pad, 0), max(y0 - args.pad, 0),
           min(x1 + args.pad, img.width), min(y1 + args.pad, img.height))
    img.crop(box).save(args.out, optimize=True)
    print(f"{args.out}: {box[2] - box[0]}x{box[3] - box[1]} from {img.width}x{img.height}")


if __name__ == "__main__":
    main()
