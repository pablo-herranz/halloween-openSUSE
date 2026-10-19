#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build every installable piece of halloween-openSUSE into build/.

build/user/     goes to ~/.local/share (no root needed)
build/root/     goes to /usr/share (SDDM and Plymouth)
build/firefox/  the Firefox theme, unpacked and as an .xpi
Any art master missing from art/source/ is replaced by a drawn placeholder,
listed in build/placeholders.txt.
"""

import hashlib
import json
import math
import shutil
import tomllib
import zipfile

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import placeholders as ph
import plasma_style
import vectors
from common import BUILD, FIREFOX_ID, ROOT, VERSION, contrast, fill_tokens, load_palette, rgb, write

USER = BUILD / "user"
SYSTEM = BUILD / "root"
FIREFOX = BUILD / "firefox"
SIZES = [(3840, 2160), (2560, 1440), (1920, 1080), (1366, 768),   # 16:9
         (2560, 1600), (1920, 1200), (1440, 900)]                 # 16:10
MAX_4K_BYTES = 3_000_000
LNF_ID = "org.openSUSE.halloween.desktop"
SDDM_DIR = "/usr/share/sddm/themes/breeze-openSUSE-halloween"
PLYMOUTH_DIR = "/usr/share/plymouth/themes/openSUSE-halloween"
FIREFOX_HEADER_H = 200   # Firefox's recommended header height
FIREFOX_PAD = 150        # plain frame on the right, under the window buttons
FIREFOX_DIM = 0.8        # the art's most opacity over the frame colour
FIREFOX_TAB_STRIP_H = 44  # the top of the header that stays visible above the toolbar
FIREFOX_TITLE_CONTRAST = 5.0
CROPS = tomllib.loads((ROOT / "art/crops.toml").read_text())

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


def crop_to(wallpapers, variant, ratio):
    """Crop a wallpaper master to `ratio` around its focus point in art/crops.toml."""
    focus = CROPS.get(variant, {})
    return crop_ratio(wallpapers[variant], ratio, focus.get("focus_x", 0.5), focus.get("focus_y", 0.5))


def splash_backdrop(night):
    """The part of the night master that leaves the chameleon out (art/crops.toml [splash])."""
    x0, y0, x1, y1 = CROPS["splash"]["box"]
    region = night.crop((round(x0 * night.width), round(y0 * night.height),
                         round(x1 * night.width), round(y1 * night.height)))
    return crop_ratio(region, 16 / 9)


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
    src = ROOT / "wallpapers/openSUSEhalloween"
    out = USER / "wallpapers/openSUSEhalloween"
    write(out / "metadata.json", (src / "metadata.json").read_text())
    images = {}
    for variant, sub in (("dusk", "images"), ("night", "images_dark")):
        images[variant] = master(f"wallpaper-{variant}", lambda v=variant: ph.wallpaper(p, v)).convert("RGB")
        for w, h in SIZES:
            save_jpeg(crop_to(images, variant, w / h).resize((w, h), Image.LANCZOS),
                      out / f"contents/{sub}/{w}x{h}.jpg", MAX_4K_BYTES if w >= 3840 else None)
    save_png(crop_to(images, "dusk", 16 / 9).resize((400, 225), Image.LANCZOS), out / "contents/screenshot.png")
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
    night = splash_backdrop(wallpapers["night"]).resize((1920, 1080), Image.LANCZOS)
    bg = ImageEnhance.Brightness(night.filter(ImageFilter.GaussianBlur(8))).enhance(0.55)
    save_jpeg(bg, splash / "images/background.jpg")
    save_png(fit(hero, 512), splash / "images/hero.png")
    save_png(fit(lit, 192), splash / "images/pumpkin-lit.png")
    save_png(fit(unlit, 192), splash / "images/pumpkin-unlit.png")
    save_png(ph.glow(p, 256), splash / "images/glow.png")
    write(splash / "palette.js", ".pragma library\n// Generated from art/palette.toml by tools/build.py\n"
          + "".join(f'var {k} = "{p[k]}";\n' for k in ("night", "cream", "pumpkin", "candle")))

    previews = out / "contents/previews"
    previews.mkdir(parents=True, exist_ok=True)
    shots = ROOT / "art/previews"
    made = {
        "preview.png": lambda: panel_mock(crop_to(wallpapers, "dusk", 16 / 9), p).resize((600, 337), Image.LANCZOS),
        "fullscreenpreview.jpg": lambda: panel_mock(crop_to(wallpapers, "dusk", 16 / 9), p).resize((1920, 1080), Image.LANCZOS),
        "lockscreen.png": lambda: ImageEnhance.Brightness(crop_to(wallpapers, "night", 16 / 9)).enhance(0.8).resize((600, 337), Image.LANCZOS),
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
    for rel, svg in vectors.icons(p).items():
        write(out / rel, svg)
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
    bg = crop_to(wallpapers, "night", 16 / 10).resize((2560, 1600), Image.LANCZOS)
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


def firefox_header(p, night):
    """A band of the night master (art/crops.toml [firefox]) that fades into the
    frame colour: slowly to the left, where the tabs are, quickly to the right.
    Bright parts (the moon) are made more transparent, so tab titles drawn over
    them keep FIREFOX_TITLE_CONTRAST against the frame showing through."""
    c = CROPS["firefox"]
    w = c["width"]
    h = round(night.height * w / night.width)
    top, art_w = round(c["top"] * h), round(c["right"] * w)
    art = night.resize((w, h), Image.LANCZOS).crop((0, top, art_w, top + FIREFOX_HEADER_H))
    img = Image.new("RGBA", (art_w + FIREFOX_PAD, FIREFOX_HEADER_H), (0, 0, 0, 0))
    img.paste(art, (0, 0))

    # The most opacity each column can have behind the tab titles, spread out
    # over a tab's width
    frame = rgb(p["night"])
    band = img.convert("RGB").crop((0, 0, img.width, FIREFOX_TAB_STRIP_H)).resize((img.width, 1), Image.BOX)

    def readable(x):
        col = band.getpixel((x, 0))
        steps = [a / 50 for a in range(51)
                 if contrast(p["cream"], [f + (v - f) * a / 50 for f, v in zip(frame, col)]) >= FIREFOX_TITLE_CONTRAST]
        return round(255 * min(FIREFOX_DIM, max(steps, default=0)))
    limit = Image.new("L", (img.width, 1))
    limit.putdata([readable(x) for x in range(img.width)])
    limit = limit.filter(ImageFilter.MinFilter(121)).filter(ImageFilter.BoxBlur(60))

    fade_l, fade_r = round(art_w * 0.45), 60
    row = [round(limit.getpixel((x, 0)) * min(1, x / fade_l) ** 1.6 * min(1, max(0, (art_w - x) / fade_r)) ** 1.2)
           for x in range(img.width)]
    img.putalpha(Image.frombytes("L", img.size, bytes(row * img.height)))
    return img


def build_firefox(p, wallpapers):
    out = FIREFOX / "openSUSE-halloween"
    header = "header.png"
    save_png(firefox_header(p, wallpapers["night"]), out / header)
    values = {**p, **{f"{k}_rgb": ", ".join(str(c) for c in rgb(v)) for k, v in p.items()},
              "VERSION": VERSION, "FIREFOX_ID": FIREFOX_ID, "HEADER": header}
    write(out / "manifest.json", fill_tokens((ROOT / "firefox/manifest.json.in").read_text(), values))
    # A fixed timestamp keeps the .xpi identical between builds
    with zipfile.ZipFile(FIREFOX / "openSUSE-halloween.xpi", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            z.writestr(zipfile.ZipInfo(f.name, (2026, 10, 1, 0, 0, 0)), f.read_bytes(), zipfile.ZIP_DEFLATED)


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
    for d in (USER, SYSTEM, FIREFOX, BUILD / "install"):
        if d.exists():
            shutil.rmtree(d)
    p = load_palette()
    colors = render_colors(p)
    write(USER / "color-schemes/openSUSEHalloween.colors", colors)
    plasma_style.build(USER / "plasma/desktoptheme/openSUSE-halloween", p, colors)
    placeholders_used.extend(f"ornament {n}" for n in plasma_style.ORNAMENTS if vectors.ornament(n, p) is None)

    wallpapers = build_wallpaper(p)
    hero = master("hero", lambda: ph.hero(p)).convert("RGBA")
    lit = master("lantern-lit", lambda: ph.pumpkin(p, 192, lit=True)).convert("RGBA")
    unlit = master("lantern-unlit", lambda: ph.pumpkin(p, 192, lit=False)).convert("RGBA")
    build_look_and_feel(p, wallpapers, hero, lit, unlit)
    build_icons(p)
    build_sddm(p, wallpapers)
    build_plymouth(p, hero, lit, unlit)
    build_firefox(p, wallpapers)
    build_install_scripts()
    write_manifest()
    print(f"built {BUILD}")
    if placeholders_used:
        print(f"placeholders: {len(placeholders_used)} (see build/placeholders.txt)")


if __name__ == "__main__":
    main()
