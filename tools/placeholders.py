# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Simple drawn stand-ins for the AI artwork, used until the masters exist.

They only need to be recognisable and to have the right sizes and alpha, so
the whole build, install and test pipeline can run before any art is made.
"""

import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from common import rgb


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def vertical_gradient(size, stops):
    """stops: [(position 0..1, (r, g, b)), ...] top to bottom."""
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                draw.line([(0, y), (w, y)], fill=mix(c0, c1, (t - p0) / (p1 - p0)))
                break
    return img


def dither(img, sigma=2.0):
    """Add faint noise so smooth skies don't band after JPEG compression."""
    noise = Image.effect_noise(img.size, sigma).convert("RGB")
    return ImageChops.add(img, noise, 1.0, -128)


def hills(draw, w, h, base, amp, waves, phase, color):
    pts = [(0, h)]
    for x in range(0, w + 1, max(1, w // 400)):
        y = base + amp * math.sin(x / w * waves * math.tau + phase) \
            + amp * 0.35 * math.sin(x / w * waves * 2.7 * math.tau + phase * 1.7)
        pts.append((x, y))
    pts.append((w, h))
    draw.polygon(pts, fill=color)


def wallpaper(p, variant, size=(3840, 2160)):
    w, h = size
    if variant == "dusk":
        sky = [(0, rgb("#3B2A4F")), (0.45, rgb("#8A3A2E")), (0.72, rgb(p["pumpkin"])), (1, rgb(p["ember"]))]
        moon, halo, far, near = rgb(p["candle"]), rgb(p["apricot"]), rgb("#3A2236"), rgb(p["night"])
    else:
        sky = [(0, rgb(p["sky_top"])), (0.6, rgb("#241830")), (1, rgb(p["sky_bottom"]))]
        moon, halo, far, near = rgb(p["cream"]), rgb(p["plum"]), rgb("#1E1526"), rgb("#0B080E")
    img = vertical_gradient(size, sky)

    glow = Image.new("L", size, 0)
    mx, my, r = int(w * 0.72), int(h * 0.3), int(h * 0.09)
    ImageDraw.Draw(glow).ellipse([mx - r * 2.2, my - r * 2.2, mx + r * 2.2, my + r * 2.2], fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.05))
    img = Image.composite(Image.new("RGB", size, halo), img, glow)
    draw = ImageDraw.Draw(img)
    draw.ellipse([mx - r, my - r, mx + r, my + r], fill=moon)

    hills(draw, w, h, h * 0.70, h * 0.035, 1.3, 0.4, far)
    hills(draw, w, h, h * 0.80, h * 0.025, 2.1, 1.9, near)
    for i, (fx, fy, fr) in enumerate([(0.64, 0.80, 0.030), (0.70, 0.815, 0.022), (0.75, 0.805, 0.026)]):
        pr = h * fr
        pumpkin_at(draw, w * fx, h * fy - pr * 0.6, pr, p, lit=(variant == "night" or i == 1))
    return dither(img)


def pumpkin_at(draw, cx, cy, r, p, lit=True):
    body = [rgb(p["ember"]), mix(rgb(p["ember"]), rgb(p["pumpkin"]), 0.5), rgb(p["pumpkin"])]
    if not lit:
        body = [mix(c, rgb(p["night"]), 0.55) for c in body]
    draw.polygon([(cx - r * 0.12, cy - r * 0.95), (cx + r * 0.05, cy - r * 1.25),
                  (cx + r * 0.2, cy - r * 1.2), (cx + r * 0.12, cy - r * 0.9)], fill=rgb(p["moss"]))
    for dx, rx, c in ((-0.5, 0.55, body[0]), (0.5, 0.55, body[0]), (-0.25, 0.55, body[1]),
                      (0.25, 0.55, body[1]), (0, 0.5, body[2])):
        draw.ellipse([cx + (dx - rx) * r, cy - r * 0.95, cx + (dx + rx) * r, cy + r * 0.95], fill=c)
    face = rgb(p["candle"]) if lit else mix(rgb(p["night"]), rgb(p["ember"]), 0.25)
    for sx in (-1, 1):
        draw.polygon([(cx + sx * r * 0.42, cy - r * 0.05), (cx + sx * r * 0.12, cy - r * 0.05),
                      (cx + sx * r * 0.27, cy - r * 0.38)], fill=face)
    mouth = [(cx - r * 0.5, cy + r * 0.25)]
    for i in range(1, 8):
        mouth.append((cx - r * 0.5 + i * r / 7, cy + r * (0.25 if i % 2 else 0.4)))
    mouth += [(cx + r * 0.4, cy + r * 0.45), (cx, cy + r * 0.62), (cx - r * 0.4, cy + r * 0.45)]
    draw.polygon(mouth, fill=face)


def pumpkin(p, size, lit=True):
    img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    pumpkin_at(ImageDraw.Draw(img), size * 2, size * 2.25, size * 1.6, p, lit)
    return img.resize((size, size), Image.LANCZOS)


def glow(p, size=256, strength=1.0):
    alpha = Image.radial_gradient("L").resize((size, size), Image.LANCZOS)
    alpha = alpha.point(lambda v: int(max(0, 255 - v * 1.6) * 0.75 * strength))
    img = Image.new("RGBA", (size, size), rgb(p["candle"]) + (0,))
    img.putalpha(alpha)
    return img


def hero(p, size=512):
    """A green chameleon in a witch hat with a lantern: clearly a stand-in."""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    g, dark = rgb(p["chameleon"]), mix(rgb(p["chameleon"]), (0, 0, 0), 0.35)
    k = s / 512
    d.arc([70 * k, 250 * k, 250 * k, 430 * k], 90, 420, fill=dark, width=int(26 * k))
    d.ellipse([150 * k, 220 * k, 380 * k, 440 * k], fill=g)
    d.ellipse([280 * k, 160 * k, 450 * k, 300 * k], fill=g)
    d.ellipse([360 * k, 185 * k, 420 * k, 245 * k], fill=rgb(p["cream"]))
    d.ellipse([382 * k, 202 * k, 410 * k, 230 * k], fill=rgb(p["night"]))
    d.polygon([(300 * k, 205 * k), (440 * k, 205 * k), (330 * k, 40 * k)], fill=rgb(p["plum"]))
    d.ellipse([270 * k, 190 * k, 470 * k, 225 * k], fill=mix(rgb(p["plum"]), (0, 0, 0), 0.3))
    d.rounded_rectangle([250 * k, 270 * k, 370 * k, 305 * k], radius=14 * k, fill=rgb(p["ember"]))
    img = img.resize((size, size), Image.LANCZOS)
    lantern = pumpkin(p, int(size * 0.32), lit=True)
    img.alpha_composite(lantern, (int(size * 0.08), int(size * 0.6)))
    return img


# --- icons -------------------------------------------------------------------

EMBLEMS = {
    "folder-documents": "cream", "folder-download": "olive", "folder-music": "plum",
    "folder-pictures": "candle", "folder-videos": "cranberry", "folder-templates": "apricot",
    "folder-publicshare": "moss",
}


def _svg(body, size=64):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}">\n  <!-- placeholder -->\n{body}</svg>\n')


def folder_svg(p, emblem=None, open_=False):
    body = (f'  <path d="M6 12 h18 l6 6 h28 v36 h-52 z" fill="{p["plum"]}"/>\n')
    if open_:
        body += f'  <path d="M2 26 h56 l-6 30 h-48 z" fill="{p["pumpkin"]}"/>\n'
    else:
        body += f'  <rect x="6" y="22" width="52" height="34" rx="3" fill="{p["pumpkin"]}"/>\n'
    if emblem:
        body += f'  <circle cx="32" cy="40" r="9" fill="{p[emblem]}"/>\n'
    return _svg(body)


def icon_svgs(p):
    icons = {}
    for name in ("folder", "folder-open"):
        icons[f"scalable/places/{name}.svg"] = folder_svg(p, open_=name.endswith("open"))
    for name, emblem in EMBLEMS.items():
        icons[f"scalable/places/{name}.svg"] = folder_svg(p, emblem)
    icons["scalable/places/user-home.svg"] = _svg(
        f'  <path d="M32 6 L60 30 h-8 v26 h-40 v-26 h-8 z" fill="{p["pumpkin"]}"/>\n'
        f'  <rect x="27" y="38" width="10" height="18" fill="{p["night"]}"/>\n'
        f'  <rect x="40" y="32" width="8" height="8" fill="{p["candle"]}"/>\n')
    icons["scalable/places/user-desktop.svg"] = _svg(
        f'  <rect x="4" y="8" width="56" height="38" rx="3" fill="{p["plum"]}"/>\n'
        f'  <rect x="8" y="12" width="48" height="30" fill="{p["night"]}"/>\n'
        f'  <rect x="22" y="48" width="20" height="6" fill="{p["plum"]}"/>\n')
    cauldron = (f'  <ellipse cx="32" cy="38" rx="24" ry="20" fill="{p["plum"]}"/>\n'
                f'  <ellipse cx="32" cy="22" rx="26" ry="6" fill="{p["moss"]}"/>\n')
    icons["scalable/places/user-trash.svg"] = _svg(cauldron)
    icons["scalable/places/user-trash-full.svg"] = _svg(
        cauldron + "".join(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{p["olive"]}"/>\n'
                           for x, y, r in ((24, 16, 4), (34, 12, 5), (42, 17, 3))))
    launcher = _svg(f'  <circle cx="32" cy="36" r="22" fill="{p["chameleon"]}"/>\n'
                    f'  <path d="M14 22 h36 l-18 -18 z" fill="{p["plum"]}"/>\n')
    for name in ("start-here-kde-plasma", "start-here-kde", "start-here"):
        icons[f"scalable/apps/{name}.svg"] = launcher
    small = {
        "folder": f'  <rect x="1" y="2" width="6" height="3" fill="{p["plum"]}"/>\n'
                  f'  <rect x="1" y="4" width="14" height="10" rx="1" fill="{p["pumpkin"]}"/>\n',
        "user-home": f'  <path d="M8 1 L15 8 h-2 v7 h-10 v-7 h-2 z" fill="{p["pumpkin"]}"/>\n',
        "user-trash": f'  <ellipse cx="8" cy="10" rx="6" ry="5" fill="{p["plum"]}"/>\n'
                      f'  <rect x="1" y="4" width="14" height="2" rx="1" fill="{p["moss"]}"/>\n',
    }
    for name, body in small.items():
        icons[f"16x16/places/{name}.svg"] = _svg(body, 16)
    return icons
