# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The Firefox theme: a static WebExtension theme in the palette's colours,
with a header band cut from the night wallpaper; unpacked and as an .xpi."""

import base64
import io
import zipfile

from PIL import Image, ImageFilter

from common import FIREFOX, FIREFOX_ID, SHARED, VERSION, contrast, fill_tokens, rgb, write
from imaging import CROPS

DESKTOP = "shared"
ID = "openSUSE-halloween"
HEADER_H = 200       # Firefox's recommended header height
PAD = 150            # plain frame on the right, under the window buttons
DIM = 0.8            # the art's most opacity over the frame colour
TAB_STRIP_H = 44     # the top of the header that stays visible above the toolbar
TITLE_CONTRAST = 5.0
SCALE = 2            # the header's picture is drawn at 2x, so it stays sharp on HiDPI screens


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


def header_svg(p, night):
    """The header as SVG at its 1x size: the picture drawn again at SCALE x as a
    JPEG, with header()'s per-column fade as a mask. Firefox draws theme images
    at their own size in CSS pixels, so a PNG would be blurry on HiDPI screens;
    an SVG is drawn at the screen's resolution."""
    one = header(p, night)
    c = CROPS["firefox"]
    w = c["width"] * SCALE
    h = round(night.height * w / night.width)
    top, art_w = round(c["top"] * h), round(c["right"] * w)
    art = night.resize((w, h), Image.LANCZOS).crop((0, top, art_w, top + HEADER_H * SCALE))
    picture = Image.new("RGB", (one.width * SCALE, HEADER_H * SCALE), rgb(p["night"]))
    picture.paste(art, (0, 0))
    buf = io.BytesIO()
    picture.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    data = base64.b64encode(buf.getvalue()).decode()

    alpha = one.getchannel("A")
    xs = sorted({*range(0, one.width, 4), one.width - 1})
    stops = "".join(f'<stop offset="{x / (one.width - 1):.4f}" stop-color="#{a:02x}{a:02x}{a:02x}"/>'
                    for x in xs for a in [alpha.getpixel((x, 0))])
    W, H = one.size
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs><linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>'
            f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>'
            f'<image width="{W}" height="{H}" preserveAspectRatio="none" mask="url(#m)" '
            f'href="data:image/jpeg;base64,{data}"/></svg>\n')


def build(ctx):
    p = ctx.palette
    out = FIREFOX / ID
    name = "header.svg"
    write(out / name, header_svg(p, ctx.wallpapers["night"]))
    values = {**p, **{f"{k}_rgb": ", ".join(str(c) for c in rgb(v)) for k, v in p.items()},
              "VERSION": VERSION, "FIREFOX_ID": FIREFOX_ID, "HEADER": name}
    write(out / "manifest.json", fill_tokens((SHARED / "firefox/manifest.json.in").read_text(), values))
    # A fixed timestamp keeps the .xpi identical between builds
    with zipfile.ZipFile(FIREFOX / f"{ID}.xpi", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            z.writestr(zipfile.ZipInfo(f.name, (2026, 10, 1, 0, 0, 0)), f.read_bytes(), zipfile.ZIP_DEFLATED)
