#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Turn screenshots from install/test-screens.sh into package previews.

Reads art/screenshots/{desktop-light,lockscreen,splash,sddm}.png and writes
art/previews/, which tools/build.py prefers over its generated mock-ups.
"""

from PIL import Image

from imaging import crop_ratio
from common import ROOT

SHOTS = ROOT / "art/screenshots"
OUT = ROOT / "art/previews"
TARGETS = {
    "preview.png": ("desktop-light.png", (600, 337)),
    "fullscreenpreview.jpg": ("desktop-light.png", (1920, 1080)),
    "lockscreen.png": ("lockscreen.png", (600, 337)),
    "splash.png": ("splash.png", (300, 169)),
    "sddm.png": ("sddm.png", (1200, 750)),
}


def main():
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
