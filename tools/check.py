#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate build/ before it is deployed.

Checks metadata syntax, leftover tokens, colour contrast, image sizes and
file budgets, the Plasma style's SVG element IDs, icon SVG sanity, the Firefox
theme and REUSE compliance. `--release` also fails while placeholders are
still in use.
"""

import argparse
import configparser
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from PIL import Image

from common import BUILD, CACHE, FIREFOX, FIREFOX_ID, ROOT, SYSTEM, USER, VERSION, contrast, rgb

STYLE = USER / "plasma/desktoptheme/openSUSE-halloween"
LNF = USER / "plasma/look-and-feel/org.openSUSE.halloween.desktop/contents"
INI_NAMES = ("defaults", "plasmarc", "colors", "index.theme")
INI_SUFFIXES = (".colors", ".desktop", ".plymouth", ".overrides")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL  {msg}")


def ok(msg):
    print(f"ok    {msg}")


def text_files():
    for f in BUILD.rglob("*"):
        if not f.is_file() or f.relative_to(BUILD).parts[0] == "cache":
            continue
        if f.suffix in (".json", ".qml", ".js", ".svg", ".sh", *INI_SUFFIXES) or f.name in INI_NAMES:
            yield f


def check_syntax():
    n = 0
    for f in text_files():
        text = f.read_text()
        if f.suffix == ".json":
            try:
                json.loads(text)
            except ValueError as e:
                fail(f"{f.relative_to(BUILD)}: {e}")
        elif f.suffix in INI_SUFFIXES or f.name in INI_NAMES:
            cp = configparser.ConfigParser(strict=False, interpolation=None)
            try:
                cp.read_string(text)
            except configparser.Error as e:
                fail(f"{f.relative_to(BUILD)}: {e}")
        if f.suffix != ".sh" and re.search(r"@[A-Za-z_][A-Za-z0-9_]*@", text):
            fail(f"{f.relative_to(BUILD)}: unfilled @token@")
        n += 1
    ok(f"syntax and tokens in {n} text files")


def kde_colors(path):
    cp = configparser.ConfigParser(strict=False, interpolation=None)
    cp.optionxform = str
    cp.read_string(path.read_text())

    def get(group, key):
        return tuple(int(v) for v in cp[f"Colors:{group}"][key].split(","))
    return get


def check_contrast():
    get = kde_colors(USER / "color-schemes/openSUSEHalloween.colors")
    worst = {}
    for group in ("Window", "View", "Button", "Header", "Tooltip", "Complementary"):
        bg = get(group, "BackgroundNormal")
        rules = [("ForegroundNormal", 7.0), ("ForegroundInactive", 4.5)]
        if group in ("Window", "View"):
            rules += [(k, 4.5) for k in ("ForegroundLink", "ForegroundVisited", "ForegroundNegative",
                                         "ForegroundNeutral", "ForegroundPositive", "ForegroundActive")]
        for key, need in rules:
            c = contrast(get(group, key), bg)
            worst[key] = min(worst.get(key, 99), c)
            if c < need:
                fail(f"contrast {group}/{key} {c:.2f}:1 < {need}:1")
    c = contrast(get("Selection", "ForegroundNormal"), get("Selection", "BackgroundNormal"))
    if c < 4.5:
        fail(f"contrast Selection text {c:.2f}:1 < 4.5:1")
    ok("contrast: " + ", ".join(f"{k.removeprefix('Foreground')} {v:.1f}" for k, v in worst.items())
       + f", Selection {c:.1f}")


def dir_size(d):
    return sum(f.stat().st_size for f in d.rglob("*") if f.is_file())


def check_images():
    wall = USER / "wallpapers/openSUSEhalloween/contents"
    for sub in ("images", "images_dark"):
        files = sorted((wall / sub).glob("*.jpg"))
        if len(files) < 7:
            fail(f"wallpaper {sub}: only {len(files)} sizes")
        for f in files:
            w, h = (int(v) for v in f.stem.split("x"))
            if Image.open(f).size != (w, h):
                fail(f"{f.relative_to(BUILD)} is {Image.open(f).size}, not {w}x{h}")
            if w >= 3840 and f.stat().st_size > 3_000_000:
                fail(f"{f.relative_to(BUILD)} is {f.stat().st_size / 1e6:.1f} MB (> 3 MB)")
    expected = {"previews/preview.png": (600, 337), "previews/fullscreenpreview.jpg": (1920, 1080),
                "previews/lockscreen.png": (600, 337), "previews/splash.png": (300, 169)}
    for rel, size in expected.items():
        f = LNF / rel
        if not f.exists() or Image.open(f).size != size:
            fail(f"look-and-feel {rel} missing or not {size}")
    for d, limit in ((LNF / "splash", 1_000_000), (SYSTEM / "plymouth/openSUSE-halloween", 600_000)):
        size = dir_size(d)
        if size > limit:
            fail(f"{d.relative_to(BUILD)} is {size / 1e3:.0f} kB (> {limit / 1e3:.0f} kB)")
    for f in ("throbber-0001.png", "throbber-0040.png", "watermark.png"):
        if not (SYSTEM / "plymouth/openSUSE-halloween" / f).exists():
            fail(f"plymouth {f} missing")
    ok(f"images: wallpapers, previews, splash {dir_size(LNF / 'splash') / 1e3:.0f} kB, "
       f"plymouth {dir_size(SYSTEM / 'plymouth/openSUSE-halloween') / 1e3:.0f} kB")


def svg_ids(path):
    return {el.get("id") for el in ET.parse(path).iter() if el.get("id")}


def check_plasma_style():
    upstream = CACHE / "libplasma-breeze"
    n = 0
    for built in sorted(STYLE.rglob("*.svg")):
        rel = built.relative_to(STYLE)
        try:
            ids = svg_ids(built)
        except ET.ParseError as e:
            fail(f"plasma style {rel}: {e}")
            continue
        missing = svg_ids(upstream / rel) - ids
        if missing:
            fail(f"plasma style {rel} lost Breeze elements: {sorted(missing)[:5]}")
        need = {"dialogs/background.svg": {"overlay", "hint-overlay-pos-right"},
                "widgets/panel-background.svg": {"overlay", "hint-overlay-tile-horizontal"},
                "widgets/clock.svg": {"ClockFace", "HourHand", "MinuteHand", "SecondHand"}}
        for suffix, req in need.items():
            if str(rel).endswith(suffix) and not req <= ids:
                fail(f"plasma style {rel} lacks {sorted(req - ids)}")
        n += 1
    if not (STYLE / "colors").exists():
        fail("plasma style has no colors file")
    ok(f"plasma style: {n} SVGs keep every Breeze element ID")


def check_icons():
    icons = USER / "icons/openSUSE-halloween"
    n = 0
    for f in sorted(icons.rglob("*.svg")):
        rel = f.relative_to(icons)
        text = f.read_text()
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            fail(f"icon {rel}: {e}")
            continue
        if not root.get("viewBox"):
            fail(f"icon {rel}: no viewBox")
        if f.stat().st_size > 60_000:
            fail(f"icon {rel}: {f.stat().st_size / 1e3:.0f} kB (> 60 kB)")
        if re.search(r"<(\w+:)?(text|script|image)\b", text) or re.search(r'href="(https?:|file:)', text):
            fail(f"icon {rel}: contains text, script, raster images or external links")
        n += 1
    ok(f"icons: {n} SVGs")


def check_firefox():
    theme = FIREFOX / "openSUSE-halloween"
    try:
        manifest = json.loads((theme / "manifest.json").read_text())
        colors, images = manifest["theme"]["colors"], manifest["theme"]["images"]["additional_backgrounds"]
    except (OSError, ValueError, KeyError) as e:
        fail(f"firefox manifest.json: {e!r}")
        return
    if manifest.get("version") != VERSION:
        fail(f"firefox version {manifest.get('version')} is not {VERSION}")
    if manifest.get("browser_specific_settings", {}).get("gecko", {}).get("id") != FIREFOX_ID:
        fail(f"firefox add-on ID is not {FIREFOX_ID}")

    # Text on its background: (text, background, minimum)
    pairs = [("tab_text", "tab_selected", 4.5), ("tab_text", "toolbar", 4.5), ("tab_background_text", "frame", 4.5),
             ("tab_background_text", "frame_inactive", 4.5), ("toolbar_text", "toolbar", 4.5), ("icons", "toolbar", 3.0),
             ("toolbar_field_text", "toolbar_field", 4.5), ("toolbar_field_text_focus", "toolbar_field_focus", 4.5),
             ("toolbar_field_highlight_text", "toolbar_field_highlight", 4.5), ("popup_text", "popup", 4.5),
             ("popup_highlight_text", "popup_highlight", 4.5), ("sidebar_text", "sidebar", 4.5),
             ("sidebar_highlight_text", "sidebar_highlight", 4.5), ("ntp_text", "ntp_background", 4.5),
             ("ntp_text", "ntp_card_background", 4.5)]
    worst = 99
    for text, bg, need in pairs:
        if text not in colors or bg not in colors:
            fail(f"firefox colours lack {text} or {bg}")
            continue
        c = contrast(colors[text], colors[bg])
        worst = min(worst, c)
        if c < need:
            fail(f"firefox contrast {text} on {bg} {c:.2f}:1 < {need}:1")

    title = 99
    for name in images:
        f = theme / name
        if not f.exists():
            fail(f"firefox image {name} missing")
            continue
        img = Image.open(f)
        if img.height > 200 or f.stat().st_size > 300_000:
            fail(f"firefox {name} is {img.width}x{img.height}, {f.stat().st_size / 1e3:.0f} kB (> 200 px or 300 kB)")
        # Background tab titles over the image: every tab-sized patch of the
        # 44 px tab strip, with the frame colour showing through
        over = Image.new("RGBA", img.size, rgb(colors["frame"]) + (255,))
        over.alpha_composite(img.convert("RGBA"))
        strip = over.convert("RGB").crop((0, 0, img.width, 44))
        title = min(contrast(colors["tab_background_text"], strip.crop((x, 0, x + 100, 44)).resize((1, 1), Image.BOX).getpixel((0, 0)))
                    for x in range(0, img.width - 99, 10))
        if title < 4.5:
            fail(f"firefox tab titles over {name} {title:.2f}:1 < 4.5:1")

    xpi = FIREFOX / "openSUSE-halloween.xpi"
    try:
        with zipfile.ZipFile(xpi) as z:
            packed = {i.filename: z.read(i) for i in z.infolist()}
    except (OSError, zipfile.BadZipFile) as e:
        fail(f"firefox {xpi.name}: {e}")
        return
    unpacked = {f.name: f.read_bytes() for f in theme.iterdir()}
    if packed != unpacked:
        fail(f"firefox {xpi.name} does not match {theme.name}/")
    ok(f"firefox theme {manifest['version']}: contrast {worst:.1f}, tab titles over the header {title:.1f}, "
       f"{xpi.name} {xpi.stat().st_size / 1e3:.0f} kB")


def check_reuse():
    reuse = shutil.which("reuse") or str(ROOT / "tools/.venv/bin/reuse")
    if not Path(reuse).exists():
        print("skip  reuse lint (reuse not installed)")
        return
    r = subprocess.run([reuse, "--root", str(ROOT), "lint"], capture_output=True, text=True)
    if r.returncode:
        fail("reuse lint:\n" + r.stdout[-2000:])
    else:
        ok("reuse lint")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", action="store_true", help="fail while placeholders are in use")
    args = ap.parse_args()
    if not USER.exists():
        sys.exit("build/ is empty: run tools/build.py first")
    check_syntax()
    check_contrast()
    check_images()
    check_plasma_style()
    check_icons()
    check_firefox()
    check_reuse()
    placeholders = (BUILD / "placeholders.txt").read_text().split("\n") if (BUILD / "placeholders.txt").exists() else []
    placeholders = [p for p in placeholders if p]
    if placeholders:
        msg = f"{len(placeholders)} placeholders still in use (build/placeholders.txt)"
        fail(msg) if args.release else print(f"note  {msg}")
    print(f"\n{len(failures)} problem(s)" if failures else "\nall checks passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
