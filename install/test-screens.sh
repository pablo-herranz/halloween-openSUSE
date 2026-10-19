#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Show each themed screen in test mode and screenshot it into screenshots/
# next to this build. Run as the desktop user (also works over SSH).
#
# usage: test-screens.sh [desktop|splash|lock|sddm|widgets|dolphin|firefox|plymouth|all]
#   plymouth needs sudo and Plymouth's X11 renderer (not packaged on openSUSE:
#   there, test the boot splash by rebooting). It switches the default theme
#   only while the test runs and never touches the initrd.
#   firefox uses a throwaway profile; your own Firefox profiles are not touched.
set -euo pipefail
. "$(dirname "$0")/common.sh"
session_env

DATA=${XDG_DATA_HOME:-$HOME/.local/share}
OUT=$BUILD_DIR/screenshots
# The Plasma session's Wayland socket, not SSH's: the first one in the runtime dir
wayland_socket() {
    local s
    for s in "$XDG_RUNTIME_DIR"/wayland-[0-9]*; do
        case $s in *.lock) continue ;; esac
        [ -S "$s" ] && { basename "$s"; return; }
    done
}
WL=${WAYLAND_SESSION_SOCKET:-$(wayland_socket)}
[ -n "$WL" ] || die "no Wayland socket in $XDG_RUNTIME_DIR: is a Plasma session running?"
BASE_URL="file://$DATA/wallpapers/$WALLPAPER_ID"
mkdir -p "$OUT"

# Apps started from SSH need the session's desktop variables, or Qt skips
# KDE's platform theme and draws them with its default light palette
if pid=$(pgrep -u "$(id -u)" -x plasmashell | head -1); then
    while IFS= read -r -d '' var; do
        case $var in XDG_CURRENT_DESKTOP=*|KDE_FULL_SESSION=*|KDE_SESSION_VERSION=*|DESKTOP_SESSION=*) export "${var?}" ;; esac
    done < "/proc/$pid/environ"
fi

shot() {
    WAYLAND_DISPLAY=$WL spectacle -b -n -f -o "$OUT/$1.png"
    log "saved $OUT/$1.png"
}

set_wallpaper() {
    plasma_script "desktops().forEach(d => { d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General']; d.writeConfig('Image', '$1'); d.reloadConfig(); })" >/dev/null
}

xauth_file() { find "$XDG_RUNTIME_DIR" -maxdepth 1 -name 'xauth_*' -print -quit 2>/dev/null; }

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

widgets() {
    # An analog clock for the pumpkin face, removed again afterwards
    local id
    id=$(plasma_script 'var w = desktops()[0].addWidget("org.kde.plasma.analogclock", 1180, 140, 360, 360); print(w.id)')
    sleep 4
    shot clock
    plasma_script "desktops().forEach(d => d.widgets().forEach(w => { if (w.id == $id) w.remove() }))" >/dev/null
    # The app launcher, for the popup frame and its leaf sprig
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.activateLauncherMenu
    sleep 2
    shot kickoff
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.activateLauncherMenu
}

dolphin() {
    pgrep -u "$(id -u)" -x dolphin >/dev/null && die "close Dolphin first; this test closes the windows it opens"
    WAYLAND_DISPLAY=$WL command dolphin --new-window "$HOME" >/dev/null 2>&1 &
    sleep 9     # the first start with KDE's platform theme is slow
    shot dolphin
    pkill -u "$(id -u)" -x dolphin
    sleep 1

    # File type icons: a throwaway folder with one empty file of each kind
    local demo
    demo=$(mktemp -d -t halloween-file-types.XXXXXX)
    touch "$demo"/{notes.txt,letter.pdf,photo.png,song.mp3,film.mp4,backup.zip,page.html,script.py,data.json}
    printf '#!/bin/sh\n' > "$demo/program" && chmod +x "$demo/program"
    WAYLAND_DISPLAY=$WL command dolphin --new-window "$demo" >/dev/null 2>&1 &
    sleep 6
    shot dolphin-file-types
    pkill -u "$(id -u)" -x dolphin
    rm -rf "$demo"
}

firefox() {
    # Release Firefox only keeps signed add-ons, so the theme is loaded as a
    # temporary add-on over the remote debugging protocol, as web-ext does
    local profile port=6080 xpi=$BUILD_DIR/firefox/openSUSE-halloween.xpi
    [ -f "$xpi" ] || die "missing $xpi"
    profile=$(mktemp -d)
    # shellcheck disable=SC2064 # expand now: $profile is gone when the trap runs
    trap "pkill -u $(id -u) -f -- '--profile $profile' || true; sleep 2; rm -rf '$profile'" EXIT
    cat > "$profile/user.js" <<'EOF'
user_pref("devtools.chrome.enabled", true);
user_pref("devtools.debugger.remote-enabled", true);
user_pref("devtools.debugger.prompt-connection", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("browser.tabs.warnOnClose", false);
EOF
    echo '{"chrome://browser/content/browser.xhtml":{"main-window":{"sizemode":"maximized"}}}' > "$profile/xulstore.json"
    WAYLAND_DISPLAY=$WL command firefox --no-remote --profile "$profile" --start-debugger-server "$port" \
        https://en.wikipedia.org/wiki/Jack-o%27-lantern https://www.opensuse.org/ https://news.opensuse.org/ \
        https://en.opensuse.org/Portal:Tumbleweed https://en.wikipedia.org/wiki/Halloween about:addons >/dev/null 2>&1 &
    timeout 60 python3 - "$port" "$xpi" <<'EOF'
import json, socket, sys, time

port, xpi = int(sys.argv[1]), sys.argv[2]
for _ in range(30):
    try:
        sock = socket.create_connection(("127.0.0.1", port))
        break
    except OSError:
        time.sleep(1)
else:
    sys.exit("Firefox's debugger server did not start")
stream = sock.makefile("rb")

def receive():
    length = b""
    while (c := stream.read(1)) != b":":
        if not c:
            raise EOFError
        length += c
    return json.loads(stream.read(int(length)))

def request(to, kind, **args):
    data = json.dumps({"to": to, "type": kind, **args}).encode()
    sock.sendall(b"%d:%s" % (len(data), data))
    while (reply := receive()).get("from") != to:
        pass
    if "error" in reply:
        sys.exit(f"{kind}: {reply['error']}: {reply.get('message', '')}")
    return reply

receive()   # the greeting
addons = request("root", "getRoot")["addonsActor"]
print("loaded", request(addons, "installTemporaryAddon", addonPath=xpi)["addon"]["id"], flush=True)

# Close the debugger server's listener, or the URL bar keeps its striped
# "remote control" cue in the screenshot. This connection closes with it.
process = request("root", "getProcess", id=0)["processDescriptor"]["actor"]
console = request(process, "getTarget")["process"]["consoleActor"]
try:
    request(console, "evaluateJSAsync", text="""
        const { useDistinctSystemPrincipalLoader, releaseDistinctSystemPrincipalLoader } = ChromeUtils.importESModule(
            "resource://devtools/shared/loader/DistinctSystemPrincipalLoader.sys.mjs", { global: "shared" });
        const owner = {};
        useDistinctSystemPrincipalLoader(owner).require("resource://devtools/server/devtools-server.js")
            .DevToolsServer.closeAllSocketListeners();
        releaseDistinctSystemPrincipalLoader(owner);
    """)
    while receive().get("type") != "evaluationResult":
        pass
except EOFError:
    pass
time.sleep(1)
try:
    socket.create_connection(("127.0.0.1", port)).close()
    sys.exit("Firefox's debugger server is still listening")
except OSError:
    pass
EOF
    sleep 6     # the pages load and the window settles
    shot firefox
}

plymouth_test() {
    local renderer
    renderer=$(find /usr/lib64/plymouth/renderers /usr/lib/plymouth/renderers -name x11.so -print -quit 2>/dev/null)
    [ -n "$renderer" ] || die "Plymouth's X11 renderer isn't installed (openSUSE doesn't package it): test the boot splash by rebooting instead"
    local display=${DISPLAY:-:0} xauth previous log_file
    xauth=$(xauth_file)
    log_file=$(mktemp -t plymouth-test.XXXXXX)
    # plymouthd shows the default theme: switch it only for this test, and put
    # the old one back however the test ends ($previous is expanded right now,
    # because the trap runs after this function's locals are gone)
    previous=$(plymouth-set-default-theme)
    sudo plymouth-set-default-theme "$PLYMOUTH_ID"
    # shellcheck disable=SC2064
    trap "sudo plymouth quit 2>/dev/null; sudo plymouth-set-default-theme $(printf %q "$previous")" EXIT
    sudo env DISPLAY="$display" XAUTHORITY="$xauth" plymouthd --debug --debug-file="$log_file"
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
    log "debug log: $log_file"
}

case ${1:-all} in
    desktop|splash|lock|sddm|widgets|dolphin|firefox) "$1" ;;
    plymouth) plymouth_test ;;
    all) desktop; splash; lock; sddm; widgets; dolphin; firefox ;;
    *) die "usage: $0 [desktop|splash|lock|sddm|widgets|dolphin|firefox|plymouth|all]" ;;
esac
