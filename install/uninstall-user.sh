#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Switch the session back to the settings saved by install-user.sh (or the
# openSUSE defaults), then remove the per-user halloween-openSUSE files.
set -euo pipefail
. "$(dirname "$0")/common.sh"
session_env

DATA=${XDG_DATA_HOME:-$HOME/.local/share}
STATE=$DATA/halloween-openSUSE
LNF=$DEFAULT_LNF STYLE=$DEFAULT_STYLE SCHEME=$DEFAULT_SCHEME ICONS=$DEFAULT_ICONS
SPLASH=$DEFAULT_LNF LOCK_IMAGE= DESKTOP_IMAGES=
if [ -f "$STATE/user-state.env" ]; then
    . "$STATE/user-state.env"
else
    warn "no saved settings found, restoring the openSUSE defaults"
fi

log "switching back to $LNF, $STYLE, $SCHEME, $ICONS"
apply plasma-apply-lookandfeel -a "$LNF"
apply plasma-apply-desktoptheme "$STYLE" || true
apply plasma-apply-colorscheme "$SCHEME" || true
kwriteconfig6 --file kdeglobals --group Icons --key Theme "$ICONS"
[ -x /usr/libexec/plasma-changeicons ] && apply /usr/libexec/plasma-changeicons "$ICONS" || true
kwriteconfig6 --file ksplashrc --group KSplash --key Theme "$SPLASH"

log "restoring wallpapers"
images=${DESKTOP_IMAGES:-$DEFAULT_WALLPAPER}
plasma_script "const saved = '$images'.split('|'); desktops().forEach((d, i) => { d.wallpaperPlugin = 'org.kde.image'; d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General']; d.writeConfig('Image', saved[Math.min(i, saved.length - 1)] || '$DEFAULT_WALLPAPER'); d.reloadConfig(); })"
lock_group=(--file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General)
if [ -n "$LOCK_IMAGE" ]; then
    kwriteconfig6 "${lock_group[@]}" --key Image "$LOCK_IMAGE"
    kwriteconfig6 "${lock_group[@]}" --key PreviewImage "$LOCK_IMAGE"
else
    kwriteconfig6 "${lock_group[@]}" --key Image --delete
    kwriteconfig6 "${lock_group[@]}" --key PreviewImage --delete
fi

log "removing files"
apply kpackagetool6 -t Plasma/LookAndFeel -r "$LNF_ID" 2>/dev/null || true
rm -rf "$DATA/wallpapers/$WALLPAPER_ID" "$DATA/plasma/desktoptheme/$STYLE_ID" \
    "$DATA/icons/$ICONS_ID" "$DATA/color-schemes/$SCHEME_ID.colors"
if [ -d "$STATE" ]; then
    mv "$STATE" "$STATE.removed-$(date +%Y%m%d-%H%M%S)"
    log "saved settings and config backups kept in $STATE.removed-*"
fi
log "done"
