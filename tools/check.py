#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate build/ before it is deployed.

Checks metadata syntax, leftover tokens, colour contrast, image sizes and
file budgets, the Plasma style's SVG element IDs, icon SVG sanity and REUSE
compliance. `--release` also fails while placeholders are still in use.
"""

import argparse
import configparser
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

from common import BUILD, CACHE, ROOT, contrast

USER, SYSTEM = BUILD / "user", BUILD / "root"
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
