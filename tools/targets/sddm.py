# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""The SDDM login theme: a thin layer over openSUSE's breeze-openSUSE theme
(installed by install/install-root.sh) with the night wallpaper."""

from PIL import Image, ImageEnhance

from common import ROOT, SYSTEM, fill_tokens, write
from imaging import crop_to, save_jpeg, save_png, vignette

DESKTOP = "plasma"
ID = "breeze-openSUSE-halloween"
INSTALL_DIR = f"/usr/share/sddm/themes/{ID}"


def build(ctx):
    src = ROOT / "plasma/sddm" / ID
    out = SYSTEM / "sddm" / ID
    write(out / "metadata.desktop", (src / "metadata.desktop").read_text())
    write(out / "theme.conf.overrides",
          fill_tokens((src / "theme.conf.overrides.in").read_text(), {**ctx.palette, "THEMEDIR": INSTALL_DIR}))
    bg = crop_to(ctx.wallpapers, "night", 16 / 10).resize((2560, 1600), Image.LANCZOS)
    bg = vignette(ImageEnhance.Brightness(bg).enhance(0.9))
    save_jpeg(bg, out / "background.jpg")
    shots = ROOT / "art/previews/sddm.png"
    preview = Image.open(shots) if shots.exists() else bg
    save_png(preview.convert("RGB").resize((600, 375), Image.LANCZOS), out / "preview.png")
