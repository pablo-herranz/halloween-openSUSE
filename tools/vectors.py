# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Turn the Recraft SVG masters in art/source/vectors/ into icons and ornaments.

Recraft SVGs are a flat list of <path d fill="rgb()" transform="translate()">
on a 2048x2048 canvas, with a full-canvas white backdrop path first and C2PA
content credentials in <metadata>. This module reads them as (d, colour)
shapes, drops the backdrop, and recomposes them:

  - every folder icon is the master folder's body plus one emblem, so all
    folders share exactly the same shape; emblems are one-colour glyphs
    recoloured cream, their white details recoloured to the folder front;
  - other icons (trash, launcher) are cleaned and moved to a 64x64 viewBox;
  - ornaments for the Plasma style are cropped to their content.

Missing masters return None, so build.py falls back to placeholders.
"""
import re

from common import ROOT, contrast, rgb

MASTERS = ROOT / "art/source/vectors"
ICON_SIZE = 64

FOLDER_EMBLEMS = {
    "folder-documents": "emblem-scroll",
    "folder-download": "emblem-acorn",
    "folder-music": "emblem-note",
    "folder-pictures": "emblem-picture",
    "folder-videos": "emblem-reel",
    "folder-templates": "emblem-stencil",
    "folder-publicshare": "emblem-lantern",
    "user-home": "emblem-cottage",
    "user-desktop": "emblem-monitor",
    "folder-development": "glyph-wand",
    "folder-cloud": "glyph-cloud",
    "folder-recent": "glyph-hourglass",
    "folder-games": "glyph-gamepad",
    "folder-network": "glyph-web",
    "folder-remote": "glyph-web",
    "folder-image-people": "glyph-ghosts",
    "folder-favorites": "glyph-bookmark",
}
LAUNCHERS = ("start-here-kde-plasma", "start-here-kde", "start-here")
# Other names Breeze uses for the same places (symlinks in Breeze); without
# them those names fall through to Breeze Dark's versions.
ALIASES = {
    "folder-public": "folder-publicshare",
    "folder-downloads": "folder-download",
    "folder-video": "folder-videos",
    "folder-images": "folder-pictures",
    "folder-picture": "folder-pictures",
    "folder-desktop": "user-desktop",
    "user-bookmarks": "folder-favorites",
    "folder-drag-accept": "folder-open",
    "folder-visiting": "folder-open",
}
EMBLEM_SCALE = 1.12      # emblem size relative to the master's leaf

# Colour application icons: master -> the icon names apps ask for, on KDE,
# GNOME and Xfce alike (a file manager is the bat folder everywhere, a
# terminal the same terminal). Other projects' logos (Qt, the ArtCraft suite,
# btop) are left to their own themes, like the distribution logo. Web
# browsers, Firefox included, get an original browser icon, never a modified
# Firefox logo.
APPS = {
    "app-browser": ("web-browser", "internet-web-browser", "firefox", "firefox-esr", "org.mozilla.firefox",
                    "firefox-developer-edition", "firefox-nightly", "org.xfce.webbrowser"),
    "app-discover": ("plasmadiscover", "org.gnome.Software", "system-software-install"),
    "app-konsole": ("utilities-terminal", "utilities-terminal_su", "org.kde.konsole", "org.gnome.Console",
                    "org.gnome.Terminal", "org.xfce.terminal", "org.xfce.terminalemulator"),
    "app-settings": ("preferences-system", "systemsettings", "org.gnome.Settings", "org.xfce.settings.manager"),
    "app-kate": ("kate", "org.kde.kate", "kwrite", "org.kde.kwrite", "accessories-text-editor",
                 "org.gnome.TextEditor", "org.xfce.mousepad"),
    "app-spectacle": ("spectacle", "org.kde.spectacle", "org.gnome.Screenshot", "org.xfce.screenshooter"),
    "app-ark": ("ark", "org.kde.ark", "org.gnome.FileRoller", "file-roller"),
    "app-gwenview": ("gwenview", "org.kde.gwenview", "org.gnome.Loupe", "org.xfce.ristretto"),
    "app-help": ("help-browser", "khelpcenter", "org.kde.khelpcenter", "org.gnome.Yelp"),
    "app-infocenter": ("hwinfo", "org.kde.kinfocenter"),
    "app-kdeconnect": ("kdeconnect", "org.kde.kdeconnect.app"),
    "app-kwallet": ("kwalletmanager", "kwalletmanager2", "org.gnome.Seahorse", "seahorse"),
    "app-menuedit": ("kmenuedit", "menulibre"),
    "app-qrca": ("org.kde.qrca",),
    "app-skanpage": ("skanpage", "org.kde.skanpage", "skanlite", "org.kde.skanlite", "org.gnome.SimpleScan",
                     "simple-scan"),
    "app-sysmon": ("utilities-system-monitor", "org.kde.plasma-systemmonitor", "org.gnome.SystemMonitor",
                   "org.xfce.taskmanager"),
    "app-bug": ("tools-report-bug", "drkonqi"),
    "app-emoji": ("preferences-desktop-emoticons", "org.gnome.Characters", "accessories-character-map"),
    "app-bridge": ("org.kde.xwaylandvideobridge",),
    # GNOME's, Xfce's and openSUSE's own apps, and their KDE counterparts
    "app-calculator": ("accessories-calculator", "org.gnome.Calculator", "gnome-calculator", "kcalc",
                       "org.kde.kcalc", "galculator"),
    "app-camera": ("org.gnome.Snapshot", "org.gnome.Cheese", "cheese", "kamoso", "org.kde.kamoso"),
    "app-clocks": ("org.gnome.clocks", "gnome-clocks", "preferences-system-time", "kclock", "org.kde.kclock"),
    "app-contacts": ("org.gnome.Contacts", "kaddressbook", "org.kde.kaddressbook"),
    "app-diskusage": ("org.gnome.baobab", "baobab", "filelight", "org.kde.filelight"),
    "app-docviewer": ("org.gnome.Evince", "org.gnome.Papers", "evince", "atril", "okular", "org.kde.okular"),
    "app-logs": ("org.gnome.Logs", "gnome-logs", "utilities-log-viewer", "org.kde.kjournaldbrowser"),
    "app-maps": ("org.gnome.Maps", "gnome-maps", "marble", "org.kde.marble"),
    "app-connections": ("org.gnome.Connections", "krdc", "org.kde.krdc", "preferences-desktop-remote-desktop"),
    "app-videos": ("org.gnome.Totem", "totem", "org.gnome.Showtime", "org.xfce.parole", "parole", "dragonplayer",
                   "org.kde.dragonplayer", "multimedia-video-player"),
    "app-music": ("pragha", "org.gnome.Music", "gnome-music", "elisa", "org.kde.elisa", "multimedia-audio-player"),
    "app-audio": ("org.gnome.Decibels",),
    "app-tour": ("org.gnome.Tour", "gnome-tour"),
    "app-tweaks": ("org.gnome.tweaks", "gnome-tweaks"),
    "app-extensions": ("org.gnome.Extensions", "org.gnome.Shell.Extensions"),
    "app-mail": ("evolution", "org.gnome.Evolution", "org.xfce.mailreader", "internet-mail", "mail-client", "kmail",
                 "org.kde.kmail2"),
    "app-updates": ("system-software-update", "gpk-update-viewer", "gpk-prefs", "update-manager"),
    "app-notes": ("org.xfce.notes", "xfce4-notes", "org.gnome.Notes", "knotes", "org.kde.knotes"),
    "app-dictionary": ("org.xfce.Dictionary", "accessories-dictionary", "org.gnome.Dictionary"),
    "app-search": ("org.xfce.appfinder",),
    "app-sensors": ("xfce-sensors", "psensor"),
    "app-clipboard": ("xfce4-clipman-plugin", "klipper", "org.kde.klipper"),
    "app-color": ("gnome-color-manager", "preferences-color"),
    "app-yast": ("yast-control-center", "yast"),
    "app-volume": ("org.pulseaudio.pavucontrol", "pavucontrol", "multimedia-volume-control",
                   "preferences-desktop-sound"),
    "app-bluetooth": ("blueman", "blueman-device", "preferences-system-bluetooth", "bluetooth"),
    "device-harddisk": ("org.gnome.DiskUtility", "gnome-disks"),
}
# Devices: master -> the names drives and media are shown with
DEVICES = {
    "device-harddisk": ("drive-harddisk", "drive-harddisk-root", "drive-partition", "drive-multidisk",
                        "drive-multipartition"),
    "device-usb": ("drive-removable-media", "drive-removable-media-usb", "drive-removable-media-usb-pendrive",
                   "media-removable", "media-flash", "media-flash-memory-stick", "media-flash-sd-mmc",
                   "media-flash-smart-media", "org.xfce.volman"),
    "device-optical": ("media-optical", "media-optical-audio", "media-optical-blu-ray", "media-optical-data",
                       "media-optical-dvd", "media-optical-recordable", "media-optical-video", "drive-optical",
                       "media-write-cd", "media-write-dvd"),
    "device-server": ("network-server", "network-workgroup", "org.xfce.gigolo"),
    "device-printer": ("printer", "printer-network", "printer-remote", "system-config-printer",
                       "preferences-devices-printer"),
    "device-phone": ("phone", "smartphone"),
    "device-mouse": ("input-mouse",),
    "device-keyboard": ("input-keyboard",),
    "device-headphones": ("audio-headphones", "audio-headset"),
    "device-monitor": ("video-display", "display"),
    "device-battery": ("battery",),
    "device-computer": ("computer", "computer-laptop"),
    "app-spectacle": ("camera-photo",),
    "app-camera": ("camera-web",),
}

# Settings dialogs (Xfce's, and the same KCMs and panels elsewhere): the
# glyph carved into the pumpkin master, large enough to tell apart at 16 px
SETTINGS = {
    "glyph-brush": ("org.xfce.settings.appearance", "preferences-desktop-theme", "preferences-desktop-theme-global"),
    "emblem-monitor": ("org.xfce.settings.display", "preferences-desktop-display"),
    "glyph-keyboard": ("org.xfce.settings.keyboard", "preferences-desktop-keyboard"),
    "glyph-mouse": ("org.xfce.settings.mouse", "preferences-desktop-mouse", "preferences-desktop-touchpad"),
    "emblem-picture": ("org.xfce.xfdesktop", "preferences-desktop-wallpaper"),
    "glyph-panel": ("org.xfce.panel", "org.xfce.PanelProfiles"),
    "glyph-grid": ("org.xfce.workspaces", "preferences-desktop-virtual"),
    "glyph-window": ("org.xfce.xfwm4", "preferences-system-windows"),
    "glyph-wand": ("org.xfce.xfwm4-tweaks",),
    "glyph-bell": ("org.xfce.notification", "preferences-desktop-notification",
                   "preferences-desktop-notification-bell"),
    "glyph-battery": ("org.xfce.powermanager", "xfce4-power-manager-settings", "preferences-system-power-management",
                      "preferences-system-power"),
    "glyph-hourglass": ("org.xfce.session", "preferences-system-session"),
    "glyph-access": ("org.xfce.settings.accessibility", "preferences-desktop-accessibility"),
    "glyph-signpost": ("org.xfce.settings.default-applications", "preferences-desktop-default-applications"),
    "glyph-quill": ("org.xfce.settings.editor", "ca.desrt.dconf-editor"),
    "glyph-crystal": ("org.xfce.about",),
    "glyph-screensaver": ("org.xfce.ScreenSaver", "preferences-desktop-screensaver"),
    "glyph-logout": ("lightdm-gtk-greeter-settings", "preferences-system-login"),
    "glyph-web": ("preferences-system-network", "nm-connection-editor"),
    "glyph-lock": ("org.freedesktop.MalcontentControl",),
    "glyph-ghosts": ("mugshot", "preferences-desktop-user", "system-users"),
}
SETTINGS_EMBLEM_SIZE = 0.68   # glyph size relative to the pumpkin's body

# File types: the page master with an emblem -> the MIME type icon names.
# File managers ask for the specific name first (image-png before
# image-x-generic), so the common specific names are listed too.
MIME_EMBLEMS = {
    "glyph-quill": ("text-x-generic", "text-plain", "text-markdown", "text-csv"),
    "emblem-scroll": ("application-pdf", "x-office-document", "x-office-spreadsheet", "x-office-presentation",
                      "application-vnd.oasis.opendocument.text", "application-vnd.oasis.opendocument.spreadsheet",
                      "application-vnd.oasis.opendocument.presentation", "application-msword",
                      "application-vnd.openxmlformats-officedocument.wordprocessingml.document",
                      "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                      "application-vnd.openxmlformats-officedocument.presentationml.presentation",
                      "application-vnd.ms-excel", "application-vnd.ms-powerpoint", "application-epub+zip"),
    "emblem-picture": ("image-x-generic", "image-png", "image-jpeg", "image-gif", "image-webp", "image-svg+xml",
                       "image-heif", "image-avif", "image-tiff"),
    "emblem-note": ("audio-x-generic", "audio-mpeg", "audio-flac", "audio-ogg", "audio-x-vorbis+ogg",
                    "audio-x-wav", "audio-mp4", "audio-x-opus+ogg"),
    "emblem-reel": ("video-x-generic", "video-mp4", "video-webm", "video-x-matroska", "video-quicktime",
                    "video-x-msvideo"),
    "emblem-stencil": ("text-x-generic-template",),
    "glyph-chest": ("package-x-generic", "application-x-archive", "application-zip", "application-x-tar",
                    "application-x-compressed-tar", "application-x-xz-compressed-tar",
                    "application-x-7z-compressed", "application-x-rpm"),
    "glyph-web": ("text-html",),
    "glyph-wand": ("text-x-script", "text-x-python", "application-x-shellscript", "application-json",
                   "application-xml"),
    "glyph-gear": ("application-x-executable", "application-x-sharedlib", "application-x-desktop"),
}
MIME_EMBLEM_SIZE = 0.66   # emblem size relative to the page's width

# Dolphin is the master folder with a bat, like Breeze's folder with a dolphin
DOLPHIN = ("org.kde.dolphin", "system-file-manager", "org.gnome.Nautilus", "org.xfce.thunar", "org.xfce.filemanager")

# One-colour icons of the app menu and the leave/power actions: master ->
# (directory, names). They take the colour scheme's text colour.
SYMBOLIC = {
    "glyph-bookmark": ("actions", ("bookmarks", "favorites")),
    "glyph-apps": ("actions", ("applications-all-symbolic",)),
    "glyph-wand": ("categories", ("applications-development-symbolic",)),
    "glyph-brush": ("categories", ("applications-graphics-symbolic",)),
    "glyph-crystal": ("categories", ("help-about-symbolic",)),
    "glyph-web": ("categories", ("applications-internet-symbolic",)),
    "emblem-note": ("categories", ("applications-multimedia-symbolic",)),
    "glyph-quill": ("categories", ("applications-office-symbolic",)),
    "glyph-gear": ("categories", ("applications-system-symbolic", "preferences-system-symbolic")),
    "glyph-broom": ("categories", ("applications-utilities-symbolic",)),
    "glyph-signpost": ("actions", ("compass",)),
    # Thunar's side pane asks for go-home for Home; Dolphin's Home button too
    "emblem-cottage": ("actions", ("go-home",)),
    "emblem-monitor": ("apps", ("org.xfce.panel.showdesktop",)),
    "glyph-sleep": ("actions", ("system-suspend", "system-suspend-symbolic")),
    "glyph-hibernate": ("actions", ("system-suspend-hibernate", "system-suspend-hibernate-symbolic", "system-hibernate",
                                    "system-hibernate-symbolic")),
    "glyph-reboot": ("actions", ("system-reboot", "system-reboot-symbolic")),
    "glyph-power": ("actions", ("system-shutdown", "system-shutdown-symbolic")),
    "glyph-lock": ("actions", ("system-lock-screen", "system-lock-screen-symbolic")),
    "glyph-logout": ("actions", ("system-log-out", "system-log-out-symbolic", "xfsm-logout")),
    "glyph-ghosts": ("actions", ("system-switch-user", "system-switch-user-symbolic")),
}
SYMBOLIC_SIZE = 16


class Shape:
    def __init__(self, d, colour, dx=0.0, dy=0.0):
        self.d, self.colour, self.dx, self.dy = d, colour, dx, dy

    def bbox(self):
        nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", self.d)]
        xs, ys = nums[0::2], nums[1::2]
        return min(xs) + self.dx, min(ys) + self.dy, max(xs) + self.dx, max(ys) + self.dy

    def markup(self, colour=None):
        move = f' transform="translate({self.dx:g} {self.dy:g})"' if (self.dx, self.dy) != (0, 0) else ""
        return f'<path d="{self.d}" fill="{hexcolour(colour or self.colour)}"{move}/>'


def hexcolour(c):
    return c if isinstance(c, str) else "#{:02X}{:02X}{:02X}".format(*c)


def luminance(c):
    r, g, b = c
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def load(name):
    """Shapes of art/source/vectors/<name>.svg, without the backdrop; None if missing."""
    f = MASTERS / f"{name}.svg"
    if not f.exists():
        return None
    text = f.read_text()
    if text.startswith("version https://git-lfs"):
        raise SystemExit(f"{f} is a Git LFS pointer: run `git lfs pull` first")
    text = re.sub(r"<metadata>.*?</metadata>", "", text, flags=re.S)
    w, h = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text).groups())
    shapes = []
    for attrs in re.findall(r"<path\b([^>]*?)/?>", text):
        d = re.search(r'\bd="([^"]+)"', attrs).group(1)
        r, g, b = (int(v) for v in re.search(r'fill="rgb\((\d+),(\d+),(\d+)\)"', attrs).groups())
        move = re.search(r'translate\(([-\d.]+)[ ,]+([-\d.]+)\)', attrs)
        dx, dy = (float(move.group(1)), float(move.group(2))) if move else (0.0, 0.0)
        shapes.append(Shape(d, (r, g, b), dx, dy))
    # The backdrop covers the whole canvas; its outline may carry extra points
    # where artwork touches the edge, and it isn't always white.
    if shapes and shapes[0].bbox() == (0, 0, w, h):
        shapes = shapes[1:]
    # Where artwork touches the edge the backdrop can come in several pieces
    def edge(s):
        x0, y0, x1, y1 = s.bbox()
        return x0 <= 1 or y0 <= 1 or x1 >= w - 1 or y1 >= h - 1
    return [s for s in shapes if not (luminance(s.colour) > 0.97 and edge(s))]


def union(boxes):
    boxes = list(boxes)
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def inside(inner, outer, slack=2):
    return (inner[0] >= outer[0] - slack and inner[1] >= outer[1] - slack
            and inner[2] <= outer[2] + slack and inner[3] <= outer[3] + slack)


def svg(body, view, size=None):
    x0, y0, w, h = view
    dims = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{dims} viewBox="{x0:g} {y0:g} {w:g} {h:g}">'
            f"{body}</svg>\n")


def tidy(text, precision=5, groups=True):
    """Shorten coordinates and drop redundancy with scour."""
    from scour import scour
    args = [f"--set-precision={precision}", "--remove-metadata", "--enable-comment-stripping",
            "--strip-xml-prolog", "--no-line-breaks"]
    opts = scour.parse_args(args + (["--create-groups"] if groups else []))
    return scour.scourString(text, opts) + "\n"


def fit(shapes_markup, box, target, attrs=""):
    """Group markup so `box` (x0, y0, x1, y1) is centred in `target` (x0, y0, size)."""
    bx0, by0, bx1, by1 = box
    tx, ty, size = target
    s = size / max(bx1 - bx0, by1 - by0)
    ox = tx + (size - (bx1 - bx0) * s) / 2 - bx0 * s
    oy = ty + (size - (by1 - by0) * s) / 2 - by0 * s
    return f'<g{attrs} transform="translate({ox:.3f} {oy:.3f}) scale({s:.6f})">{shapes_markup}</g>'


def icon(shapes_markup, box, margin=0.0, size=ICON_SIZE):
    """A size x size icon of `shapes_markup`, scaled so `box` fills it (less the margin)."""
    m = size * margin
    return tidy(svg(fit(shapes_markup, box, (m, m, size - 2 * m)), (0, 0, size, size)))


# --- folders -------------------------------------------------------------------

def split_folder(shapes):
    """(body, leaf, front colour): the leaf is the near-white emblem and anything inside it."""
    leaf = [s for s in shapes if luminance(s.colour) > 0.93]
    if not leaf:
        raise SystemExit("folder master: no light emblem found")
    leaf_box = union(s.bbox() for s in leaf)
    leaf += [s for s in shapes if s not in leaf and inside(s.bbox(), leaf_box)]
    body = [s for s in shapes if s not in leaf]
    front = max(body, key=lambda s: (s.bbox()[3] - s.bbox()[1]) * (s.bbox()[2] - s.bbox()[0])
                if s.colour[0] > s.colour[2] else 0)
    return body, leaf, front.colour


def emblem_markup(shapes, box, ink, paper):
    """Fit a black-on-white glyph into `box`, dark parts in `ink`, light parts in `paper`."""
    glyph = [s for s in shapes if luminance(s.colour) < 0.5]
    gbox = union(s.bbox() for s in glyph)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    size = max(box[2] - box[0], box[3] - box[1]) * EMBLEM_SCALE
    body = "".join(s.markup(ink if luminance(s.colour) < 0.5 else paper) for s in shapes
                   if inside(s.bbox(), gbox))
    return fit(body, gbox, (cx - size / 2, cy - size / 2, size))


def open_folder_markup(body, palette):
    """The master folder opened: the front pocket tilts towards the viewer over
    a sheet of paper. Made from the master's own shapes, so it matches."""
    import math
    front = [s for s in body if s.colour[0] > s.colour[2] + 40]       # pocket and its top edge
    back = [s for s in body if s not in front]
    fx0, fy0, fx1, fy1 = union(s.bbox() for s in front)
    bx0, by0, bx1, by1 = union(s.bbox() for s in back)
    pw, ph = (bx1 - bx0) * 0.78, (fy1 - by0) * 0.7
    px, py = bx0 + (bx1 - bx0) * 0.11, by0 + (fy0 - by0) * 0.6
    paper = (f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{pw * 0.03:.1f}" '
             f'fill="{palette["cream"]}" transform="rotate(-4 {px + pw / 2:.1f} {py + ph / 2:.1f})"/>')
    k, lean = 0.82, math.tan(math.radians(14))     # squash towards the bottom edge, lean right
    e = lean * fy1 - lean * (fy1 - fy0) * k / 2
    tilt = f'<g transform="matrix(1 0 {-lean:.4f} {k} {e:.2f} {fy1 * (1 - k):.2f})">'
    return "".join(s.markup() for s in back) + paper + tilt + "".join(s.markup() for s in front) + "</g>"


def folder_icons(palette):
    """{relative path: SVG text} for every folder-shaped icon, or {} without the master."""
    master = load("folder")
    if master is None:
        return {}
    body, leaf, front = split_folder(master)
    body_markup = "".join(s.markup() for s in body)
    canvas = union(s.bbox() for s in master)
    leaf_box = union(s.bbox() for s in leaf)
    cream = palette["cream"]
    icons = {
        "scalable/places/folder.svg":
            icon(body_markup + "".join(s.markup(cream if luminance(s.colour) > 0.93 else None) for s in leaf),
                 canvas, 0.06),
        "16x16/places/folder.svg": icon(body_markup, canvas, 0.0, 16),
        "scalable/places/folder-open.svg": icon(open_folder_markup(body, palette), canvas, 0.06),
    }
    for name, emblem in FOLDER_EMBLEMS.items():
        shapes = load(emblem)
        if shapes is None:
            continue
        icons[f"scalable/places/{name}.svg"] = icon(
            body_markup + emblem_markup(shapes, leaf_box, cream, front), canvas, 0.06)
    return icons


# --- other icons -----------------------------------------------------------------

def to_chameleon_green(colour, chameleon):
    """Move greens and teals to the chameleon's hue, keeping lightness and saturation."""
    import colorsys
    h, light, s = colorsys.rgb_to_hls(*(c / 255 for c in colour))
    if 70 / 360 <= h <= 185 / 360 and s > 0.2:
        h = colorsys.rgb_to_hls(*(c / 255 for c in rgb(chameleon)))[0]
        return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, light, s))
    return colour


def normalise(colour, palette):
    """Hold a master's colour to the palette: purples move to the icon plum's
    hue and saturation (the masters drift towards magenta), near-whites
    become cream, and near-blacks lift until they stand off the night
    background (WCAG 1.4.11 asks 3:1 of icons; this keeps at least 1.5:1)."""
    import colorsys
    r, g, b = (c / 255 for c in colour)
    h, light, s = colorsys.rgb_to_hls(r, g, b)
    if 260 / 360 <= h <= 340 / 360 and s > 0.2:
        ph, _, ps = colorsys.rgb_to_hls(*(c / 255 for c in rgb(palette["plum_icon"])))
        h, s = ph, min(s, ps)
    elif light > 0.93 and s < 0.6:
        return rgb(palette["cream"])
    night = rgb(palette["night"])
    while light < 1 and contrast(tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, light, s)), night) < 1.5:
        light += 0.01
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, light, s))


def paint(shapes, palette):
    """Markup of a colour master's shapes, its colours held to the palette."""
    return "".join(s.markup(normalise(s.colour, palette)) for s in shapes)


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def potion_markup(trash, potion):
    """The glowing potion and bubbles of `potion`, sized and placed on `trash`'s rim.

    The potion goes first, so the cauldron's rim hides its lower half."""
    rim = min(trash, key=lambda s: s.bbox()[1])
    rx0, ry0, rx1, _ = rim.bbox()
    warm = [s for s in potion if s.colour[0] > 200 and s.colour[1] > 80 and s.colour[2] < 120]
    surface = max(warm, key=lambda s: area(s.bbox()))
    sx0, sy0, sx1, sy1 = surface.bbox()
    k = 0.9 * (rx1 - rx0) / (sx1 - sx0)
    tx = (rx0 + rx1) / 2 - (sx0 + sx1) / 2 * k
    ty = ry0 - (sy0 + 0.6 * (sy1 - sy0)) * k       # the potion bubbles up over the rim
    top = ty + min(s.bbox()[1] for s in warm) * k
    return (f'<g transform="translate({tx:.3f} {ty:.3f}) scale({k:.6f})">'
            + "".join(s.markup() for s in warm) + "</g>"), top


def other_icons(palette):
    icons = {}
    trash, potion = load("trash"), load("potion")
    if trash:
        pot = paint(trash, palette)
        box = union(s.bbox() for s in trash)
        if potion:
            full, top = potion_markup(trash, potion)
            box = (box[0], min(box[1], top), box[2], box[3])   # same frame for both
            icons["scalable/places/user-trash-full.svg"] = icon(full + pot, box, 0.06)
        icons["scalable/places/user-trash.svg"] = icon(pot, box, 0.06)
        icons["16x16/places/user-trash.svg"] = icon(pot, union(s.bbox() for s in trash), 0.0, 16)
    launcher = load("launcher")
    if launcher:
        markup = "".join(s.markup(to_chameleon_green(s.colour, palette["chameleon"])) for s in launcher)
        svg_text = icon(markup, union(s.bbox() for s in launcher), 0.02)
        for name in LAUNCHERS:
            icons[f"scalable/apps/{name}.svg"] = svg_text
    folder, cottage = load("folder"), load("emblem-cottage")
    if folder and cottage:
        body, leaf, front = split_folder(folder)
        box = union(s.bbox() for s in leaf)
        grow = (box[2] - box[0]) * 0.25
        box = (box[0] - grow, box[1] - grow, box[2] + grow, box[3] + grow)
        icons["16x16/places/user-home.svg"] = icon(
            "".join(s.markup() for s in body) + emblem_markup(cottage, box, palette["cream"], front),
            union(s.bbox() for s in folder), 0.0, 16)
    return icons


def app_icons(palette):
    made = {}
    for master, names in APPS.items():
        shapes = load(master)
        if shapes:
            text = icon(paint(shapes, palette), union(s.bbox() for s in shapes), 0.06)
            made.update({f"scalable/apps/{n}.svg": text for n in names})
    folder, bat = load("folder"), load("emblem-bat")
    if folder and bat:
        body, leaf, front = split_folder(folder)
        text = icon("".join(s.markup() for s in body)
                    + emblem_markup(bat, union(s.bbox() for s in leaf), palette["cream"], front),
                    union(s.bbox() for s in folder), 0.06)
        made.update({f"scalable/apps/{n}.svg": text for n in DOLPHIN})
    return made


def symbolic_icon(shapes, palette):
    """A one-colour icon in KDE's symbolic format: the dark parts of a glyph in
    the colour scheme's text colour, the light details inside them cut out as
    holes (each dark shape plus the light shapes drawn on top of it, even-odd)."""
    dark = [(i, s) for i, s in enumerate(shapes) if luminance(s.colour) < 0.5]
    light = [(i, s) for i, s in enumerate(shapes) if luminance(s.colour) >= 0.5]
    paths = []
    for i, s in dark:
        holes = [h for j, h in light if j > i and inside(h.bbox(), s.bbox())]
        d = " ".join([s.d] + [h.d for h in holes])
        paths.append(f'<path class="ColorScheme-Text" d="{d}" fill="currentColor" fill-rule="evenodd"/>')
    box = union(s.bbox() for _, s in dark)
    style = ('<style type="text/css" id="current-color-scheme">'
             f'.ColorScheme-Text {{ color:{palette["cream"]}; }}</style>')
    size = SYMBOLIC_SIZE
    # scour moves a fill all paths share up to their group, and Qt resolves
    # currentColor there, so the group needs the class as well
    # whole pixels: a 14 px box from (1, 1) keeps straight edges on the grid at 16 px
    body = fit("".join(paths), box, (1, 1, size - 2), ' class="ColorScheme-Text"')
    return tidy(svg(style + body, (0, 0, size, size)), groups=False)


def symbolic_icons(palette):
    made = {}
    for master, (folder, names) in SYMBOLIC.items():
        shapes = load(master)
        if shapes:
            text = symbolic_icon(shapes, palette)
            made.update({f"scalable/{folder}/{n}.svg": text for n in names})
    return made


def device_icons(palette):
    made = {}
    for master, names in DEVICES.items():
        shapes = load(master)
        if shapes:
            text = icon(paint(shapes, palette), union(s.bbox() for s in shapes), 0.06)
            made.update({f"scalable/devices/{n}.svg": text for n in names})
    return made


def mime_icons(palette):
    """File types: the page master with an emblem on its sheet, dark parts of
    the glyph in pumpkin, light details in the page's colour."""
    page = load("mime-page")
    if page is None:
        return {}
    sheet = max(page, key=lambda s: area(s.bbox()) if luminance(s.colour) > 0.7 else 0)
    x0, y0, x1, y1 = sheet.bbox()
    size = (x1 - x0) * MIME_EMBLEM_SIZE / EMBLEM_SCALE
    cx, cy = (x0 + x1) / 2, y0 + (y1 - y0) * 0.58
    box = (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2)
    page_markup = "".join(s.markup() for s in page)
    frame = union(s.bbox() for s in page)
    made = {}
    for emblem, names in MIME_EMBLEMS.items():
        shapes = load(emblem)
        if shapes:
            text = icon(page_markup + emblem_markup(shapes, box, palette["pumpkin"], sheet.colour), frame, 0.06)
            made.update({f"scalable/mimetypes/{n}.svg": text for n in names})
    return made


def settings_icons(palette):
    """Settings dialogs: the glyph carved into the pumpkin master, dark like an
    unlit jack-o'-lantern. The pumpkin's body is flattened to two oranges so
    the glyph stays readable at 16 px; the stem keeps its colours."""
    pumpkin = load("settings-pumpkin")
    if pumpkin is None:
        return {}
    frame = union(s.bbox() for s in pumpkin)
    top = frame[1] + (frame[3] - frame[1]) * 0.25          # below the stem
    lower = [s for s in pumpkin if s.bbox()[1] >= top]
    body = union(s.bbox() for s in lower)
    size = min(body[2] - body[0], body[3] - body[1]) * SETTINGS_EMBLEM_SIZE / EMBLEM_SCALE
    cx, cy = (body[0] + body[2]) / 2, (body[1] + body[3]) / 2
    box = (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2)
    face = palette["pumpkin"]

    def flat(s):
        if s not in lower:
            return normalise(s.colour, palette)
        return rgb(palette["ember"] if luminance(s.colour) < 0.45 else face)
    pumpkin_markup = "".join(s.markup(flat(s)) for s in pumpkin)
    made = {}
    for emblem, names in SETTINGS.items():
        shapes = load(emblem)
        if shapes:
            carved = emblem_markup(shapes, box, palette["complementary"], face)
            made.update({f"scalable/apps/{n}.svg": icon(pumpkin_markup + carved, frame, 0.06) for n in names})
    return made


def icons(palette):
    """Every icon the masters can make: {path relative to the theme: SVG text}."""
    made = {**folder_icons(palette), **other_icons(palette), **app_icons(palette), **symbolic_icons(palette),
            **device_icons(palette), **mime_icons(palette), **settings_icons(palette)}
    if "scalable/places/folder.svg" in made:
        made["scalable/mimetypes/inode-directory.svg"] = made["scalable/places/folder.svg"]
    for alias, name in ALIASES.items():
        if f"scalable/places/{name}.svg" in made:
            made[f"scalable/places/{alias}.svg"] = made[f"scalable/places/{name}.svg"]
    return made


# --- Plasma style ornaments ------------------------------------------------------

def ornament(name, palette):
    """SVG text for plasma/desktoptheme ornaments/<name>, or None without a master."""
    stem = name.removesuffix(".svg")
    shapes = load({"popup-sprig": "sprig", "clock-face": "clock"}[stem])
    if shapes is None:
        return None
    # Ornaments have no white of their own: any left is backdrop trapped
    # between shapes (between a twig and a leaf, say)
    shapes = [s for s in shapes if luminance(s.colour) <= 0.97]
    markup = "".join(s.markup() for s in shapes)
    x0, y0, x1, y1 = union(s.bbox() for s in shapes)
    if stem == "popup-sprig":
        pad = (x1 - x0) * 0.02
        w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
        return tidy(svg(f'<g transform="translate({pad - x0:g} {pad - y0:g})">{markup}</g>', (0, 0, w, h)))
    # clock-face: the pumpkin body centred on (100, 100), which the hands turn
    # around; the invisible rect keeps the element exactly 200x200.
    body = [s for s in shapes if s.colour[0] > 150 and s.colour[0] > s.colour[2] + 60]
    bx0, by0, bx1, by1 = union(s.bbox() for s in body)
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    reach = max(cx - x0, x1 - cx, cy - y0, y1 - cy)
    s = 96 / reach
    notches = "".join(
        f'<rect x="{96 if i % 3 == 0 else 97}" y="{24 if i % 3 == 0 else 26}" '
        f'width="{8 if i % 3 == 0 else 6}" height="{15 if i % 3 == 0 else 11}" rx="2" '
        f'transform="rotate({i * 30} 100 100)"/>' for i in range(12))
    return tidy(svg(
        '<rect width="200" height="200" fill="#000000" fill-opacity="0.002"/>'
        f'<g transform="translate({100 - cx * s:.3f} {100 - cy * s:.3f}) scale({s:.6f})">{markup}</g>'
        f'<g fill="{palette["sel_neutral"]}" stroke="{palette["ember"]}" stroke-width="1.5">{notches}</g>',
        (0, 0, 200, 200), 200))
