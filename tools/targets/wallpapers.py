# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The wallpaper package: dusk (light) and night (dark) variants at common
screen sizes, cropped around the focus points in art/crops.toml."""

from PIL import Image

from common import SHARED, USER, write
from imaging import crop_to, save_jpeg, save_png

DESKTOP = "shared"
ID = "openSUSEhalloween"
SIZES = [(3840, 2160), (2560, 1440), (1920, 1080), (1366, 768),   # 16:9
         (2560, 1600), (1920, 1200), (1440, 900)]                 # 16:10
MAX_4K_BYTES = 3_000_000


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
