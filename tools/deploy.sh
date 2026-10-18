#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copy build/ to a test machine: tools/deploy.sh user@host
# It lands in ~/.cache/halloween-openSUSE; screenshots taken there are kept.
set -euo pipefail
target=${1:?usage: deploy.sh user@host}
root=$(cd "$(dirname "$0")/.." && pwd)
rsync -a --delete --exclude /cache/ --exclude /screenshots/ "$root/build/" "$target:.cache/halloween-openSUSE/"
echo "deployed to $target:~/.cache/halloween-openSUSE"
