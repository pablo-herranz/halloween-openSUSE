#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the openSUSE-halloween Plasma style from pinned Breeze sources.

Breeze's frame SVGs take their colours from the style's `colors` file, so most
of the autumn look comes for free. On top of that this script:
  - adds a leaf sprig `overlay` to popups (dialogs/background) and a vine
    garland tiled along the panel's top edge (widgets/panel-background),
  - tints the tooltip shadow ember so tooltips glow warmly,
  - swaps the analog clock face for a carved pumpkin with dark hands.
It does this for all four Breeze variants (plain, translucent, opaque, solid)
so Plasma never falls back to an unthemed Breeze frame.
"""

import argparse
import re
import shutil
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from common import CACHE, ROOT, fetch, write

SVG_NS = "http://www.w3.org/2000/svg"
SRC = ROOT / "plasma/desktoptheme/openSUSE-halloween"
VARIANTS = ("", "translucent/", "opaque/", "solid/")

# Ornament placement: (ornament file, target height in px, opacity, hint elements)
OVERLAYS = {
    "dialogs/background.svg": ("popup-sprig.svg", 56, 0.55, ["hint-overlay-pos-right"]),
    "widgets/panel-background.svg": ("panel-garland.svg", 8, 0.7, ["hint-overlay-tile-horizontal"]),
}
TOOLTIP_SHADOW = ("widgets/tooltip.svg", "ember", 1.8)


def upstream(name):
    pins = tomllib.loads((ROOT / "tools/upstream.toml").read_text())
    return fetch(f"{pins['base']}/{name}", pins["files"][name],
                 CACHE / "libplasma-breeze" / name).read_text()


def ornament(name, prefix):
    """Return (inner SVG markup with prefixed ids, width, height) of an ornament."""
    root = ET.parse(SRC / "ornaments" / name).getroot()
    _, _, w, h = (float(v) for v in root.get("viewBox").split())
    ET.register_namespace("", SVG_NS)
    parts = []
    for child in root:
        if child.tag is ET.Comment:
            continue
        for el in child.iter():
            if el.get("id"):
                el.set("id", prefix + el.get("id"))
        parts.append(ET.tostring(child, encoding="unicode"))
    markup = "".join(parts)
    markup = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", markup)
    markup = re.sub(r"url\(#", f"url(#{prefix}", markup)
    markup = re.sub(r'href="#', f'href="#{prefix}', markup)
    return markup, w, h


def widen_canvas(svg, extra_w, min_h):
    """Grow the root <svg> canvas so new elements sit beside Breeze's ones."""
    head = re.search(r"<svg\b[^>]*>", svg)
    tag = head.group(0)
    w = float(re.search(r'\swidth="([\d.]+)"', tag).group(1))
    h = float(re.search(r'\sheight="([\d.]+)"', tag).group(1))
    new_w, new_h = w + extra_w, max(h, min_h)
    new = re.sub(r'(\swidth=")[\d.]+"', rf'\g<1>{new_w:g}"', tag)
    new = re.sub(r'(\sheight=")[\d.]+"', rf'\g<1>{new_h:g}"', new)
    new = re.sub(r'(\sviewBox=")[^"]*"', rf'\g<1>0 0 {new_w:g} {new_h:g}"', new)
    return svg.replace(tag, new, 1), w


def append(svg, markup):
    i = svg.rindex("</svg>")
    return svg[:i] + markup + "\n" + svg[i:]


def add_overlay(svg, name, height, opacity, hints):
    frag, w, h = ornament(name, "halloween-" + Path(name).stem + "-")
    scale = height / h
    width = w * scale
    svg, x0 = widen_canvas(svg, width + 12, height + 4)
    x = x0 + 4
    markup = (f'  <g id="overlay" transform="translate({x:g} 0) scale({scale:g})" '
              f'opacity="{opacity:g}">{frag}</g>\n')
    for i, hint in enumerate(hints):
        markup += (f'  <rect id="{hint}" x="{x + width + 2 + i * 3:g}" y="0" width="2" height="2" '
                   f'style="fill:#00ff00;fill-opacity:0.01"/>\n')
    return append(svg, markup)


def tint_shadow(svg, color, factor):
    svg = re.sub(r"stop-color:#000(000)?\b", f"stop-color:{color}", svg)

    def boost(m):
        return f"stop-opacity:{min(1.0, float(m.group(1)) * factor):.3g}"
    return re.sub(r"stop-opacity:([\d.]+)", boost, svg)


def set_class(svg, element_id, new_class):
    def fix(m):
        tag = m.group(0)
        return re.sub(r'class="[^"]*"', f'class="{new_class}"', tag)
    out, n = re.subn(rf'<g\b[^>]*\bid="{element_id}"[^>]*>', fix, svg, count=1)
    if n != 1:
        raise RuntimeError(f"clock.svg: no <g id={element_id}>")
    return out


def pumpkin_clock(svg):
    svg = svg.replace('id="ClockFace"', 'id="ClockFaceBreeze"', 1)
    svg = set_class(svg, "HourHand", "ColorScheme-Background")
    svg = set_class(svg, "MinuteHand", "ColorScheme-Background")
    svg = set_class(svg, "SecondHand", "ColorScheme-Text")
    frag, w, h = ornament("clock-face.svg", "halloween-face-")
    if (w, h) != (200, 200):
        raise RuntimeError("clock-face.svg must be 200x200 to match Breeze's clock")
    return append(svg, f'  <g id="ClockFace">{frag}</g>\n')


def build(out, palette, colors_text):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    for f in ("metadata.json", "plasmarc"):
        write(out / f, (SRC / f).read_text())
    write(out / "colors", colors_text)
    for variant in VARIANTS:
        for name, (orn, height, opacity, hints) in OVERLAYS.items():
            path = variant + name
            write(out / path, add_overlay(upstream(path), orn, height, opacity, hints))
        name, color, factor = TOOLTIP_SHADOW
        path = variant + name
        write(out / path, tint_shadow(upstream(path), palette[color], factor))
    write(out / "widgets/clock.svg", pumpkin_clock(upstream("widgets/clock.svg")))
    return out


def main():
    from build import render_colors
    from common import load_palette
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", nargs="?", default=str(ROOT / "build/user/plasma/desktoptheme/openSUSE-halloween"))
    args = ap.parse_args()
    palette = load_palette()
    print(build(args.out, palette, render_colors(palette)))


if __name__ == "__main__":
    main()
