#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Show each themed screen in test mode and screenshot it into screenshots/
# next to this build. Run as the desktop user (also works over SSH).
#
# usage: test-screens.sh [desktop|splash|lock|sddm|plymouth|all]
#   plymouth needs sudo and the plymouth-x11-renderer package; it switches the
#   default theme only while the test runs and never touches the initrd.
set -euo pipefail
. "$(dirname "$0")/common.sh"
session_env

DATA=${XDG_DATA_HOME:-$HOME/.local/share}
OUT=$BUILD_DIR/screenshots
WL=${WAYLAND_SESSION_SOCKET:-wayland-1}   # the Plasma session's socket, not SSH's
BASE_URL="file://$DATA/wallpapers/$WALLPAPER_ID"
mkdir -p "$OUT"

shot() {
    WAYLAND_DISPLAY=$WL spectacle -b -n -f -o "$OUT/$1.png"
    log "saved $OUT/$1.png"
}

set_wallpaper() {
    plasma_script "desktops().forEach(d => { d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General']; d.writeConfig('Image', '$1'); d.reloadConfig(); })" >/dev/null
}

xauth_file() { ls "$XDG_RUNTIME_DIR"/xauth_* 2>/dev/null | head -1; }

desktop() {
    for variant in light dark; do
        set_wallpaper "$BASE_URL#$variant"
        sleep 3
        shot "desktop-$variant"
    done
    set_wallpaper "$BASE_URL#day-night"
}

splash() {
    WAYLAND_DISPLAY=$WL ksplashqml --test "$LNF_ID" &
    local pid=$!
    sleep 3.5
    shot splash
    wait "$pid" 2>/dev/null || true
}

lock() {
    WAYLAND_DISPLAY=$WL /usr/libexec/kscreenlocker_greet --testing &
    local pid=$!
    sleep 4
    shot lockscreen
    kill "$pid" 2>/dev/null || true
}

sddm() {
    WAYLAND_DISPLAY=$WL sddm-greeter-qt6 --test-mode --theme "/usr/share/sddm/themes/$SDDM_ID" &
    local pid=$!
    sleep 5
    shot sddm
    kill "$pid" 2>/dev/null || true
}

plymouth() {
    rpm -q plymouth-x11-renderer >/dev/null || die "install plymouth-x11-renderer first"
    local display=${DISPLAY:-:0} xauth previous
    xauth=$(xauth_file)
    # plymouthd shows the default theme: switch it only for this test
    previous=$(plymouth-set-default-theme)
    sudo plymouth-set-default-theme "$PLYMOUTH_ID"
    trap 'sudo plymouth quit 2>/dev/null; sudo plymouth-set-default-theme "$previous"' EXIT
    sudo env DISPLAY="$display" XAUTHORITY="$xauth" plymouthd --debug --debug-file=/tmp/plymouth-test.log
    sudo plymouth show-splash
    sleep 4
    shot plymouth-boot
    sudo plymouth display-message --text="Happy Halloween"
    sleep 1
    shot plymouth-message
    sudo plymouth ask-for-password --prompt="Disk password (test only)" >/dev/null &
    sleep 2
    shot plymouth-password
    sudo plymouth quit
    log "debug log: /tmp/plymouth-test.log"
}

case ${1:-all} in
    desktop|splash|lock|sddm|plymouth) "$1" ;;
    all) desktop; splash; lock; sddm ;;
    *) die "usage: $0 [desktop|splash|lock|sddm|plymouth|all]" ;;
esac
