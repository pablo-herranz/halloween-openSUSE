#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Install the per-user parts of halloween-openSUSE into ~/.local/share and
# switch the running Plasma session to them. Panels and widgets are kept.
# Safe to re-run; the first run saves the current settings for
# uninstall-user.sh.
set -euo pipefail
. "$(dirname "$0")/common.sh"
session_env

SRC=$BUILD_DIR/user
DATA=${XDG_DATA_HOME:-$HOME/.local/share}
STATE=$DATA/halloween-openSUSE
WALLPAPER_URL="file://$DATA/wallpapers/$WALLPAPER_ID#day-night"
[ -d "$SRC" ] || die "no build found at $SRC"

desktop_images() {
    plasma_script 'print(desktops().map(d => { d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]; return d.readConfig("Image") }).join("|"))'
}

save_state() {
    if [ -f "$STATE/user-state.env" ]; then
        log "keeping the settings saved by the first install"
        return
    fi
    log "saving current settings to $STATE"
    mkdir -p "$STATE/config-backup"
    for f in kdeglobals plasmarc ksplashrc kscreenlockerrc plasma-org.kde.plasma.desktop-appletsrc; do
        [ -f "$HOME/.config/$f" ] && cp -p "$HOME/.config/$f" "$STATE/config-backup/"
    done
    {
        printf 'LNF=%q\n' "$(kreadconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage --default $DEFAULT_LNF)"
        printf 'STYLE=%q\n' "$(kreadconfig6 --file plasmarc --group Theme --key name --default $DEFAULT_STYLE)"
        printf 'SCHEME=%q\n' "$(kreadconfig6 --file kdeglobals --group General --key ColorScheme --default $DEFAULT_SCHEME)"
        printf 'ICONS=%q\n' "$(kreadconfig6 --file kdeglobals --group Icons --key Theme --default $DEFAULT_ICONS)"
        printf 'SPLASH=%q\n' "$(kreadconfig6 --file ksplashrc --group KSplash --key Theme --default $DEFAULT_LNF)"
        printf 'LOCK_IMAGE=%q\n' "$(kreadconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image)"
        printf 'DESKTOP_IMAGES=%q\n' "$(desktop_images)"
    } > "$STATE/user-state.env"
}

install_files() {
    log "installing wallpaper, Plasma style, colour scheme and icons"
    install_tree "$SRC/wallpapers/$WALLPAPER_ID" "$DATA/wallpapers/$WALLPAPER_ID"
    install_tree "$SRC/plasma/desktoptheme/$STYLE_ID" "$DATA/plasma/desktoptheme/$STYLE_ID"
    install_tree "$SRC/icons/$ICONS_ID" "$DATA/icons/$ICONS_ID"
    mkdir -p "$DATA/color-schemes"
    cp "$SRC/color-schemes/$SCHEME_ID.colors" "$DATA/color-schemes/"

    log "installing look-and-feel $LNF_ID"
    local pkg=$SRC/plasma/look-and-feel/$LNF_ID
    apply kpackagetool6 -t Plasma/LookAndFeel -u "$pkg" 2>/dev/null \
        || apply kpackagetool6 -t Plasma/LookAndFeel -i "$pkg"
}

apply_theme() {
    log "applying look-and-feel (colours, icons, Plasma style, splash; panels untouched)"
    apply plasma-apply-lookandfeel -a "$LNF_ID"
    # Applied again explicitly: the look-and-feel skips pieces it thinks are current
    apply plasma-apply-desktoptheme "$STYLE_ID" || true
    apply plasma-apply-colorscheme "$SCHEME_ID" || true
    kwriteconfig6 --file kdeglobals --group Icons --key Theme "$ICONS_ID"
    [ -x /usr/libexec/plasma-changeicons ] && apply /usr/libexec/plasma-changeicons "$ICONS_ID" || true
    kwriteconfig6 --file ksplashrc --group KSplash --key Engine KSplashQML
    kwriteconfig6 --file ksplashrc --group KSplash --key Theme "$LNF_ID"

    log "setting the wallpaper on every desktop and the lock screen"
    plasma_script "desktops().forEach(d => { d.wallpaperPlugin = 'org.kde.image'; d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General']; d.writeConfig('Image', '$WALLPAPER_URL'); d.reloadConfig(); })"
    kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin org.kde.image
    kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image "$WALLPAPER_URL"
    kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key PreviewImage "$WALLPAPER_URL"
}

save_state
install_files
apply_theme
log "done. Undo with: $(dirname "$0")/uninstall-user.sh"
