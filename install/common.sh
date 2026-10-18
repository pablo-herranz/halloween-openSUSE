# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
# Shared settings and helpers for the install scripts. Sourced, not run.

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BUILD_DIR=$(cd "$HERE/.." && pwd)   # the deployed build/ tree: user/ root/ install/

LNF_ID=org.openSUSE.halloween.desktop
STYLE_ID=openSUSE-halloween
SCHEME_ID=openSUSEHalloween
ICONS_ID=openSUSE-halloween
WALLPAPER_ID=openSUSEhalloween
SDDM_ID=breeze-openSUSE-halloween
SDDM_BASE=breeze-openSUSE
PLYMOUTH_ID=openSUSE-halloween
SDDM_CONF=/etc/sddm.conf.d/zz-halloween-openSUSE.conf

# openSUSE defaults, used when no saved state exists
DEFAULT_LNF=org.openSUSE.desktop
DEFAULT_STYLE=openSUSE
DEFAULT_SCHEME=BreezeClassic
DEFAULT_ICONS=breeze
DEFAULT_WALLPAPER=file:///usr/share/wallpapers/openSUSEdefault

PATH=$PATH:/usr/sbin:/sbin

log() { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;31m!!\033[0m %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

# Reach the logged-in Plasma session's D-Bus, also when run over SSH
session_env() {
    local uid
    uid=$(id -u)
    export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$uid}
    export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}
}

# plasma-apply-* only need D-Bus; a Wayland or X socket inherited from SSH
# makes them try (and fail) to open a window
apply() { env -u WAYLAND_DISPLAY -u DISPLAY QT_QPA_PLATFORM=offscreen "$@"; }

# Run JavaScript in plasmashell and print its print() output
plasma_script() {
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$1"
}

# Replace a directory tree atomically enough for config files
install_tree() {
    local src=$1 dest=$2
    [ -d "$src" ] || die "missing $src"
    rm -rf "$dest.new"
    mkdir -p "$(dirname "$dest")"
    cp -R "$src" "$dest.new"
    rm -rf "$dest"
    mv "$dest.new" "$dest"
}
