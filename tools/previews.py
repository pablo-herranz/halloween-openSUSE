#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Turn screenshots from tools/dev/test-screens.sh into package previews.

Reads art/screenshots/*.png (1920x1080) and writes art/previews/, which
tools/build.py prefers over its generated mock-ups, and the web-sized images
in docs/screenshots/ that the README shows.
"""

from PIL import Image

from common import ROOT
from imaging import crop_ratio

SHOTS = ROOT / "art/screenshots"
OUT = ROOT / "art/previews"
DOCS = ROOT / "docs/screenshots"
TARGETS = {
    "preview.png": ("desktop-light.png", (600, 337)),
    "fullscreenpreview.jpg": ("desktop-light.png", (1920, 1080)),
    "lockscreen.png": ("lockscreen.png", (600, 337)),
    "splash.png": ("splash.png", (300, 169)),
    "sddm.png": ("sddm.png", (1200, 750)),
}


# README images: (screenshot, width). The hero is full width, the gallery
# shows two per row.
WEB = {
    "desktop.jpg": ("desktop-light.png", 1600),
    "desktop-night.jpg": ("desktop-dark.png", 960),
    "launcher.jpg": ("kickoff.png", 960),
    "dolphin.jpg": ("dolphin.png", 960),
    "file-types.jpg": ("dolphin-file-types.png", 960),
    "login.jpg": ("sddm.png", 960),
    "splash.jpg": ("splash.png", 960),
    "lockscreen.jpg": ("lockscreen.png", 960),
    "clock.jpg": ("clock.png", 960),
    "firefox.jpg": ("firefox.png", 960),
    "gnome.jpg": ("gnome.png", 960),
    "xfce.jpg": ("xfce.png", 960),
    "gdm.jpg": ("gdm.png", 960),
}


def web_images():
    DOCS.mkdir(parents=True, exist_ok=True)
    for name, (src, width) in WEB.items():
        f = SHOTS / src
        if not f.exists():
            print(f"skip  {name}: no {f.relative_to(ROOT)}")
            continue
        img = Image.open(f).convert("RGB")
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
        img.save(DOCS / name, "JPEG", quality=84, optimize=True, progressive=True)
        print(f"wrote {(DOCS / name).relative_to(ROOT)}")


def main():
    web_images()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (src, size) in TARGETS.items():
        f = SHOTS / src
        if not f.exists():
            print(f"skip  {name}: no {f.relative_to(ROOT)}")
            continue
        img = crop_ratio(Image.open(f).convert("RGB"), size[0] / size[1]).resize(size, Image.LANCZOS)
        if name.endswith(".jpg"):
            img.save(OUT / name, "JPEG", quality=90, optimize=True)
        else:
            img.save(OUT / name, "PNG", optimize=True)
        print(f"wrote {(OUT / name).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
