#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build every installable piece of halloween-openSUSE into build/.

build/user/     goes to ~/.local/share (no root needed)
build/root/     goes to /usr/share (login screen and boot splash)
build/firefox/  the Firefox theme, unpacked and as an .xpi
build/install/  the install scripts

The pieces come from tools/targets/: shared ones for any desktop, and one
set per desktop (KDE Plasma today). Any art master missing from art/source/
is replaced by a drawn placeholder, listed in build/placeholders.txt.
"""

import argparse
import hashlib
import json
import shutil

from common import BUILD, FIREFOX, ROOT, SYSTEM, USER, write
from context import Context
from targets import DESKTOPS, TARGETS


def build_install_scripts():
    out = BUILD / "install"
    shutil.copytree(ROOT / "install", out)
    for f in out.iterdir():
        if f.suffix == ".sh":
            f.chmod(0o755)


def write_manifest(ctx):
    lines = []
    for f in sorted(BUILD.rglob("*")):
        rel = f.relative_to(BUILD)
        if f.is_file() and rel.parts[0] in ("user", "root", "install"):
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}")
    write(BUILD / "MANIFEST.sha256", "\n".join(lines) + "\n")
    write(BUILD / "placeholders.txt", "".join(f"{n}\n" for n in ctx.placeholders))
    write(BUILD / "build-info.json", json.dumps({"placeholders": ctx.placeholders}, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--desktop", choices=["all", *DESKTOPS], default="all",
                    help="build the shared pieces plus this desktop's (default: every desktop)")
    args = ap.parse_args()
    for d in (USER, SYSTEM, FIREFOX, BUILD / "install"):
        if d.exists():
            shutil.rmtree(d)
    ctx = Context()
    for target in TARGETS:
        if args.desktop == "all" or target.DESKTOP in ("shared", args.desktop):
            target.build(ctx)
    build_install_scripts()
    write_manifest(ctx)
    print(f"built {BUILD}")
    if ctx.placeholders:
        print(f"placeholders: {len(ctx.placeholders)} (see build/placeholders.txt)")


if __name__ == "__main__":
    main()
