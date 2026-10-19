#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Pack build/ into release archives in dist/:
#   halloween-openSUSE-VERSION.tar.gz        everything, with the install scripts
#   halloween-openSUSE-VERSION-*.tar.gz      each Plasma piece on its own, as the
#                                            KDE Store and kpackagetool6 take them
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

# The complete set: unpack, then run install/install-user.sh and friends
cp -R build/user build/root build/firefox build/install build/MANIFEST.sha256 \
    README.md CHANGELOG.md REUSE.toml LICENSES "$out/$name/"
tar -C "$out" -czf "$out/$name.tar.gz" "$name"
rm -rf "${out:?}/$name"

piece() {  # piece SUFFIX DIR ENTRY
    tar -C "$2" -czf "$out/$name-$1.tar.gz" "$3"
}
piece global-theme build/user/plasma/look-and-feel org.openSUSE.halloween.desktop
piece plasma-style build/user/plasma/desktoptheme openSUSE-halloween
piece icons build/user/icons openSUSE-halloween
piece wallpaper build/user/wallpapers openSUSEhalloween
cp build/user/color-schemes/openSUSEHalloween.colors "$out/$name-openSUSEHalloween.colors"
cp build/firefox/openSUSE-halloween.xpi "$out/$name-firefox.xpi"

if command -v sha256sum >/dev/null; then
    (cd "$out" && sha256sum -- * > SHA256SUMS)
else
    (cd "$out" && shasum -a 256 -- * > SHA256SUMS)
fi
ls -l "$out"
