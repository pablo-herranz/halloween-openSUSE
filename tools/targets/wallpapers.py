# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The wallpaper package: dusk (light) and night (dark) variants at common
screen sizes, cropped around the chameleon (art/crops.toml), for Plasma. And
one picture of each for desktops that zoom a single picture to fill any
screen (GNOME, Xfce): 16:10, with the chameleon in the middle of what
zooming keeps."""

from PIL import Image

from common import SHARED, USER, write
from imaging import crop_to, save_jpeg, save_png

DESKTOP = "shared"
ID = "openSUSEhalloween"
# One or more sizes per common screen shape: Plasma picks the closest aspect
# ratio, then the closest size, and crops the rest away.
SIZES = [(5120, 2880), (3840, 2160), (2560, 1440), (1920, 1080), (1366, 768),   # 16:9
         (3840, 2400), (2560, 1600), (1920, 1200), (1440, 900),                 # 16:10
         (3000, 2000),                                                         # 3:2
         (3440, 1440),                                                         # 21:9
         (5120, 1440),                                                         # 32:9
         (2048, 1536),                                                         # 4:3
         (1280, 1024),                                                         # 5:4
         (1440, 2560)]                                                         # 9:16, portrait
MAX_4K_BYTES = 3_000_000
ZOOMED = (3840, 2400)


def build(ctx):
    src = SHARED / "wallpapers" / ID
    out = USER / "wallpapers" / ID
    write(out / "metadata.json", (src / "metadata.json").read_text())
    images = ctx.wallpapers
    for variant, sub in (("dusk", "images"), ("night", "images_dark")):
        for w, h in SIZES:
            save_jpeg(crop_to(images, variant, w / h).resize((w, h), Image.LANCZOS),
                      out / f"contents/{sub}/{w}x{h}.jpg", MAX_4K_BYTES if w >= 3840 else None)
    save_png(crop_to(images, "dusk", 16 / 9).resize((400, 225), Image.LANCZOS), out / "contents/screenshot.png")
    for variant in ("dusk", "night"):
        save_jpeg(crop_to(images, variant, ZOOMED[0] / ZOOMED[1], zoomed=True).resize(ZOOMED, Image.LANCZOS),
                  USER / "backgrounds" / ID / f"{variant}.jpg", MAX_4K_BYTES)
