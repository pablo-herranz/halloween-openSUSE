# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build targets: one module per installable piece of the theme.

Every module has DESKTOP: "shared" for pieces any desktop can use, the
desktop it belongs to (such as "plasma"), or a tuple of desktops; and
build(ctx), which writes its output into build/. tools/build.py runs them in the order of TARGETS. To add
a desktop, add its modules and list them here; see docs/architecture.md.
"""

from targets import firefox, icons, plasma, plymouth, sddm, wallpapers

TARGETS = [wallpapers, plasma, icons, sddm, plymouth, firefox]


def desktops_of(target):
    return (target.DESKTOP,) if isinstance(target.DESKTOP, str) else tuple(target.DESKTOP)


DESKTOPS = sorted({d for t in TARGETS for d in desktops_of(t)} - {"shared"})
