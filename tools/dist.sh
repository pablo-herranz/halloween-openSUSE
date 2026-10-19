#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Pack build/ into release archives in dist/:
#   halloween-openSUSE-VERSION.tar.gz        the built theme with tools/install.py
#                                            and the Makefile: unpack, then
#                                            `make install DESTDIR=…` (what an RPM
#                                            spec's %install runs)
#   halloween-openSUSE-VERSION-firefox.xpi   the Firefox theme
#   SHA256SUMS
# Run `make check` (or `make release-check`) first.
set -euo pipefail
cd "$(dirname "$0")/.."
export COPYFILE_DISABLE=1   # no macOS ._ metadata files in the archives
[ -f build/MANIFEST.sha256 ] || { echo "no build: run make check first" >&2; exit 1; }

version=$(python3 -c 'import sys; sys.path.insert(0, "tools"); from common import VERSION; print(VERSION)')
name=halloween-openSUSE-$version
out=dist
rm -rf "$out"
mkdir -p "$out/$name"

# The complete set: the build, the installer and the docs
mkdir -p "$out/$name/build" "$out/$name/tools"
cp -R build/user build/root build/firefox build/defaults build/MANIFEST.sha256 "$out/$name/build/"
cp tools/install.py "$out/$name/tools/"
cp -R Makefile README.md CHANGELOG.md REUSE.toml LICENSES "$out/$name/"
tar --no-xattrs -C "$out" -czf "$out/$name.tar.gz" "$name"
rm -rf "${out:?}/$name"
cp build/firefox/openSUSE-halloween.xpi "$out/$name-firefox.xpi"

if command -v sha256sum >/dev/null; then
    (cd "$out" && sha256sum -- * > SHA256SUMS)
else
    (cd "$out" && shasum -a 256 -- * > SHA256SUMS)
fi
ls -l "$out"
