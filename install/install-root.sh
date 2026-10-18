#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Install the system parts of halloween-openSUSE. Needs root.
#   - Plasma style, colour scheme, icons, wallpaper and look-and-feel in
#     /usr/local/share, so the login screen and other users can use them
#   - the SDDM theme (selected in /etc/sddm.conf.d) and the greeter's colours
#   - the Plymouth theme files; the theme is NOT made the default, because any
#     later initrd rebuild (kernel update, zypper dup) would then boot with it
#
# usage: install-root.sh             install, and switch the login screen to the theme
#        install-root.sh --files     install only, switch nothing (for test mode)
#        install-root.sh --plymouth  after the Plymouth test: make the boot splash
#                                    the default and rebuild the initrds
set -euo pipefail
. "$(dirname "$0")/common.sh"
[ "$(id -u)" = 0 ] || die "run as root: sudo $0 $*"

STATE=/var/lib/halloween-openSUSE
LOCAL=/usr/local/share
SDDM_THEMES=/usr/share/sddm/themes
PLYMOUTH_THEMES=/usr/share/plymouth/themes
SDDM_HOME=$(getent passwd sddm | cut -d: -f6)
SRC=$BUILD_DIR

MODE=${1:-all}
case $MODE in all|--files|--plymouth) ;; *) die "usage: $0 [--files|--plymouth]" ;; esac
[ -d "$SRC/root" ] || die "no build found at $SRC/root"

save_state() {
    mkdir -p "$STATE"
    [ -f "$STATE/root-state.env" ] && return
    log "saving current Plymouth theme and greeter settings to $STATE"
    printf 'PLYMOUTH_THEME=%q\n' "$(plymouth-set-default-theme)" > "$STATE/root-state.env"
    for f in kdeglobals plasmarc; do
        if [ -f "$SDDM_HOME/.config/$f" ]; then
            cp -p "$SDDM_HOME/.config/$f" "$STATE/sddm-$f"
        else
            touch "$STATE/sddm-$f.absent"
        fi
    done
}

install_shared() {
    log "installing shared pieces in $LOCAL"
    install_tree "$SRC/user/plasma/desktoptheme/$STYLE_ID" "$LOCAL/plasma/desktoptheme/$STYLE_ID"
    install_tree "$SRC/user/plasma/look-and-feel/$LNF_ID" "$LOCAL/plasma/look-and-feel/$LNF_ID"
    install_tree "$SRC/user/icons/$ICONS_ID" "$LOCAL/icons/$ICONS_ID"
    install_tree "$SRC/user/wallpapers/$WALLPAPER_ID" "$LOCAL/wallpapers/$WALLPAPER_ID"
    install -D -m 644 "$SRC/user/color-schemes/$SCHEME_ID.colors" "$LOCAL/color-schemes/$SCHEME_ID.colors"
    chmod -R u=rwX,go=rX "$LOCAL/plasma/desktoptheme/$STYLE_ID" "$LOCAL/plasma/look-and-feel/$LNF_ID" \
        "$LOCAL/icons/$ICONS_ID" "$LOCAL/wallpapers/$WALLPAPER_ID"
}

install_sddm() {
    local base=$SDDM_THEMES/$SDDM_BASE theme=$SDDM_THEMES/$SDDM_ID
    [ -f "$base/Main.qml" ] || die "$base not found (is sddm-theme-openSUSE installed?)"
    log "building SDDM theme $SDDM_ID on top of $SDDM_BASE"
    rm -rf "$theme"
    mkdir -p "$theme"
    # Link the QML so updates of breeze-openSUSE keep flowing in
    for f in "$base"/*; do
        case $(basename "$f") in
            metadata.desktop|theme.conf|theme.conf.user|preview.png) ;;
            *) ln -s "$f" "$theme/$(basename "$f")" ;;
        esac
    done
    cp "$SRC/root/sddm/$SDDM_ID/metadata.desktop" "$SRC/root/sddm/$SDDM_ID/background.jpg" \
        "$SRC/root/sddm/$SDDM_ID/preview.png" "$theme/"
    cp "$base/theme.conf" "$theme/theme.conf"
    local group=General key value
    while IFS= read -r line; do
        case $line in
            ''|'#'*) ;;
            '['*']') group=${line#[}; group=${group%]} ;;
            *=*) key=${line%%=*} value=${line#*=}
                 kwriteconfig6 --file "$theme/theme.conf" --group "$group" --key "$key" "$value" ;;
        esac
    done < "$SRC/root/sddm/$SDDM_ID/theme.conf.overrides"
    chmod -R u=rwX,go=rX "$theme"
}

activate_sddm() {
    log "switching the login screen to $SDDM_ID"
    printf '[Theme]\nCurrent=%s\n' "$SDDM_ID" > "$SDDM_CONF"
    chmod 644 "$SDDM_CONF"

    log "giving the login screen the autumn colours, icons and Plasma style"
    install -d -o sddm -g sddm "$SDDM_HOME/.config"
    install -o sddm -g sddm -m 644 "$SRC/user/color-schemes/$SCHEME_ID.colors" "$SDDM_HOME/.config/kdeglobals"
    kwriteconfig6 --file "$SDDM_HOME/.config/kdeglobals" --group Icons --key Theme "$ICONS_ID"
    kwriteconfig6 --file "$SDDM_HOME/.config/plasmarc" --group Theme --key name "$STYLE_ID"
    chown sddm:sddm "$SDDM_HOME/.config/kdeglobals" "$SDDM_HOME/.config/plasmarc"
}

install_plymouth() {
    local theme=$PLYMOUTH_THEMES/$PLYMOUTH_ID
    log "installing Plymouth theme $PLYMOUTH_ID"
    install_tree "$SRC/root/plymouth/$PLYMOUTH_ID" "$theme"
    # Password dialog images come from the stock spinner theme
    for f in entry bullet lock keyboard keymap-render capslock; do
        cp "$PLYMOUTH_THEMES/spinner/$f.png" "$theme/"
    done
    chmod -R u=rwX,go=rX "$theme"
}

activate_plymouth() {
    [ -f "$PLYMOUTH_THEMES/$PLYMOUTH_ID/$PLYMOUTH_ID.plymouth" ] || die "install the theme first: $0"
    log "making $PLYMOUTH_ID the default boot splash and rebuilding the systemd-boot initrds"
    plymouth-set-default-theme "$PLYMOUTH_ID"
    sdbootutil mkinitrd
}

save_state
if [ "$MODE" = --plymouth ]; then
    activate_plymouth
    log "done. The boot splash shows from the next boot."
    exit 0
fi
install_shared
install_sddm
install_plymouth
[ "$MODE" = all ] && activate_sddm
if command -v restorecon >/dev/null && command -v getenforce >/dev/null && [ "$(getenforce)" != Disabled ]; then
    restorecon -R "$LOCAL" "$SDDM_THEMES/$SDDM_ID" "$PLYMOUTH_THEMES/$PLYMOUTH_ID" "$SDDM_HOME/.config"
fi
if [ "$MODE" = all ]; then
    log "done. The new login screen shows after logout or reboot."
else
    log "done. Files installed; nothing switched. Run $0 to switch the login screen."
fi
log "The boot splash is installed but not active: test it, then run $0 --plymouth"
