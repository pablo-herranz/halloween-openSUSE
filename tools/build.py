#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build every installable piece of halloween-openSUSE into build/.

build/user/  goes to ~/.local/share (no root needed)
build/root/  goes to /usr/share (SDDM and Plymouth)
Any art master missing from art/source/ is replaced by a drawn placeholder,
listed in build/placeholders.txt.
"""

import hashlib
import json
import math
import shutil
import tomllib

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import placeholders as ph
import plasma_style
from common import BUILD, ROOT, fill_tokens, load_palette, rgb, write

USER = BUILD / "user"
SYSTEM = BUILD / "root"
SIZES = [(3840, 2160), (2560, 1440), (1920, 1080), (1366, 768),   # 16:9
         (2560, 1600), (1920, 1200), (1440, 900)]                 # 16:10
MAX_4K_BYTES = 3_000_000
LNF_ID = "org.openSUSE.halloween.desktop"
SDDM_DIR = "/usr/share/sddm/themes/breeze-openSUSE-halloween"
PLYMOUTH_DIR = "/usr/share/plymouth/themes/openSUSE-halloween"

placeholders_used = []


def render_colors(p):
    tpl = (ROOT / "plasma/color-schemes/openSUSEHalloween.colors.in").read_text()
    return fill_tokens(tpl, p, fmt=lambda h: ",".join(str(c) for c in rgb(h)))


def master(name, make):
    """art/source/<name>.{png,jpg,webp} if present, otherwise a placeholder."""
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        f = ROOT / "art/source" / (name + ext)
        if f.exists():
            if f.read_bytes()[:40].startswith(b"version https://git-lfs"):
                raise SystemExit(f"{f} is a Git LFS pointer: run `git lfs pull` first")
            return Image.open(f)
    placeholders_used.append(name)
    return make()


def crop_ratio(img, ratio, fx=0.5, fy=0.5):
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        x = min(max(round(fx * w - nw / 2), 0), w - nw)
        return img.crop((x, 0, x + nw, h))
    nh = round(w / ratio)
    y = min(max(round(fy * h - nh / 2), 0), h - nh)
    return img.crop((0, y, w, y + nh))


def save_jpeg(img, path, limit=None):
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


def panel_mock(img, p):
    """Draw a translucent panel strip so previews read as a desktop."""
    out = img.convert("RGBA")
    h = max(8, round(out.height * 0.045))
    strip = Image.new("RGBA", (out.width, h), rgb(p["night"]) + (215,))
    out.alpha_composite(strip, (0, out.height - h))
    return out.convert("RGB")


# --- components ----------------------------------------------------------------

def build_wallpaper(p):
    crops = tomllib.loads((ROOT / "art/crops.toml").read_text())
    src = ROOT / "wallpapers/openSUSEhalloween"
    out = USER / "wallpapers/openSUSEhalloween"
    write(out / "metadata.json", (src / "metadata.json").read_text())
    images = {}
    for variant, sub in (("dusk", "images"), ("night", "images_dark")):
        img = master(f"wallpaper-{variant}", lambda v=variant: ph.wallpaper(p, v)).convert("RGB")
        focus = crops.get(variant, {})
        for w, h in SIZES:
            c = crop_ratio(img, w / h, focus.get("focus_x", 0.5), focus.get("focus_y", 0.5))
            save_jpeg(c.resize((w, h), Image.LANCZOS), out / f"contents/{sub}/{w}x{h}.jpg",
                      MAX_4K_BYTES if w >= 3840 else None)
        images[variant] = img
    save_png(crop_ratio(images["dusk"], 16 / 9).resize((400, 225), Image.LANCZOS), out / "contents/screenshot.png")
    return images


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


def build_look_and_feel(p, wallpapers, hero, lit, unlit):
    src = ROOT / "plasma/look-and-feel" / LNF_ID
    out = USER / "plasma/look-and-feel" / LNF_ID
    shutil.copytree(src, out)
    splash = out / "contents/splash"
    night = crop_ratio(wallpapers["night"], 16 / 9).resize((1920, 1080), Image.LANCZOS)
    bg = ImageEnhance.Brightness(night.filter(ImageFilter.GaussianBlur(8))).enhance(0.55)
    save_jpeg(bg, splash / "images/background.jpg")
    save_png(fit(hero, 512), splash / "images/hero.png")
    save_png(fit(lit, 192), splash / "images/pumpkin-lit.png")
    save_png(fit(unlit, 192), splash / "images/pumpkin-unlit.png")
    save_png(ph.glow(p, 256), splash / "images/glow.png")
    write(splash / "palette.js", ".pragma library\n// Generated from art/palette.toml by tools/build.py\n"
          + "".join(f'var {k} = "{p[k]}";\n' for k in ("night", "cream", "pumpkin", "candle")))

    previews = out / "contents/previews"
    shots = ROOT / "art/previews"
    made = {
        "preview.png": lambda: panel_mock(crop_ratio(wallpapers["dusk"], 16 / 9), p).resize((600, 337), Image.LANCZOS),
        "fullscreenpreview.jpg": lambda: panel_mock(crop_ratio(wallpapers["dusk"], 16 / 9), p).resize((1920, 1080), Image.LANCZOS),
        "lockscreen.png": lambda: ImageEnhance.Brightness(crop_ratio(wallpapers["night"], 16 / 9)).enhance(0.8).resize((600, 337), Image.LANCZOS),
        "splash.png": lambda: splash_mock(p, bg, fit(hero, 512), fit(lit, 192)).resize((300, 169), Image.LANCZOS),
    }
    for name, make in made.items():
        if (shots / name).exists():
            shutil.copy2(shots / name, previews / name)
        else:
            img = make()
            (save_jpeg if name.endswith(".jpg") else save_png)(img, previews / name)
    return bg


def build_icons(p):
    src = ROOT / "icons/openSUSE-halloween"
    out = USER / "icons/openSUSE-halloween"
    shutil.copytree(src, out)
    for rel, svg in ph.icon_svgs(p).items():
        if not (out / rel).exists():
            write(out / rel, svg)
            placeholders_used.append(f"icon {rel}")


def build_sddm(p, wallpapers):
    src = ROOT / "sddm/breeze-openSUSE-halloween"
    out = SYSTEM / "sddm/breeze-openSUSE-halloween"
    write(out / "metadata.desktop", (src / "metadata.desktop").read_text())
    write(out / "theme.conf.overrides",
          fill_tokens((src / "theme.conf.overrides.in").read_text(), {**p, "THEMEDIR": SDDM_DIR}))
    bg = crop_ratio(wallpapers["night"], 16 / 10).resize((2560, 1600), Image.LANCZOS)
    bg = vignette(ImageEnhance.Brightness(bg).enhance(0.9))
    save_jpeg(bg, out / "background.jpg")
    shots = ROOT / "art/previews/sddm.png"
    preview = Image.open(shots) if shots.exists() else bg
    save_png(preview.convert("RGB").resize((600, 375), Image.LANCZOS), out / "preview.png")


def build_plymouth(p, hero, lit, unlit):
    src = ROOT / "plymouth/openSUSE-halloween"
    out = SYSTEM / "plymouth/openSUSE-halloween"
    hexes = {k: "0x" + v.lstrip("#").lower() for k, v in p.items()}
    write(out / "openSUSE-halloween.plymouth",
          fill_tokens((src / "openSUSE-halloween.plymouth.in").read_text(), {**hexes, "IMAGEDIR": PLYMOUTH_DIR}))
    save_png(fit(hero, 300), out / "watermark.png")
    size, frames = 64, 40
    small_lit, small_unlit = fit(lit, 48), fit(unlit, 48)
    for i in range(frames):
        t = i / frames * math.tau
        f = 0.72 + 0.28 * (0.5 + 0.5 * math.sin(2 * t + 0.7 * math.sin(3 * t)))
        frame = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        frame.alpha_composite(ph.glow(p, size, f))
        frame.alpha_composite(small_unlit, (8, 8))
        lit_f = small_lit.copy()
        lit_f.putalpha(lit_f.getchannel("A").point(lambda a: int(a * f)))
        frame.alpha_composite(lit_f, (8, 8))
        for prefix in ("throbber", "animation"):
            save_png(frame, out / f"{prefix}-{i + 1:04d}.png")


def build_install_scripts():
    out = BUILD / "install"
    shutil.copytree(ROOT / "install", out)
    for f in out.iterdir():
        if f.suffix == ".sh":
            f.chmod(0o755)


def write_manifest():
    lines = []
    for f in sorted(BUILD.rglob("*")):
        rel = f.relative_to(BUILD)
        if f.is_file() and rel.parts[0] in ("user", "root", "install"):
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}")
    write(BUILD / "MANIFEST.sha256", "\n".join(lines) + "\n")
    write(BUILD / "placeholders.txt", "".join(f"{n}\n" for n in placeholders_used))
    write(BUILD / "build-info.json", json.dumps({"placeholders": placeholders_used}, indent=2) + "\n")


def main():
    for d in (USER, SYSTEM, BUILD / "install"):
        if d.exists():
            shutil.rmtree(d)
    p = load_palette()
    colors = render_colors(p)
    write(USER / "color-schemes/openSUSEHalloween.colors", colors)
    plasma_style.build(USER / "plasma/desktoptheme/openSUSE-halloween", p, colors)

    wallpapers = build_wallpaper(p)
    hero = master("hero", lambda: ph.hero(p)).convert("RGBA")
    lit = master("lantern-lit", lambda: ph.pumpkin(p, 192, lit=True)).convert("RGBA")
    unlit = master("lantern-unlit", lambda: ph.pumpkin(p, 192, lit=False)).convert("RGBA")
    build_look_and_feel(p, wallpapers, hero, lit, unlit)
    build_icons(p)
    build_sddm(p, wallpapers)
    build_plymouth(p, hero, lit, unlit)
    build_install_scripts()
    write_manifest()
    print(f"built {BUILD}")
    if placeholders_used:
        print(f"placeholders: {len(placeholders_used)} (see build/placeholders.txt)")


if __name__ == "__main__":
    main()
