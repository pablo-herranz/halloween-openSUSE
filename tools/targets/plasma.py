# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""KDE Plasma: the colour scheme, the Plasma style and the look-and-feel
package with its splash screen."""

import shutil

from PIL import Image, ImageEnhance, ImageFilter

import placeholders as ph
import plasma_style
import vectors
from common import ROOT, USER, fill_tokens, rgb, write
from imaging import CROPS, crop_ratio, crop_to, fit, save_jpeg, save_png

DESKTOP = "plasma"
SCHEME = "openSUSEHalloween"
STYLE = "openSUSE-halloween"
LNF_ID = "org.openSUSE.halloween.desktop"


def render_colors(p):
    tpl = (ROOT / f"plasma/color-schemes/{SCHEME}.colors.in").read_text()
    return fill_tokens(tpl, p, fmt=lambda h: ",".join(str(c) for c in rgb(h)))


def splash_backdrop(night):
    """The part of the night master that leaves the chameleon out (art/crops.toml [splash])."""
    x0, y0, x1, y1 = CROPS["splash"]["box"]
    region = night.crop((round(x0 * night.width), round(y0 * night.height),
                         round(x1 * night.width), round(y1 * night.height)))
    return crop_ratio(region, 16 / 9)


def panel_mock(img, p):
    """Draw a translucent panel strip so previews read as a desktop."""
    out = img.convert("RGBA")
    h = max(8, round(out.height * 0.045))
    strip = Image.new("RGBA", (out.width, h), rgb(p["night"]) + (215,))
    out.alpha_composite(strip, (0, out.height - h))
    return out.convert("RGB")


def splash_mock(p, background, hero, lit, size=(1920, 1080)):
    img = crop_ratio(background, size[0] / size[1]).resize(size, Image.LANCZOS).convert("RGBA")
    unit = size[1] / 60
    hs = round(unit * 14)
    hx, hy = (size[0] - hs) // 2, round(size[1] / 2 - unit * 2 - hs / 2)
    img.alpha_composite(hero.resize((hs, hs), Image.LANCZOS), (hx, hy))
    ps = round(unit * 3)
    total = 5 * ps + 4 * round(unit)
    x = (size[0] - total) // 2
    for _ in range(5):
        img.alpha_composite(lit.resize((ps, ps), Image.LANCZOS), (x, hy + hs + round(unit * 2)))
        x += ps + round(unit)
    return img.convert("RGB")


def build_look_and_feel(ctx):
    p, wallpapers = ctx.palette, ctx.wallpapers
    lit, unlit = ctx.lanterns
    out = USER / "plasma/look-and-feel" / LNF_ID
    shutil.copytree(ROOT / "plasma/look-and-feel" / LNF_ID, out)
    splash = out / "contents/splash"
    night = splash_backdrop(wallpapers["night"]).resize((1920, 1080), Image.LANCZOS)
    bg = ImageEnhance.Brightness(night.filter(ImageFilter.GaussianBlur(8))).enhance(0.55)
    save_jpeg(bg, splash / "images/background.jpg")
    save_png(fit(ctx.hero, 512), splash / "images/hero.png")
    save_png(fit(lit, 192), splash / "images/pumpkin-lit.png")
    save_png(fit(unlit, 192), splash / "images/pumpkin-unlit.png")
    save_png(ph.glow(p, 256), splash / "images/glow.png")
    write(splash / "palette.js", ".pragma library\n// Generated from art/palette.toml by tools/build.py\n"
          + "".join(f'var {k} = "{p[k]}";\n' for k in ("night", "cream", "pumpkin", "candle")))

    previews = out / "contents/previews"
    previews.mkdir(parents=True, exist_ok=True)
    shots = ROOT / "art/previews"
    made = {
        "preview.png": lambda: panel_mock(crop_to(wallpapers, "dusk", 16 / 9), p).resize((600, 337), Image.LANCZOS),
        "fullscreenpreview.jpg": lambda: panel_mock(crop_to(wallpapers, "dusk", 16 / 9), p).resize((1920, 1080), Image.LANCZOS),
        "lockscreen.png": lambda: ImageEnhance.Brightness(crop_to(wallpapers, "night", 16 / 9)).enhance(0.8).resize((600, 337), Image.LANCZOS),
        "splash.png": lambda: splash_mock(p, bg, fit(ctx.hero, 512), fit(lit, 192)).resize((300, 169), Image.LANCZOS),
    }
    for name, make in made.items():
        if (shots / name).exists():
            shutil.copy2(shots / name, previews / name)
        else:
            img = make()
            (save_jpeg if name.endswith(".jpg") else save_png)(img, previews / name)


def build(ctx):
    p = ctx.palette
    colors = render_colors(p)
    write(USER / f"color-schemes/{SCHEME}.colors", colors)
    plasma_style.build(USER / "plasma/desktoptheme" / STYLE, p, colors)
    ctx.placeholders.extend(f"ornament {n}" for n in plasma_style.ORNAMENTS if vectors.ornament(n, p) is None)
    build_look_and_feel(ctx)
