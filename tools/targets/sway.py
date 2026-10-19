# SPDX-FileCopyrightText: 2026 Jan Baier <jan.baier@amagical.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Sway and Waybar: a compositor config snippet with the palette's colours,
and a Waybar stylesheet. GTK apps use the shared GTK theme."""

from common import ROOT, USER, fill_tokens, write

DESKTOP = "sway"


def build(ctx):
    src = ROOT / "sway"
    sway_out = USER / "openSUSE-halloween" / "sway"
    waybar_out = USER / "openSUSE-halloween" / "waybar"
    write(sway_out / "theme", fill_tokens((src / "sway/theme.in").read_text(), ctx.palette))
    write(waybar_out / "style.css", fill_tokens((src / "waybar/style.css.in").read_text(), ctx.palette))
    swaync_out = USER / "openSUSE-halloween" / "swaync"
    write(swaync_out / "style.css", fill_tokens((src / "swaync/style.css.in").read_text(), ctx.palette))
