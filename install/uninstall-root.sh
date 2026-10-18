#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Undo install-root.sh: restore the previous login screen and Plymouth theme,
# rebuild the initrds, then remove the system halloween-openSUSE files.
set -euo pipefail
. "$(dirname "$0")/common.sh"
[ "$(id -u)" = 0 ] || die "run as root: sudo $0"

STATE=/var/lib/halloween-openSUSE
LOCAL=/usr/local/share
SDDM_HOME=$(getent passwd sddm | cut -d: -f6)
PLYMOUTH_THEME=bgrt
[ -f "$STATE/root-state.env" ] && . "$STATE/root-state.env"

log "restoring the login screen"
rm -f "$SDDM_CONF"
for f in kdeglobals plasmarc; do
    if [ -f "$STATE/sddm-$f" ]; then
        cp -p "$STATE/sddm-$f" "$SDDM_HOME/.config/$f"
    elif [ -f "$STATE/sddm-$f.absent" ]; then
        rm -f "$SDDM_HOME/.config/$f"
    fi
done

log "restoring Plymouth theme $PLYMOUTH_THEME"
plymouth-set-default-theme "$PLYMOUTH_THEME"

log "removing files"
rm -rf "/usr/share/sddm/themes/$SDDM_ID" "/usr/share/plymouth/themes/$PLYMOUTH_ID" \
    "$LOCAL/plasma/desktoptheme/$STYLE_ID" "$LOCAL/plasma/look-and-feel/$LNF_ID" \
    "$LOCAL/icons/$ICONS_ID" "$LOCAL/wallpapers/$WALLPAPER_ID" "$LOCAL/color-schemes/$SCHEME_ID.colors"

log "rebuilding the systemd-boot initrds"
sdbootutil mkinitrd
[ -d "$STATE" ] && mv "$STATE" "$STATE.removed-$(date +%Y%m%d-%H%M%S)"
log "done"
