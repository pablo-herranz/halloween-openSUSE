#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Install the built theme into the system paths, as a package does.

Only copies files: nothing is selected, no settings change. An RPM's
%install runs this with DESTDIR set to the build root. --defaults installs
the optional defaults instead (what a separate defaults subpackage ships),
which make the theme the default the way openSUSE packages do it.

Uses only the standard library, so it runs from a release tarball too.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent / "build"
FIREFOX_ID = "openSUSE-halloween@pluskal.org"

# (path in build/, install path). Every entry inside a source directory is
# ours, so uninstalling removes exactly those entries from the install path.
FILES = [
    ("user/wallpapers", "{datadir}/wallpapers"),
    ("user/backgrounds", "{datadir}/backgrounds"),
    ("user/icons", "{datadir}/icons"),
    ("user/themes", "{datadir}/themes"),
    ("user/openSUSE-halloween", "{datadir}/openSUSE-halloween"),
    ("user/gnome-background-properties", "{datadir}/gnome-background-properties"),
    ("user/color-schemes", "{datadir}/color-schemes"),
    ("user/plasma/desktoptheme", "{datadir}/plasma/desktoptheme"),
    ("user/plasma/look-and-feel", "{datadir}/plasma/look-and-feel"),
    ("root/sddm", "{datadir}/sddm/themes"),
    ("root/plymouth", "{datadir}/plymouth/themes"),
    ("firefox/openSUSE-halloween.xpi", "{libdir}/firefox/browser/extensions/" + FIREFOX_ID + ".xpi"),
]
DEFAULTS = [
    ("defaults/sddm.conf.d", "{prefix}/lib/sddm/sddm.conf.d"),
    ("defaults/glib-2.0/schemas", "{datadir}/glib-2.0/schemas"),
]
# Files that name our own installed files by their /usr/share path
REWRITE = (".xml", ".override", ".conf", ".plymouth")


def entries(table, dirs):
    """(source, destination) for each of our top-level files or folders."""
    for src, dest in table:
        src, dest = BUILD / src, Path(dest.format(**dirs))
        if src.is_dir():
            for child in sorted(src.iterdir()):
                yield child, dest / child.name
        elif src.exists():
            yield src, dest


def under(destdir, path):
    return Path(destdir + str(path)) if destdir else path


def copy(src, dest, datadir):
    """Copy a file, folder or symlink: folders 0755, files 0644, links as links.
    Paths under /usr/share in REWRITE files follow --prefix."""
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.is_dir() and (src.is_symlink() or not src.is_dir()):
        shutil.rmtree(dest)
    dest.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    if src.is_symlink():
        os.symlink(os.readlink(src), dest)
    elif src.is_dir():
        dest.mkdir(mode=0o755, exist_ok=True)
        dest.chmod(0o755)
        for child in sorted(src.iterdir()):
            copy(child, dest / child.name, datadir)
    elif src.suffix in REWRITE and datadir != "/usr/share":
        dest.write_text(src.read_text().replace("/usr/share/", f"{datadir}/"))
        dest.chmod(0o644)
    else:
        shutil.copyfile(src, dest)
        dest.chmod(0o644)


def remove(dest):
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.is_dir():
        shutil.rmtree(dest)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--destdir", default=os.environ.get("DESTDIR", ""))
    ap.add_argument("--prefix", default="/usr")
    ap.add_argument("--libdir", help="default: PREFIX/lib64")
    ap.add_argument("--sysconfdir", default="/etc")
    ap.add_argument("--defaults", action="store_true", help="the defaults instead of the theme files")
    ap.add_argument("--uninstall", action="store_true", help="remove what this installs")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if not (BUILD / "MANIFEST.sha256").exists():
        sys.exit(f"{BUILD} has no build: run `make check` first")
    dirs = {"prefix": args.prefix, "datadir": f"{args.prefix}/share", "libdir": args.libdir or f"{args.prefix}/lib64",
            "sysconfdir": args.sysconfdir}
    for src, dest in entries(DEFAULTS if args.defaults else FILES, dirs):
        target = under(args.destdir.rstrip("/"), dest)
        if args.uninstall:
            remove(target)
        else:
            copy(src, target, dirs["datadir"])
        if not args.quiet:
            print(f"{'removed' if args.uninstall else 'installed'} {dest}")


if __name__ == "__main__":
    main()
