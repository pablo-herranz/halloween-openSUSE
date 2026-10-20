# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""How Plasma finds an icon, and which Breeze icons it would take from us.

KIconLoader (kiconthemes, src/kiconloader.cpp, findMatchingIcon) goes through
the theme and the themes it inherits one at a time, and inside each it
shortens the name before it moves on: "battery-060-charging-symbolic" becomes
"battery-060-symbolic", then "battery-060", "battery-symbolic", "battery".
Our theme comes first, so any Breeze icon whose name extends one we ship
shows ours, not Breeze's. The theme therefore ships, for every such name,
either an icon of its own or a link to Breeze's (plan()); check.py runs the
same lookup over every Breeze name to keep it that way.

Breeze's names come from tools/breeze-icons.txt."""

from common import ROOT

BREEZE = ROOT / "tools/breeze-icons.txt"
MEDIA = {"text", "application", "image", "audio", "inode", "video", "message", "model", "multipart", "x-content",
         "x-epoc"}
# Shortened names whose icon is ours on purpose: a variant of the same thing
KEEP_SUFFIXES = ("-rtl", "-update", "-large", "-template", "-master", "-compressed")
# Words that add a state to a name (the tray's notification-active and
# notification-empty, the battery applet's system-suspend-inhibited): one glyph
# of ours can't show which state it is, so those keep Breeze's
STATES = {"active", "inactive", "disabled", "empty", "inhibited", "uninhibited", "progress"}


def breeze():
    """{icon name: its file, relative to Breeze Dark's folder}."""
    files = {}
    for line in BREEZE.read_text().splitlines():
        if line and not line.startswith("#"):
            name = line.rsplit("/", 1)[1].rsplit(".", 1)[0]
            files[name] = line
    return files


def chain(name):
    """The names KIconLoader tries in one theme, in order."""
    generic, symbolic = name.endswith("-x-generic"), name.endswith("-symbolic")
    current = name
    while current:
        yield current
        if generic:
            return
        if symbolic:
            current = current.removesuffix("-symbolic")
            yield current
        cut = current.rfind("-")
        if cut > 1:
            current = current[:cut].removesuffix("-x")
            if symbolic:
                current += "-symbolic"
        elif current in MEDIA:
            current, generic = current + "-x-generic", True
        else:
            return


def first_hit(name, ours):
    return next((n for n in chain(name) if n in ours), None)


def wanted(name, hit, one_colour):
    """Is it right that Breeze's `name` shows our `hit`?"""
    if name.split("-", 1)[0] in MEDIA or hit.endswith("-x-generic"):
        return True                                  # file types: our generic page
    if name.startswith("folder") and not name.endswith("-symbolic"):
        return True                                  # folder variants: our folder
    if STATES & set(name.removesuffix("-symbolic")[len(hit.removesuffix("-symbolic")):].split("-")):
        return False                                 # a state ours can't show
    if hit in one_colour:
        return True                                  # ours is one colour already
    return any(name.endswith(s) or s + "-" in name for s in KEEP_SUFFIXES)


def plan(ours, one_colour):
    """{Breeze name: its Breeze file} for every Breeze icon Plasma would
    otherwise take from us where it shouldn't; the theme links them."""
    files = breeze()
    links = {}
    for name, path in files.items():
        if name in ours:
            continue
        hit = first_hit(name, ours)
        if hit and not wanted(name, hit, one_colour):
            links[name] = path
    return links
