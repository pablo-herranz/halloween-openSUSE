#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copy build/ and the development helpers in tools/dev/ to a test machine:
# tools/deploy.sh user@host. They land in ~/.cache/halloween-openSUSE (the
# helpers in its install/); screenshots taken there are kept.
set -euo pipefail
target=${1:?usage: deploy.sh user@host}
root=$(cd "$(dirname "$0")/.." && pwd)
rsync -a --delete --exclude /cache/ --exclude /screenshots/ --exclude /install/ \
    "$root/build/" "$target:.cache/halloween-openSUSE/"
rsync -a --delete "$root/tools/dev/" "$target:.cache/halloween-openSUSE/install/"
echo "deployed to $target:~/.cache/halloween-openSUSE"
