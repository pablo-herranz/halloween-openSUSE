# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Image helpers shared by the build targets."""

import tomllib

from PIL import Image

from common import ROOT

CROPS = tomllib.loads((ROOT / "art/crops.toml").read_text())


def crop_ratio(img, ratio, fx=0.5, fy=0.5):
    """Crop `img` to aspect `ratio` around the focus point (fx, fy), 0..1."""
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        x = min(max(round(fx * w - nw / 2), 0), w - nw)
        return img.crop((x, 0, x + nw, h))
    nh = round(w / ratio)
    y = min(max(round(fy * h - nh / 2), 0), h - nh)
    return img.crop((0, y, w, y + nh))


def crop_to(wallpapers, variant, ratio):
    """Crop a wallpaper master to `ratio` around its focus point in art/crops.toml."""
    focus = CROPS.get(variant, {})
    return crop_ratio(wallpapers[variant], ratio, focus.get("focus_x", 0.5), focus.get("focus_y", 0.5))


def save_jpeg(img, path, limit=None):
    """Save as JPEG, stepping the quality down until it fits `limit` bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    for q in (90, 88, 86, 84):
        img.convert("RGB").save(path, "JPEG", quality=q, subsampling=0, optimize=True, progressive=True)
        if limit is None or path.stat().st_size <= limit:
            break
    return path


def save_png(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return path


def fit(img, size):
    """`img` scaled into a transparent size x size square, centred."""
    out = img.copy()
    out.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(out.convert("RGBA"), ((size - out.width) // 2, (size - out.height) // 2))
    return canvas


def vignette(img, strength=0.55):
    w, h = img.size
    mask = Image.radial_gradient("L").resize((w, h), Image.LANCZOS)
    mask = mask.point(lambda v: int(min(255, max(0, (v - 90) * 1.6)) * strength))
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), img.convert("RGB"), mask)
