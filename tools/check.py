#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate build/ before it is installed.

Checks, for the desktops that were built: metadata syntax, leftover tokens,
Plasma metadata against KDE's KPlugin schema, colour contrast, image sizes and
file budgets, the Plasma style's SVG element IDs, the SDDM theme's links, the
icon theme and its SVGs, the Firefox theme, a staged install and uninstall, and
REUSE compliance. `--release` also fails while placeholders are still in use.
"""

import argparse
import base64
import configparser
import io
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from jsonschema import Draft7Validator
from PIL import Image, ImageFilter

import install
from common import BUILD, CACHE, FIREFOX, FIREFOX_ID, ROOT, SYSTEM, USER, VERSION, contrast, fetch, load_palette, rgb

STYLE = USER / "plasma/desktoptheme/openSUSE-halloween"
LNF = USER / "plasma/look-and-feel/org.openSUSE.halloween.desktop/contents"
INI_NAMES = ("defaults", "plasmarc", "colors", "index.theme")
INI_SUFFIXES = (".colors", ".desktop", ".plymouth", ".overrides", ".override")
THEMES = USER / "themes"

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
        if (f.suffix in (".json", ".qml", ".js", ".svg", ".sh", ".css", ".xml", *INI_SUFFIXES)
                or f.name in INI_NAMES or f.name == "theme"):
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
        elif f.suffix == ".xml":
            try:
                ET.parse(f)
            except ET.ParseError as e:
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


def check_metadata():
    """Plasma's metadata.json files against KDE's KPlugin schema, plus the keys
    Plasma shows to users."""
    pin = tomllib.loads((ROOT / "tools/upstream.toml").read_text())["kpluginmetadata"]
    schema = fetch(pin["url"], pin["sha256"], CACHE / "kde/kpluginmetadata.schema.json")
    validator = Draft7Validator(json.loads(schema.read_text()))
    files = sorted(USER.rglob("metadata.json"))
    for f in files:
        rel = f.relative_to(BUILD)
        try:
            data = json.loads(f.read_text())
        except ValueError:
            continue  # check_syntax reports it
        for e in validator.iter_errors(data):
            fail(f"{rel}: {e.json_path}: {e.message}")
        plugin = data.get("KPlugin", {})
        for key in ("Id", "Name", "Description", "Authors", "License", "Version"):
            if not plugin.get(key):
                fail(f"{rel}: KPlugin has no {key}")
        if plugin.get("Version") and plugin["Version"] != VERSION:
            fail(f"{rel}: version {plugin['Version']} is not {VERSION}")
        spdx(rel, plugin.get("License", ""))
    for f in sorted(SYSTEM.glob("sddm/*/metadata.desktop")):
        cp = configparser.ConfigParser(interpolation=None)
        cp.read_string(f.read_text())
        spdx(f.relative_to(BUILD), cp.get("SddmGreeterTheme", "License", fallback=""))
    ok(f"metadata: {len(files)} metadata.json files match KDE's KPlugin schema, licences are SPDX")


def spdx(rel, expression):
    """Packages take their License tags from these fields, so they must be
    exact SPDX expressions ("LGPL-2.0-or-later", not "LGPL")."""
    from license_expression import get_spdx_licensing
    errors = get_spdx_licensing().validate(expression).errors if expression else ["empty"]
    if errors:
        fail(f"{rel}: licence {expression!r} is not an SPDX expression: {errors[0]}")


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
    status = ("ForegroundLink", "ForegroundVisited", "ForegroundNegative", "ForegroundNeutral",
              "ForegroundPositive", "ForegroundActive")
    # WCAG 2.2: 4.5:1 for text (7:1 for body text here), 3:1 for focus rings
    # and for the selection against the lists and windows it sits in
    for group in ("Window", "View", "Button", "Header", "Tooltip", "Complementary", "Selection"):
        bg = get(group, "BackgroundNormal")
        rules = [("ForegroundNormal", 4.5 if group == "Selection" else 7.0), ("ForegroundInactive", 4.5)]
        rules += [(k, 4.5) for k in status] + [("DecorationFocus", 3.0)]
        for key, need in rules:
            c = contrast(get(group, key), bg)
            worst[key] = min(worst.get(key, 99), c)
            if c < need:
                fail(f"contrast {group}/{key} {c:.2f}:1 < {need}:1")
    selection = get("Selection", "BackgroundNormal")
    for group in ("View", "Window"):
        c = contrast(selection, get(group, "BackgroundNormal"))
        worst["Selection"] = min(worst.get("Selection", 99), c)
        if c < 3.0:
            fail(f"contrast Selection against {group} {c:.2f}:1 < 3:1")
    ok("contrast: " + ", ".join(f"{k.removeprefix('Foreground')} {v:.1f}" for k, v in worst.items()))


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
    # A picture for every common screen shape, and 4K where one picture fills any screen
    shapes = {"16:9": 16 / 9, "16:10": 16 / 10, "3:2": 3 / 2, "21:9": 43 / 18, "32:9": 32 / 9,
              "4:3": 4 / 3, "5:4": 5 / 4, "portrait 9:16": 9 / 16}
    sizes = [tuple(int(v) for v in f.stem.split("x")) for f in (wall / "images_dark").glob("*.jpg")]
    for name, ratio in shapes.items():
        if not any(abs(w / h - ratio) < 0.02 for w, h in sizes):
            fail(f"wallpaper has no {name} size")
    if max(w for w, h in sizes) < 5120:
        fail("wallpaper has no 5K size")
    big = {"zoomed wallpaper": USER / "backgrounds/openSUSEhalloween/night.jpg",
           "login background": SYSTEM / "sddm/breeze-openSUSE-halloween/background.jpg",
           "splash backdrop": LNF / "splash/images/background.jpg"}
    for name, f in big.items():
        if f.exists() and Image.open(f).width < 3840:
            fail(f"{name} {f.relative_to(BUILD)} is narrower than 4K")
    plymouth = SYSTEM / "plymouth/openSUSE-halloween"
    if dir_size(plymouth) > 600_000:
        fail(f"{plymouth.relative_to(BUILD)} is {dir_size(plymouth) / 1e3:.0f} kB (> 600 kB)")
    for f in ("throbber-0001.png", "throbber-0040.png", "watermark.png", "entry.png", "bullet.png", "lock.png"):
        if not (plymouth / f).exists():
            fail(f"plymouth {f} missing")
    ok(f"images: wallpapers for {len(shapes)} screen shapes up to 5K, 4K backgrounds, "
       f"plymouth {dir_size(plymouth) / 1e3:.0f} kB")


def check_look_and_feel():
    expected = {"previews/preview.png": (600, 337), "previews/fullscreenpreview.jpg": (1920, 1080),
                "previews/lockscreen.png": (600, 337), "previews/splash.png": (300, 169)}
    for rel, size in expected.items():
        f = LNF / rel
        if not f.exists() or Image.open(f).size != size:
            fail(f"look-and-feel {rel} missing or not {size}")
    if dir_size(LNF / "splash") > 1_000_000:
        fail(f"look-and-feel splash is {dir_size(LNF / 'splash') / 1e3:.0f} kB (> 1000 kB)")
    ok(f"look-and-feel: previews, splash {dir_size(LNF / 'splash') / 1e3:.0f} kB")


def check_plymouth_colours():
    """The pinned dialog images are recoloured from the palette: no blue left
    (the password prompt was the only blue between boot and login)."""
    theme = SYSTEM / "plymouth/openSUSE-halloween"
    for name in ("entry", "lock", "bullet", "keyboard", "capslock"):
        px = Image.open(theme / f"{name}.png").convert("RGBA").tobytes()
        blue = sum(1 for i in range(0, len(px), 4)
                   if px[i + 3] > 128 and px[i + 2] > px[i] + 40 and px[i + 2] > px[i + 1] + 20)
        if blue:
            fail(f"plymouth {name}.png: {blue} blue pixels; recolour it from the palette")
    # two-step plays an end animation in every mode that doesn't turn it off,
    # and without animation-* frames it takes the throbber's (plugin.c)
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string((theme / "openSUSE-halloween.plymouth").read_text())
    for mode in ("boot-up", "shutdown", "reboot", "updates", "system-upgrade", "firmware-upgrade", "system-reset"):
        if cp.get(mode, "UseEndAnimation", fallback="true").lower() != "false":
            fail(f"plymouth [{mode}] doesn't set UseEndAnimation=false")
    if list(theme.glob("animation-*.png")):
        fail("plymouth ships animation-*.png, which no mode plays")
    ok("plymouth colours: dialog images from the palette")


def check_plymouth_layout():
    """two-step places each image at alignment x (screen - image). The chameleon
    stays on screen during a passphrase prompt (the lantern stops), so the prompt
    and the update title must clear it, and the lantern must too, at common sizes."""
    theme = SYSTEM / "plymouth/openSUSE-halloween"
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string((theme / "openSUSE-halloween.plymouth").read_text())
    s = {k.lower(): v for k, v in cp["two-step"].items()}
    size = {n: Image.open(theme / f"{n}.png").size for n in ("watermark", "entry", "throbber-0001")}

    def box(name, h_key, v_key, sw, sh, pad=0, centred=False):
        w, h = size[name]
        if centred:     # the animation is centred on the alignment point (plugin.c)
            x, y = float(s[h_key]) * sw - w / 2, float(s[v_key]) * sh - h / 2
        else:
            x, y = (sw - w) * float(s[h_key]), (sh - h) * float(s[v_key])
        return (x - pad, y - pad, x + w + pad, y + h + pad)

    def overlap(a, b):
        return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

    for sw, sh in ((1280, 720), (1024, 768), (1366, 768), (1920, 1080), (2560, 1440), (3840, 2160), (1080, 1920)):
        chameleon = box("watermark", "watermarkhorizontalalignment", "watermarkverticalalignment", sw, sh)
        # The entry with the prompt text and lock icon around it
        prompt = box("entry", "dialoghorizontalalignment", "dialogverticalalignment", sw, sh, pad=30)
        lantern = box("throbber-0001", "horizontalalignment", "verticalalignment", sw, sh, centred=True)
        title_y = (sh - 80) * float(s["titleverticalalignment"])
        title = (0, title_y, sw, title_y + 80)
        for name, other in (("passphrase prompt", prompt), ("lantern", lantern), ("update title", title)):
            if overlap(chameleon, other):
                fail(f"plymouth at {sw}x{sh}: the {name} overlaps the chameleon")
        if prompt[3] > sh:
            fail(f"plymouth at {sw}x{sh}: the passphrase prompt runs off the screen")
    ok("plymouth layout: the prompt, lantern and title clear the chameleon from 720p to 4K and portrait")


def login_label_contrast(path):
    """Worst contrast of the login screen's action labels (cream at the 0.85
    opacity KDE's ActionButton uses) over the band of the background they sit
    on, blurred as SDDM blurs it while the login form shows."""
    cream = rgb(load_palette()["cream"])
    img = Image.open(path).convert("RGB").resize((1920, 1200), Image.LANCZOS).filter(ImageFilter.GaussianBlur(25))
    band = img.crop((660, 900, 1260, 1000)).resize((60, 10))
    worst = 99
    for y in range(band.height):
        for x in range(band.width):
            bg = band.getpixel((x, y))
            worst = min(worst, contrast(tuple(round(0.85 * c + 0.15 * b) for c, b in zip(cream, bg, strict=True)), bg))
    return worst


def check_sddm():
    """The login theme links breeze-openSUSE's QML and points at its own background."""
    from targets import sddm
    theme = SYSTEM / "sddm" / sddm.ID
    for name in sddm.BASE_FILES:
        link = theme / name
        if not link.is_symlink() or str(link.readlink()) != f"../{sddm.BASE}/{name}":
            fail(f"sddm {name} is not a link to ../{sddm.BASE}/{name}")
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string((theme / "theme.conf").read_text())
    background = cp.get("General", "background", fallback="")
    if background != f"{sddm.INSTALL_DIR}/background.jpg" or not (theme / "background.jpg").exists():
        fail(f"sddm theme.conf background {background!r} is not the theme's own background.jpg")
    labels = login_label_contrast(theme / "background.jpg")
    if labels < 4.5:
        fail(f"sddm: the power action labels are {labels:.2f}:1 over the background (< 4.5:1)")
    ok(f"sddm: {len(sddm.BASE_FILES)} links to {sddm.BASE}, own background, action labels {labels:.1f}:1")


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
    if (STYLE / "colors").exists():
        fail("plasma style has a colors file: it would override the user's colour scheme, high contrast included")
    ok(f"plasma style: {n} SVGs keep every Breeze element ID")


def icon_dirs(icons):
    """The directories index.theme lists, as {path: section}."""
    cp = configparser.ConfigParser(strict=False, interpolation=None)
    cp.optionxform = str
    cp.read_string((icons / "index.theme").read_text())
    theme = cp["Icon Theme"]
    listed = [d.strip() for key in ("Directories", "ScaledDirectories")
              for d in theme.get(key, "").split(",") if d.strip()]
    dirs = {}
    for d in listed:
        if d not in cp or not {"Size", "Type"} <= set(cp[d]):
            fail(f"icons index.theme: [{d}] is missing or has no Size and Type")
        elif not (icons / d).is_dir():
            fail(f"icons index.theme lists {d}, which has no icons")
        else:
            dirs[d] = cp[d]
    return dirs


# Icon names the desktops show in plain sight that the theme must draw, one
# colour (they are actions and panel buttons), with where each is asked for
ONE_COLOUR_SEEN = {
    "go-home": "Thunar's side pane, Home (thunar-shortcuts-model.c); Dolphin's Home button",
    "org.xfce.panel.showdesktop": "the Xfce panel's show desktop button (xfce4-panel)",
}

# GTK reads one-colour icons with a small parser of its own (tools/upstream.toml,
# [references] gtk-symbolic-parser: gtk/gdktextureutils.c, start_element_cb)
# and falls back to its full SVG renderer when it can't. It sees tags as GMarkup
# does, prefixes and all; it skips the tags below, so a transform on a <g> would
# be lost and the shapes inside a <defs> drawn, and it rejects any attribute on
# a shape, or any value, that it doesn't know.
GTK_SKIPPED = {"g", "defs", "style", "metadata"}
GTK_SKIPPED_PREFIXES = ("sodipodi:", "inkscape:", "rdf:", "cc:", "dc:")
GTK_SHAPE_ATTRS = {"class", "opacity", "visibility", "fill-rule", "fill-opacity", "stroke-width", "stroke-opacity",
                   "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-dasharray",
                   "stroke-dashoffset", "fill", "stroke", "style", "id", "color", "overflow", "d", "x", "y",
                   "width", "height", "rx", "ry", "cx", "cy", "r"}
GTK_NUMBERS = {"opacity", "fill-opacity", "stroke-opacity", "stroke-width", "stroke-miterlimit", "stroke-dashoffset",
               "x", "y", "width", "height", "rx", "ry", "cx", "cy", "r"}
GTK_CHOICES = {"stroke-linecap": {"butt", "round", "square"}, "stroke-linejoin": {"miter", "round", "bevel"}}


def number(text, unit=""):
    """The value of a number as GTK reads it (g_ascii_strtod, nothing after it), or None."""
    try:
        return float(text.removesuffix(unit)) if text.strip() == text else None
    except ValueError:
        return None


def gtk_fast_symbolic(text, size):
    """Why GTK's own parser would turn this one-colour icon down, or None."""
    inside = []
    for close, tag, attrs, empty in re.findall(
            r"<(/?)([A-Za-z_][\w.:-]*)((?:\s+[\w.:-]+\s*=\s*(?:\"[^\"]*\"|'[^']*'))*)\s*(/?)>", text):
        if close:
            inside.pop()
            continue
        if not empty:
            inside.append(tag)
        a = {k: v or w for k, v, w in re.findall(r"([\w.:-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", attrs)}
        if "transform" in a:
            return f"a transform on <{tag}>"
        if tag == "svg":
            w, h = (number(a.get(k, ""), "px") for k in ("width", "height"))
            if (w, h) != (size, size):
                return f"width and height should be {size}, not {a.get('width')} and {a.get('height')}"
            box = a.get("viewBox", "").split(" ")
            if "viewBox" in a and len(box) == 4 and [number(n) for n in box] != [0, 0, w, h]:
                return f"viewBox {a['viewBox']!r} is not 0 0 {size} {size}"
        elif tag in GTK_SKIPPED or tag.startswith(GTK_SKIPPED_PREFIXES):
            continue
        elif tag not in ("path", "rect", "circle"):
            return f"<{tag}>, which GTK's parser doesn't draw"
        elif "defs" in inside:
            return f"a <{tag}> inside <defs>, which GTK draws and other renderers don't"
        elif extra := {k for k in a if not k.startswith("gpa:")} - GTK_SHAPE_ATTRS:
            return f"<{tag}> has {', '.join(sorted(extra))}"
        else:
            for k, v in a.items():
                if (k in GTK_NUMBERS and number(v) is None or k in GTK_CHOICES and v not in GTK_CHOICES[k]
                        or k == "stroke-dasharray" and v != "none"
                        and None in [number(n) for n in re.split(r"[, ]", v) if n]):
                    return f"<{tag}> {k}={v!r}, which GTK can't read"
    return None


def check_icons():
    from targets.icons import ADWAITA_ID
    adwaita = USER / "icons" / ADWAITA_ID
    adwaita_dirs = icon_dirs(adwaita)
    for f in adwaita.iterdir():
        if f.is_symlink() and not f.exists():
            fail(f"icons {ADWAITA_ID}/{f.name}: broken symlink")
    if "Adwaita" not in (adwaita / "index.theme").read_text():
        fail(f"icons {ADWAITA_ID} doesn't inherit Adwaita")
    icons = USER / "icons/openSUSE-halloween"
    dirs = icon_dirs(icons)
    # the same folders, but for kde/, Plasma's links to Breeze Dark
    if set(adwaita_dirs) != set(dirs) - {"kde"}:
        fail(f"icons {ADWAITA_ID} lists other directories than openSUSE-halloween (kde/ aside)")
    # kde/ links to Breeze Dark's own icons, which aren't here: check_kde_lookup() checks them
    for f in icons.rglob("*"):
        if f.is_symlink() and not f.exists() and f.parent.name != "kde":
            fail(f"icon {f.relative_to(icons)}: broken symlink")
    n = 0
    for f in sorted(icons.rglob("*.svg")):
        rel = f.relative_to(icons)
        if rel.parts[0] == "kde":
            continue
        # Reverse-DNS app IDs keep their capitals (org.gnome.Nautilus)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*\.svg", f.name):
            fail(f"icon {rel}: name has characters other than letters, digits and ._+-")
        section = dirs.get(str(rel.parent))
        if section is None:
            fail(f"icon {rel}: its directory isn't listed in index.theme")
        text = f.read_text()
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            fail(f"icon {rel}: {e}")
            continue
        box = (root.get("viewBox") or "").split()
        if len(box) != 4 or box[0:2] != ["0", "0"] or box[2] != box[3] or not box[2].isdigit():
            fail(f"icon {rel}: viewBox {root.get('viewBox')!r} is not 0 0 N N")
        elif section is not None and section["Type"] == "Fixed" and box[2] != section["Size"]:
            fail(f"icon {rel}: {box[2]} px in a {section['Size']} px directory")
        if f.stat().st_size > 60_000:
            fail(f"icon {rel}: {f.stat().st_size / 1e3:.0f} kB (> 60 kB)")
        if re.search(r"<(\w+:)?(text|script|image)\b", text) or re.search(r'href="(https?:|file:)', text):
            fail(f"icon {rel}: contains text, script, raster images or external links")
        # Qt resolves currentColor where fill is set: without the class there, the glyph turns black
        for el in root.iter():
            if el.get("fill") == "currentColor" and "ColorScheme-Text" not in (el.get("class") or "").split():
                fail(f"icon {rel}: fill=currentColor on a <{el.tag.split('}')[-1]}> without class ColorScheme-Text")
                break
        if f.name.endswith("-symbolic.svg") or "ColorScheme-Text" in text:
            if problem := gtk_fast_symbolic(text, 16):
                fail(f"icon {rel}: one colour, but GTK can't read it directly: {problem}")
        n += 1
    # The Icon Theme Specification's Example key: the icon that stands for the theme
    for theme in (icons, adwaita):
        example = re.search(r"^Example=(.+)$", (theme / "index.theme").read_text(), re.M)
        if not example or not list(theme.glob(f"*/*/{example.group(1)}.svg")):
            fail(f"icons {theme.name}: index.theme has no Example= naming one of its icons")
    for name, where in ONE_COLOUR_SEEN.items():
        found = [f for f in icons.glob(f"*/*/{name}.svg")]
        if not found:
            fail(f"icon {name} is missing: {where} shows a stock icon")
        elif "ColorScheme-Text" not in found[0].read_text():
            fail(f"icon {name} should be one colour: {where}")
    ok(f"icons: {n} SVGs in the {len(dirs)} directories index.theme lists")


def check_hinting():
    """The one-colour glyphs are snapped to the 16 px grid edge by edge
    (vectors.grid_warp). Moving every edge to its nearest pixel can double one
    key of the keyboard and halve the next, so six keys read as four marks:
    the gap between any two neighbouring level edges may change by at most
    vectors.HINT_MAX_STRETCH."""
    import vectors
    bad, n = [], 0
    for master in sorted({*vectors.SYMBOLIC, *vectors.GNOME_SETTINGS, *vectors.SETTINGS}):
        shapes = vectors.load(master)
        if not shapes:
            continue
        n += 1
        outlines = vectors.glyph_outlines(shapes)
        every = [c for o in outlines for c in o]
        for axis, warp in enumerate(vectors.grid_warps(outlines)):
            edges = sorted({p for p, _ in vectors.level_edges(every, axis)})
            for a, b in itertools.pairwise(edges):
                change = (warp(b) - warp(a)) - (b - a)
                if abs(change) > vectors.HINT_MAX_STRETCH + 1e-9:
                    bad.append((abs(change), f"{master}: the gap at {'xy'[axis]} {a:.2f}-{b:.2f} px goes from "
                                             f"{b - a:.2f} to {b - a + change:.2f} px"))
    for _, text in sorted(bad, reverse=True)[:5]:
        fail(f"hinting: {text}")
    if bad:
        fail(f"hinting: {len(bad)} gaps between edges change by more than {vectors.HINT_MAX_STRETCH} px")
        return
    ok(f"hinting: {n} glyphs on the 16 px grid, no gap between edges changed by more than "
       f"{vectors.HINT_MAX_STRETCH} px")


def header_svg_image(text):
    """(the header SVG drawn at its 1x size, the picture inside it), drawn as
    tools/targets/firefox.py composes it: the embedded JPEG under a horizontal
    gradient mask whose grey stops are each column's opacity."""
    ns = {"svg": "http://www.w3.org/2000/svg"}
    root = ET.fromstring(text)
    w, h = (round(float(root.get(k) or root.get("viewBox").split()[i])) for k, i in (("width", 2), ("height", 3)))
    data = text.split("data:image/jpeg;base64,", 1)[1].split('"', 1)[0]
    inner = Image.open(io.BytesIO(base64.b64decode(data)))
    stops = [(float(s.get("offset")), int(s.get("stop-color")[1:3], 16)) for s in root.iterfind(".//svg:stop", ns)]
    alpha = []
    for x in range(w):
        at = x / (w - 1)
        (o0, a0), (o1, a1) = next(((s, e) for s, e in zip(stops, stops[1:], strict=False) if s[0] <= at <= e[0]),
                                  (stops[-1], stops[-1]))
        alpha.append(round(a0 + (a1 - a0) * ((at - o0) / (o1 - o0) if o1 > o0 else 0)))
    img = inner.convert("RGB").resize((w, h), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (w, 1))
    mask.putdata(alpha)
    img.putalpha(mask.resize((w, h)))
    return img, inner


def check_kde_lookup():
    """Plasma takes an icon from the first theme that has its name or a
    shortened one (tools/kde_lookup.py): every Breeze icon that would land on
    one of ours must be ours on purpose, or linked to Breeze's own."""
    import kde_lookup
    icons = USER / "icons/openSUSE-halloween"
    if not icons.exists():
        return
    files = [f for f in icons.rglob("*") if f.suffix in (".svg", ".png")]
    ours = {f.stem for f in files}
    one_colour = {f.stem for f in files if not f.is_symlink() and f.suffix == ".svg"
                  and "ColorScheme-Text" in f.read_text()}
    breeze = kde_lookup.breeze()
    wrong = sorted((name, hit) for name in breeze if name not in ours
                   for hit in [kde_lookup.first_hit(name, ours)]
                   if hit and not kde_lookup.wanted(name, hit, one_colour))
    for name, hit in wrong[:5]:
        fail(f"icons: Plasma shows our {hit} for Breeze's {name}")
    if wrong:
        fail(f"icons: {len(wrong)} Breeze icons in all would show ours; link them to Breeze's (kde_lookup.plan)")
    links = [f for f in files if f.is_symlink()]
    pinned = {"../../breeze-dark/" + path for path in breeze.values()}
    for f in links:
        target = os.readlink(f)
        if target not in pinned:
            fail(f"icon {f.relative_to(icons)} links to {target}, not to a pinned Breeze icon")
    ok(f"icons: Plasma's lookup of {len(breeze)} Breeze names finds ours only where meant; {len(links)} left to Breeze")


def check_firefox():
    theme = FIREFOX / "openSUSE-halloween"
    try:
        manifest = json.loads((theme / "manifest.json").read_text())
        colors, images = manifest["theme"]["colors"], manifest["theme"]["images"]["additional_backgrounds"]
    except (OSError, ValueError, KeyError) as e:
        fail(f"firefox manifest.json: {e!r}")
        return
    # YEAR.MONTH.PATCH; Firefox rejects version parts with leading zeros
    if not re.fullmatch(r"20\d\d\.(?:[1-9]|1[0-2])\.(?:0|[1-9]\d*)", VERSION):
        fail(f"VERSION {VERSION} is not YEAR.MONTH.PATCH without leading zeros")
    if manifest.get("version") != VERSION:
        fail(f"firefox version {manifest.get('version')} is not {VERSION}")
    if manifest.get("browser_specific_settings", {}).get("gecko", {}).get("id") != FIREFOX_ID:
        fail(f"firefox add-on ID is not {FIREFOX_ID}")

    # Text on its background: (text, background, minimum)
    pairs = [("tab_text", "tab_selected", 4.5), ("tab_text", "toolbar", 4.5),
             ("tab_background_text", "frame", 4.5), ("tab_background_text", "frame_inactive", 4.5),
             ("toolbar_text", "toolbar", 4.5), ("icons", "toolbar", 3.0),
             ("toolbar_field_text", "toolbar_field", 4.5), ("toolbar_field_text_focus", "toolbar_field_focus", 4.5),
             ("toolbar_field_highlight_text", "toolbar_field_highlight", 4.5), ("popup_text", "popup", 4.5),
             ("popup_highlight_text", "popup_highlight", 4.5), ("sidebar_text", "sidebar", 4.5),
             ("sidebar_highlight_text", "sidebar_highlight", 4.5), ("ntp_text", "ntp_background", 4.5),
             ("ntp_text", "ntp_card_background", 4.5),
             # the address bar's edge and focus ring are what show where it is
             ("toolbar_field_border", "toolbar", 3.0), ("toolbar_field_border_focus", "toolbar", 3.0)]
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
        if f.suffix == ".svg":
            text = f.read_text()
            if "data:image/jpeg" not in text or 'href="http' in text:
                fail(f"firefox {name} should embed its picture, not link to it")
                continue
            img, inner = header_svg_image(text)
            if inner.width < 2 * img.width:
                fail(f"firefox {name}: its picture is {inner.width} px for {img.width} px, not 2x (HiDPI)")
        else:
            img = Image.open(f)
        if img.height > 200 or f.stat().st_size > 600_000:
            fail(f"firefox {name} is {img.width}x{img.height}, {f.stat().st_size / 1e3:.0f} kB (> 200 px or 600 kB)")
        # Background tab titles over the image: every tab-sized patch of the
        # 44 px tab strip, with the frame colour showing through
        over = Image.new("RGBA", img.size, rgb(colors["frame"]) + (255,))
        over.alpha_composite(img.convert("RGBA"))
        strip = over.convert("RGB").crop((0, 0, img.width, 44))
        def average(x, strip=strip):
            return strip.crop((x, 0, x + 100, 44)).resize((1, 1), Image.BOX).getpixel((0, 0))
        title = min(contrast(colors["tab_background_text"], average(x)) for x in range(0, img.width - 99, 10))
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


# Common screens: (width, height, minimum share of the chameleon box Plasma
# shows, minimum share GNOME, Xfce and SDDM show with their one zoomed picture)
SCREENS = {
    "1920x1080": (1920, 1080, 1.0, 1.0), "2560x1440": (2560, 1440, 1.0, 1.0),
    "3840x2160": (3840, 2160, 1.0, 1.0), "1366x768": (1366, 768, 1.0, 1.0),
    "5120x2880": (5120, 2880, 1.0, 1.0), "1920x1200": (1920, 1200, 1.0, 1.0),
    "2560x1600": (2560, 1600, 1.0, 1.0), "1280x800": (1280, 800, 1.0, 1.0),
    "2256x1504": (2256, 1504, 1.0, 1.0), "3000x2000": (3000, 2000, 1.0, 1.0),
    "3440x1440": (3440, 1440, 1.0, 0.9), "2560x1080": (2560, 1080, 1.0, 0.9),
    "1600x1200": (1600, 1200, 1.0, 0.85), "1280x1024": (1280, 1024, 1.0, 0.8),
    "5120x1440": (5120, 1440, 0.7, 0.5), "1080x1920": (1080, 1920, 0.85, 0.0),
}


def check_resolutions():
    """How much of the chameleon (art/crops.toml [night] keep) each desktop
    shows on common screens: Plasma picks a size from the wallpaper package and
    zooms it; GNOME, Xfce and SDDM zoom their one 16:10 picture."""
    from imaging import CROPS, keep_window
    from targets.wallpapers import SIZES, ZOOMED
    try:
        W, H = Image.open(ROOT / "art/source/wallpaper-night.png").size
    except OSError:
        print("skip  resolutions (no wallpaper master)")
        return
    c = CROPS["night"]
    keep = (c["keep"][0] * W, c["keep"][1] * H, c["keep"][2] * W, c["keep"][3] * H)

    def zoomed(box, ratio):
        """The centred part of `box` a screen of `ratio` shows when the picture fills it."""
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        if w / h > ratio:
            cut = (w - h * ratio) / 2
            return (x0 + cut, y0, x1 - cut, y1)
        cut = (h - w / ratio) / 2
        return (x0, y0 + cut, x1, y1 - cut)

    def shown(box):
        iw = max(0, min(box[2], keep[2]) - max(box[0], keep[0]))
        ih = max(0, min(box[3], keep[3]) - max(box[1], keep[1]))
        return iw * ih / ((keep[2] - keep[0]) * (keep[3] - keep[1]))

    def picture(w, h, zoomed=False):
        return keep_window((W, H), w / h, c["keep"], c["focus"], zoomed)

    def plasma_pick(sw, sh):
        # Plasma's own choice (plasma-workspace, image wallpaper's distance()):
        # the closest aspect ratio first, then the closest width, upscaling
        # counting double
        def distance(size):
            delta = size[0] - sw
            return abs(size[0] / size[1] - sw / sh) * 25000 + (delta if delta >= 0 else -2 * delta)
        return min(SIZES, key=distance)

    worst = {"plasma": 1.0, "zoomed": 1.0}
    for name, (sw, sh, need_plasma, need_zoomed) in SCREENS.items():
        plasma = shown(zoomed(picture(*plasma_pick(sw, sh)), sw / sh))
        one = shown(zoomed(picture(*ZOOMED, zoomed=True), sw / sh))
        worst = {"plasma": min(worst["plasma"], plasma), "zoomed": min(worst["zoomed"], one)}
        if plasma < need_plasma - 0.005:
            fail(f"resolution {name}: Plasma shows {plasma:.0%} of the chameleon (< {need_plasma:.0%})")
        if one < need_zoomed - 0.005:
            fail(f"resolution {name}: GNOME, Xfce and SDDM show {one:.0%} of the chameleon (< {need_zoomed:.0%})")
    ok(f"resolutions: {len(SCREENS)} screens, chameleon at least {worst['plasma']:.0%} on Plasma, "
       f"{worst['zoomed']:.0%} with one zoomed picture")


def css_colours(text):
    return dict(re.findall(r"@define-color\s+([a-z_0-9]+)\s+([^;]+);", text))


def check_gtk():
    """Every colour we set is one adw-gtk3 defines, and text stays readable."""
    from targets.gtk import FOCUS, ID
    css = (THEMES / ID / "gtk-3.0/gtk.css").read_text()
    upstream, ours = css.split("openSUSE Halloween: appended", 1)
    ours = css_colours(ours)
    unknown = sorted(set(ours) - set(css_colours(upstream)))
    if unknown:
        fail(f"gtk theme sets colours adw-gtk3 doesn't define: {unknown}")
    pairs = [("window_fg_color", "window_bg_color", 7.0), ("view_fg_color", "view_bg_color", 7.0),
             ("headerbar_fg_color", "headerbar_bg_color", 7.0), ("sidebar_fg_color", "sidebar_bg_color", 7.0),
             ("popover_fg_color", "popover_bg_color", 4.5), ("dialog_fg_color", "dialog_bg_color", 4.5),
             ("accent_fg_color", "accent_bg_color", 4.5), ("accent_color", "window_bg_color", 4.5),
             ("accent_color", "view_bg_color", 3.0), ("accent_color", "popover_bg_color", 3.0)]
    # Status colours as text on every surface, and behind their own text
    for status in ("success", "warning", "error", "destructive"):
        pairs += [(f"{status}_color", f"{bg}_bg_color", 4.5) for bg in ("window", "view", "headerbar", "popover",
                                                                          "dialog", "sidebar")]
        pairs.append((f"{status}_fg_color", f"{status}_bg_color", 4.5))
    worst = 99
    for fg, bg, need in pairs:
        if fg not in ours or bg not in ours:
            fail(f"gtk theme doesn't set {fg if fg not in ours else bg}")
            continue
        c = contrast(ours[fg], ours[bg])
        worst = min(worst, c)
        if c < need:
            fail(f"gtk contrast {fg} on {bg} {c:.2f}:1 < {need}:1")
    # Half-transparent pumpkin rings are below 3:1 (tools/targets/gtk.py draws them solid)
    if FOCUS in upstream:
        fail(f"gtk theme still draws focus with {FOCUS}")
    obsolete = re.findall(r"^(MetacityTheme|Encoding)=", (THEMES / ID / "index.theme").read_text(), re.M)
    if obsolete:
        fail(f"gtk theme index.theme has obsolete keys: {obsolete}")
    for f in ("gtk-dark.css", "assets/check-symbolic.svg"):
        if not (THEMES / ID / "gtk-3.0" / f).exists():
            fail(f"gtk theme lacks gtk-3.0/{f}")
    ok(f"gtk theme: {len(ours)} adw-gtk3 colours set, worst contrast {worst:.1f}")


def check_xfwm4():
    """Each scale has every image its themerc needs and sets every colour they use."""
    from targets.gtk import ID
    from targets.xfce import SCALES
    parts = ["top-left", "top-right", "left", "right", "bottom", "bottom-left", "bottom-right",
             *(f"title-{i}" for i in range(1, 6))]
    buttons = ["close", "hide", "maximize", "maximize-toggled", "menu", "shade", "shade-toggled",
               "stick", "stick-toggled"]
    need = [f"{p}-{s}" for p in parts for s in ("active", "inactive")]
    need += [f"{b}-{s}" for b in buttons for s in ("active", "inactive", "prelight", "pressed")]
    for suffix in SCALES:
        wm = THEMES / f"{ID}{suffix}/xfwm4"
        rc = dict(line.split("=", 1) for line in (wm / "themerc").read_text().splitlines() if "=" in line)
        missing = [n for n in need if not (wm / f"{n}.xpm").exists()]
        if missing:
            fail(f"xfwm4 {ID}{suffix} lacks {missing[:4]}")
        symbols = {s for f in wm.glob("*.xpm") for s in re.findall(r" s ([a-z_0-9]+)\"", f.read_text())}
        unset = sorted(s for s in symbols if s not in rc)
        if unset:
            fail(f"xfwm4 {ID}{suffix} themerc doesn't set {unset}")
        if not re.fullmatch(r"#[0-9A-F]{6}", rc.get("active_color_2", "")):
            fail(f"xfwm4 {ID}{suffix} active_color_2 isn't a palette colour")
    ok(f"xfwm4: {len(SCALES)} scales, {len(need)} images each, every colour set")


def check_gnome():
    """The wallpaper entry and the defaults point at files the build installs."""
    from targets import gnome
    for path in (gnome.LIGHT, gnome.DARK):
        built = USER / Path(path).relative_to("/usr/share")
        if not built.exists():
            fail(f"gnome wallpaper {path} isn't built")
    xml = ET.parse(USER / "gnome-background-properties/openSUSEhalloween.xml")
    if xml.findtext("wallpaper/filename-dark") != gnome.DARK:
        fail("gnome background XML has no dark picture")
    shell = THEMES / "openSUSE-halloween/gnome-shell/gnome-shell.css"
    if not shell.exists():
        fail("gnome shell theme missing")
    else:
        # St knows rgba(), st-transparentize(), st-mix() and the accent; it drops
        # a declaration with GTK's colour functions without a word
        css = re.sub(r"/\*.*?\*/", "", shell.read_text(), flags=re.S)
        gtk_only = sorted(set(re.findall(r"(?<![\w-])(alpha|mix|shade|lighter|darker)\(", css)))
        if gtk_only:
            fail(f"gnome shell theme uses GTK colour functions St ignores: {gtk_only}")
    for f in (BUILD / "defaults/glib-2.0/schemas").iterdir():
        cp = configparser.ConfigParser(interpolation=None)
        try:
            cp.read_string(f.read_text())
        except configparser.Error as e:
            fail(f"{f.relative_to(BUILD)}: {e}")
    # IBus draws the keyboard layout ("EN") in the panel itself, in this colour;
    # its default is blue
    cp = configparser.ConfigParser(interpolation=None)
    cp.read_string((BUILD / "defaults/glib-2.0/schemas/30_openSUSE-halloween.gschema.override").read_text())
    ibus = cp.get("org.freedesktop.ibus.panel", "xkb-icon-rgba", fallback="").strip("'")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", ibus):
        fail("gnome defaults don't set IBus's layout colour (org.freedesktop.ibus.panel xkb-icon-rgba)")
    elif contrast(rgb(ibus), rgb(load_palette()["night"])) < 4.5:
        fail(f"IBus's layout colour {ibus} is below 4.5:1 on the panel")
    ok("gnome: shell theme, wallpaper entry, gsettings and GDM defaults")


def check_manifest():
    """MANIFEST.sha256 covers every file install.py installs, so comparing
    manifests shows whether two builds ship the same."""
    listed = {line.split("  ", 1)[1].split(" -> ")[0] for line in (BUILD / "MANIFEST.sha256").read_text().splitlines()}
    shipped = set()
    for src, _ in [*install.FILES, *install.DEFAULTS]:
        path = BUILD / src
        files = [path] if path.is_file() else [f for f in path.rglob("*") if f.is_file() or f.is_symlink()]
        shipped |= {str(f.relative_to(BUILD)) for f in files}
    missing = sorted(shipped - listed)
    if missing:
        fail(f"MANIFEST.sha256 leaves out {len(missing)} installed files, such as {missing[0]}")
    ok(f"manifest: {len(listed)} files, every installed one")


def check_install():
    """Stage `make install` and `make install-defaults` and undo them again: the
    files land only under usr/ and etc/, and uninstalling leaves nothing behind."""
    with tempfile.TemporaryDirectory() as tmp:
        for extra in ([], ["--defaults"]):
            install.main(["--destdir", tmp, "--quiet", *extra])
        staged = sorted(p.relative_to(tmp) for p in Path(tmp).rglob("*") if not p.is_dir() or p.is_symlink())
        stray = [p for p in staged if p.parts[0] not in ("usr", "etc")]
        if stray:
            fail(f"install puts files outside usr/ and etc/: {stray[:3]}")
        need = ["usr/share/icons/openSUSE-halloween/index.theme",
                "usr/share/wallpapers/openSUSEhalloween/metadata.json",
                "usr/share/plymouth/themes/openSUSE-halloween/openSUSE-halloween.plymouth",
                f"usr/lib64/firefox/browser/extensions/{FIREFOX_ID}.xpi"]
        if (THEMES / "openSUSE-halloween").exists():
            need += ["usr/share/themes/openSUSE-halloween/gtk-3.0/gtk.css",
                     "usr/share/icons/openSUSE-halloween-adwaita/16x16/places"]
        if (USER / "gnome-background-properties").exists():
            need += ["usr/share/gnome-background-properties/openSUSEhalloween.xml",
                     "usr/share/glib-2.0/schemas/30_openSUSE-halloween.gschema.override"]
        if (SYSTEM / "sddm").exists():
            need += ["usr/share/sddm/themes/breeze-openSUSE-halloween/Main.qml",
                     "usr/lib/sddm/sddm.conf.d/30-breeze-openSUSE-halloween.conf"]
        missing = [n for n in need if not (Path(tmp) / n).is_symlink() and not (Path(tmp) / n).exists()]
        if missing:
            fail(f"install lacks {missing}")
        for extra in ([], ["--defaults"]):
            install.main(["--destdir", tmp, "--quiet", "--uninstall", *extra])
        left = [p.relative_to(tmp) for p in Path(tmp).rglob("*") if not p.is_dir() or p.is_symlink()]
        if left:
            fail(f"uninstall leaves {left[:3]}")
    # Under another prefix, the files that name our own files follow it
    with tempfile.TemporaryDirectory() as tmp:
        for extra in ([], ["--defaults"]):
            install.main(["--destdir", tmp, "--prefix", "/opt/halloween", "--quiet", *extra])
        stale = [p.relative_to(tmp) for p in Path(tmp).rglob("*")
                 if p.is_file() and not p.is_symlink() and p.suffix not in (".png", ".jpg", ".svg", ".xpm", ".xpi")
                 and b"/usr/share/" in p.read_bytes()]
        if stale:
            fail(f"install --prefix leaves /usr/share paths in {[str(s) for s in stale[:3]]}")
    ok(f"install: {len(staged)} files under usr/ and etc/, all removed again by uninstall")


def check_readme_images():
    """Every image the README shows exists, and every README image is shown."""
    readme = (ROOT / "README.md").read_text()
    shown = set(re.findall(r"docs/screenshots/([\w.-]+\.jpg)", readme))
    files = {f.name for f in (ROOT / "docs/screenshots").glob("*.jpg")}
    for name in sorted(shown - files):
        fail(f"README shows docs/screenshots/{name}, which doesn't exist")
    for name in sorted(files - shown):
        fail(f"docs/screenshots/{name} isn't shown in the README")
    ok(f"README: {len(shown)} screenshots, all there")


def check_reuse():
    reuse = shutil.which("reuse") or str(ROOT / "tools/.venv/bin/reuse")
    if not Path(reuse).exists():
        print("skip  reuse lint (reuse not installed)")
        return
    if (ROOT / ".git").exists():
        cmd, what = [reuse, "--root", str(ROOT), "lint"], "reuse lint"
    else:
        # From a release archive there is no git to ignore build/, which holds
        # the third-party files fetched for the build: lint the sources file by file
        files = [str(p) for p in sorted(ROOT.rglob("*"))
                 if p.is_file() and p.relative_to(ROOT).parts[0] not in ("build", "dist")
                 and ".venv" not in p.parts and "__pycache__" not in p.parts]
        cmd, what = [reuse, "--root", str(ROOT), "lint-file", *files], f"reuse lint-file ({len(files)} source files)"
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        fail(f"{what}:\n" + (r.stdout + r.stderr)[-2000:])
    else:
        ok(what)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--release", action="store_true", help="fail while placeholders are in use")
    args = ap.parse_args()
    if not USER.exists():
        sys.exit("build/ is empty: run tools/build.py first")
    desktops = json.loads((BUILD / "build-info.json").read_text()).get("desktops", [])
    check_syntax()
    check_metadata()
    check_images()
    check_plymouth_colours()
    check_plymouth_layout()
    check_icons()
    check_hinting()
    check_kde_lookup()
    check_firefox()
    if "plasma" in desktops:
        check_contrast()
        check_plasma_style()
        check_look_and_feel()
        check_sddm()
    if "gnome" in desktops or "xfce" in desktops:
        check_gtk()
    if "gnome" in desktops:
        check_gnome()
    if "xfce" in desktops:
        check_xfwm4()
    check_resolutions()
    check_manifest()
    check_install()
    check_readme_images()
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
