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
import configparser
import json
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
from PIL import Image

import install
from common import BUILD, CACHE, FIREFOX, FIREFOX_ID, ROOT, SYSTEM, USER, VERSION, contrast, fetch, rgb

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
        if f.suffix in (".json", ".qml", ".js", ".svg", ".sh", ".css", ".xml", *INI_SUFFIXES) or f.name in INI_NAMES:
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
    ok(f"metadata: {len(files)} metadata.json files match KDE's KPlugin schema")


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
    plymouth = SYSTEM / "plymouth/openSUSE-halloween"
    if dir_size(plymouth) > 600_000:
        fail(f"{plymouth.relative_to(BUILD)} is {dir_size(plymouth) / 1e3:.0f} kB (> 600 kB)")
    for f in ("throbber-0001.png", "throbber-0040.png", "watermark.png"):
        if not (plymouth / f).exists():
            fail(f"plymouth {f} missing")
    ok(f"images: wallpapers, plymouth {dir_size(plymouth) / 1e3:.0f} kB")


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
    ok(f"sddm: {len(sddm.BASE_FILES)} links to {sddm.BASE}, own background")


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
    if set(adwaita_dirs) != set(dirs):
        fail(f"icons {ADWAITA_ID} lists other directories than openSUSE-halloween")
    for f in icons.rglob("*"):
        if f.is_symlink() and not f.exists():
            fail(f"icon {f.relative_to(icons)}: broken symlink")
    n = 0
    for f in sorted(icons.rglob("*.svg")):
        rel = f.relative_to(icons)
        if not re.fullmatch(r"[a-z0-9][a-z0-9._+-]*\.svg", f.name):
            fail(f"icon {rel}: name has characters other than a-z, 0-9 and ._+-")
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
        n += 1
    ok(f"icons: {n} SVGs in the {len(dirs)} directories index.theme lists")


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
    pairs = [("tab_text", "tab_selected", 4.5), ("tab_text", "toolbar", 4.5),
             ("tab_background_text", "frame", 4.5), ("tab_background_text", "frame_inactive", 4.5),
             ("toolbar_text", "toolbar", 4.5), ("icons", "toolbar", 3.0),
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


def css_colours(text):
    return dict(re.findall(r"@define-color\s+([a-z_0-9]+)\s+([^;]+);", text))


def check_gtk():
    """Every colour we set is one adw-gtk3 defines, and text stays readable."""
    from targets.gtk import ID
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
             ("success_color", "window_bg_color", 4.5), ("warning_color", "window_bg_color", 4.5),
             ("error_color", "window_bg_color", 4.5)]
    worst = 99
    for fg, bg, need in pairs:
        c = contrast(ours[fg], ours[bg])
        worst = min(worst, c)
        if c < need:
            fail(f"gtk contrast {fg} on {bg} {c:.2f}:1 < {need}:1")
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
        built = USER / "wallpapers" / Path(path).relative_to("/usr/share/wallpapers")
        if not built.exists():
            fail(f"gnome wallpaper {path} isn't built")
    xml = ET.parse(USER / "gnome-background-properties/openSUSEhalloween.xml")
    if xml.findtext("wallpaper/filename-dark") != gnome.DARK:
        fail("gnome background XML has no dark picture")
    if not (THEMES / "openSUSE-halloween/gnome-shell/gnome-shell.css").exists():
        fail("gnome shell theme missing")
    for f in [*(BUILD / "defaults/dconf/db/gdm.d").iterdir(), *(BUILD / "defaults/glib-2.0/schemas").iterdir()]:
        cp = configparser.ConfigParser(interpolation=None)
        try:
            cp.read_string(f.read_text())
        except configparser.Error as e:
            fail(f"{f.relative_to(BUILD)}: {e}")
    ok("gnome: shell theme, wallpaper entry, gsettings and GDM defaults")


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
                     "usr/share/glib-2.0/schemas/30_openSUSE-halloween.gschema.override",
                     "etc/dconf/db/gdm.d/30-openSUSE-halloween"]
        if (SYSTEM / "sddm").exists():
            need += ["usr/share/sddm/themes/breeze-openSUSE-halloween/Main.qml",
                     "etc/sddm.conf.d/zz-openSUSE-halloween.conf"]
        missing = [n for n in need if not (Path(tmp) / n).is_symlink() and not (Path(tmp) / n).exists()]
        if missing:
            fail(f"install lacks {missing}")
        for extra in ([], ["--defaults"]):
            install.main(["--destdir", tmp, "--quiet", "--uninstall", *extra])
        left = [p.relative_to(tmp) for p in Path(tmp).rglob("*") if not p.is_dir() or p.is_symlink()]
        if left:
            fail(f"uninstall leaves {left[:3]}")
    ok(f"install: {len(staged)} files under usr/ and etc/, all removed again by uninstall")


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
    desktops = json.loads((BUILD / "build-info.json").read_text()).get("desktops", [])
    check_syntax()
    check_metadata()
    check_images()
    check_icons()
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
    check_install()
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
