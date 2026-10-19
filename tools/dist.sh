#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Pack the release archives into dist/:
#   halloween-openSUSE-VERSION.tar.gz        the sources (every tracked file,
#                                            art masters included) and the
#                                            built theme in build/: `make
#                                            install DESTDIR=…` installs the
#                                            build as an RPM spec's %install
#                                            would, `make check` rebuilds it
#   halloween-openSUSE-VERSION-firefox.xpi   the Firefox theme
#   SHA256SUMS
# Run `make check` (or `make release-check`) first, with the Git LFS masters
# pulled.
set -euo pipefail
cd "$(dirname "$0")/.."
export COPYFILE_DISABLE=1   # no macOS ._ metadata files in the archives
[ -f build/MANIFEST.sha256 ] || { echo "no build: run make check first" >&2; exit 1; }

version=$(python3 -c 'import sys; sys.path.insert(0, "tools"); from common import VERSION; print(VERSION)')
name=halloween-openSUSE-$version
out=dist
rm -rf "$out"
mkdir -p "$out/$name"

# The sources: every tracked file as checked out, so the art masters must be
# the Git LFS content, not its pointers
if git ls-files -z | xargs -0 grep -l --null-data -m1 '^version https://git-lfs' 2>/dev/null | head -c1 | grep -q .; then
    echo "Git LFS pointers instead of masters: run git lfs pull first" >&2
    exit 1
fi
git ls-files -z | tar --no-xattrs --null -T - -cf - | tar -C "$out/$name" -xf -
# and the build
mkdir -p "$out/$name/build"
cp -R build/user build/root build/firefox build/defaults build/MANIFEST.sha256 build/build-info.json "$out/$name/build/"
tar --no-xattrs -C "$out" -czf "$out/$name.tar.gz" "$name"
rm -rf "${out:?}/$name"
cp build/firefox/openSUSE-halloween.xpi "$out/$name-firefox.xpi"

if command -v sha256sum >/dev/null; then
    (cd "$out" && sha256sum -- * > SHA256SUMS)
else
    (cd "$out" && shasum -a 256 -- * > SHA256SUMS)
fi
ls -l "$out"
