# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The Firefox theme: a static WebExtension theme in the palette's colours,
with a header band cut from the night wallpaper; unpacked and as an .xpi."""

import zipfile

from PIL import Image, ImageFilter

from common import FIREFOX, FIREFOX_ID, SHARED, VERSION, contrast, fill_tokens, rgb, write
from imaging import CROPS, save_png

DESKTOP = "shared"
ID = "openSUSE-halloween"
HEADER_H = 200       # Firefox's recommended header height
PAD = 150            # plain frame on the right, under the window buttons
DIM = 0.8            # the art's most opacity over the frame colour
TAB_STRIP_H = 44     # the top of the header that stays visible above the toolbar
TITLE_CONTRAST = 5.0


def header(p, night):
    """A band of the night master (art/crops.toml [firefox]) that fades into the
    frame colour: slowly to the left, where the tabs are, quickly to the right.
    Bright parts (the moon) are made more transparent, so tab titles drawn over
    them keep TITLE_CONTRAST against the frame showing through."""
    c = CROPS["firefox"]
    w = c["width"]
    h = round(night.height * w / night.width)
    top, art_w = round(c["top"] * h), round(c["right"] * w)
    art = night.resize((w, h), Image.LANCZOS).crop((0, top, art_w, top + HEADER_H))
    img = Image.new("RGBA", (art_w + PAD, HEADER_H), (0, 0, 0, 0))
    img.paste(art, (0, 0))

    # The most opacity each column can have behind the tab titles, spread out
    # over a tab's width
    frame = rgb(p["night"])
    band = img.convert("RGB").crop((0, 0, img.width, TAB_STRIP_H)).resize((img.width, 1), Image.BOX)

    def readable(x):
        col = band.getpixel((x, 0))
        def over_frame(a):
            return [f + (v - f) * a for f, v in zip(frame, col, strict=True)]
        steps = [a / 50 for a in range(51) if contrast(p["cream"], over_frame(a / 50)) >= TITLE_CONTRAST]
        return round(255 * min(DIM, max(steps, default=0)))
    limit = Image.new("L", (img.width, 1))
    limit.putdata([readable(x) for x in range(img.width)])
    limit = limit.filter(ImageFilter.MinFilter(121)).filter(ImageFilter.BoxBlur(60))

    fade_l, fade_r = round(art_w * 0.45), 60
    row = [round(limit.getpixel((x, 0)) * min(1, x / fade_l) ** 1.6 * min(1, max(0, (art_w - x) / fade_r)) ** 1.2)
           for x in range(img.width)]
    img.putalpha(Image.frombytes("L", img.size, bytes(row * img.height)))
    return img


def build(ctx):
    p = ctx.palette
    out = FIREFOX / ID
    name = "header.png"
    save_png(header(p, ctx.wallpapers["night"]), out / name)
    values = {**p, **{f"{k}_rgb": ", ".join(str(c) for c in rgb(v)) for k, v in p.items()},
              "VERSION": VERSION, "FIREFOX_ID": FIREFOX_ID, "HEADER": name}
    write(out / "manifest.json", fill_tokens((SHARED / "firefox/manifest.json.in").read_text(), values))
    # A fixed timestamp keeps the .xpi identical between builds
    with zipfile.ZipFile(FIREFOX / f"{ID}.xpi", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            z.writestr(zipfile.ZipInfo(f.name, (2026, 10, 1, 0, 0, 0)), f.read_bytes(), zipfile.ZIP_DEFLATED)
