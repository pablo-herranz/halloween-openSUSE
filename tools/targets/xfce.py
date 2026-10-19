# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Xfce: xfwm4's default window-manager theme at its three scales (pinned in
tools/upstream.toml), recoloured through each themerc, and the notification
theme. GTK and the panel come from targets/gtk.py."""

import shutil

from common import ROOT, fill_tokens, upstream_archive, write
from targets.gtk import ID, THEME

DESKTOP = "xfce"
# Theme folder suffix: xfwm4's theme it is made from
SCALES = {"": "default", "-hdpi": "default-hdpi", "-xhdpi": "default-xhdpi"}


def themerc(upstream, colours):
    keys = {line.split("=")[0] for line in colours}
    kept = [line for line in upstream.splitlines() if line and line.split("=")[0] not in keys]
    return "\n".join(kept + colours) + "\n"


def build(ctx):
    themes = upstream_archive("xfwm4") / "xfwm4-4.20.0/themes"
    template = fill_tokens((ROOT / "xfce/xfwm4/colors.in").read_text(), ctx.palette)
    colours = [line for line in template.splitlines() if line and not line.startswith("#")]
    for suffix, name in SCALES.items():
        src, out = themes / name, THEME.parent / f"{ID}{suffix}" / "xfwm4"
        out.mkdir(parents=True)
        for f in sorted(src.iterdir()):
            if f.suffix in (".xpm", ".png", ".svg"):
                shutil.copyfile(f, out / f.name)
        write(out / "themerc", themerc((src / "themerc").read_text(), colours))
    write(THEME / "xfce-notify-4.0/gtk.css",
          fill_tokens((ROOT / "xfce/xfce-notify-4.0/gtk.css.in").read_text(), ctx.palette))
