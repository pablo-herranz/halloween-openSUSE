# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The SDDM login theme: openSUSE's breeze-openSUSE theme (package
plasma6-sddm-theme-openSUSE) with the night wallpaper. Its QML is linked, not
copied, so updates of breeze-openSUSE keep flowing in."""

import os

from PIL import Image, ImageEnhance

from common import DEFAULTS, ROOT, SYSTEM, fill_tokens, write
from imaging import crop_to, save_jpeg, save_png, scrim, vignette

DESKTOP = "plasma"
ID = "breeze-openSUSE-halloween"
BASE = "breeze-openSUSE"
INSTALL_DIR = f"/usr/share/sddm/themes/{ID}"
# SDDM zooms its background to fill each screen: 16:10 at 4K, cropped like the
# zoomed wallpaper pictures, stays sharp on 4K and keeps the chameleon
BACKGROUND = (3840, 2400)
# Everything in breeze-openSUSE except its metadata, preview and theme.conf
BASE_FILES = ["Background.qml", "KeyboardButton.qml", "Login.qml", "Main.qml", "Messages.sh",
              "SessionButton.qml", "default-logo.svg", "faces"]


def build(ctx):
    src = ROOT / "plasma/sddm" / ID
    out = SYSTEM / "sddm" / ID
    write(out / "metadata.desktop", (src / "metadata.desktop").read_text())
    tokens = {**ctx.palette, "THEMEDIR": INSTALL_DIR}
    write(out / "theme.conf", fill_tokens((src / "theme.conf.in").read_text(), tokens))
    for name in BASE_FILES:
        os.symlink(f"../{BASE}/{name}", out / name)
    defaults = ROOT / "plasma/sddm/defaults/zz-openSUSE-halloween.conf"
    write(DEFAULTS / "sddm.conf.d" / defaults.name, defaults.read_text())
    bg = crop_to(ctx.wallpapers, "night", BACKGROUND[0] / BACKGROUND[1], zoomed=True).resize(BACKGROUND, Image.LANCZOS)
    # the power actions sit low on the screen, in a band that is light in the
    # picture: a scrim keeps their labels readable
    bg = scrim(vignette(ImageEnhance.Brightness(bg).enhance(0.9)))
    save_jpeg(bg, out / "background.jpg")
    shots = ROOT / "art/previews/sddm.png"
    preview = Image.open(shots) if shots.exists() else bg
    save_png(preview.convert("RGB").resize((600, 375), Image.LANCZOS), out / "preview.png")
