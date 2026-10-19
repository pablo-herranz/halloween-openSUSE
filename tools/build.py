#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build every installable piece of halloween-openSUSE into build/.

build/user/      the themes, icons and wallpapers (share/ in the system)
build/root/      the login screen and boot splash
build/firefox/   the Firefox theme, unpacked and as an .xpi
build/defaults/  the optional defaults that make the theme the default

tools/install.py installs them into the system paths, as a package does.

The pieces come from tools/targets/: shared ones for any desktop, and one
set per desktop (KDE Plasma today). Any art master missing from art/source/
is replaced by a drawn placeholder, listed in build/placeholders.txt.
"""

import argparse
import hashlib
import json
import shutil

from common import BUILD, DEFAULTS, FIREFOX, SYSTEM, USER, write
from context import Context
from targets import DESKTOPS, TARGETS, desktops_of


def write_manifest(ctx, desktops):
    lines = []
    for f in sorted(BUILD.rglob("*")):
        rel = f.relative_to(BUILD)
        if rel.parts[0] not in ("user", "root", "defaults"):
            continue
        if f.is_symlink():
            # Links into other packages' files, such as the SDDM base theme
            lines.append(f"{hashlib.sha256(str(f.readlink()).encode()).hexdigest()}  {rel} -> {f.readlink()}")
        elif f.is_file():
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}")
    write(BUILD / "MANIFEST.sha256", "\n".join(lines) + "\n")
    write(BUILD / "placeholders.txt", "".join(f"{n}\n" for n in ctx.placeholders))
    info = {"desktops": desktops, "placeholders": ctx.placeholders}
    write(BUILD / "build-info.json", json.dumps(info, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--desktop", choices=["all", *DESKTOPS], default="all",
                    help="build the shared pieces plus this desktop's (default: every desktop)")
    args = ap.parse_args()
    for d in (USER, SYSTEM, FIREFOX, DEFAULTS, BUILD / "install"):
        if d.exists():
            shutil.rmtree(d)
    desktops = DESKTOPS if args.desktop == "all" else [args.desktop]
    ctx = Context()
    for target in TARGETS:
        if "shared" in desktops_of(target) or set(desktops_of(target)) & set(desktops):
            target.build(ctx)
    write_manifest(ctx, desktops)
    print(f"built {BUILD}")
    if ctx.placeholders:
        print(f"placeholders: {len(ctx.placeholders)} (see build/placeholders.txt)")


if __name__ == "__main__":
    main()
