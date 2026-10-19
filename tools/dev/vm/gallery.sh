#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Development helper: retake every README screenshot in the test VM (vm.sh),
# with the theme installed from a release tarball the way a package does and
# picked the way a user would. Run on the VM's host; `make gallery` runs it.
#
# usage: gallery.sh halloween-openSUSE-VERSION.tar.gz
# The screenshots land in $HALLOWEEN_VM/shots/gallery/, named as
# tools/previews.py expects.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
V=$HERE/vm.sh
VM=${HALLOWEEN_VM:-$HOME/vm-halloween}
OUT=$VM/shots/gallery
TARBALL=${1:?usage: gallery.sh halloween-openSUSE-VERSION.tar.gz}
export HALLOWEEN_VM_RES=1920x1080   # the README's screenshots are 16:9

log() { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
rm -rf "$OUT" && mkdir -p "$OUT"
"$V" stop 2>/dev/null || true
"$V" boot
"$V" install "$TARBALL"

log "KDE Plasma: the screens tools/dev/test-screens.sh takes"
"$V" desktop plasma
"$V" run "plasma-apply-lookandfeel -a org.openSUSE.halloween.desktop
          plasma-apply-colorscheme openSUSEHalloween
          plasma-apply-desktoptheme openSUSE-halloween
          \$(ls /usr/libexec/plasma-changeicons /usr/lib*/libexec/plasma-changeicons 2>/dev/null | head -1) openSUSE-halloween
          plasma-apply-wallpaperimage /usr/share/wallpapers/openSUSEhalloween
          kwriteconfig6 --file kscreenlockerrc --group Daemon --key Autolock false" >/dev/null
# test-screens.sh expects a build tree: its helpers in install/, the Firefox
# theme in firefox/ (the installed copy: logging in rebooted away /tmp)
"$V" ssh "rm -rf /tmp/gallery && mkdir -p /tmp/gallery/install /tmp/gallery/firefox \
          && cp /usr/lib64/firefox/browser/extensions/openSUSE-halloween@pluskal.org.xpi \
                /tmp/gallery/firefox/openSUSE-halloween.xpi"
scp -q -F "$VM/ssh_config" "$HERE/../common.sh" "$HERE/../test-screens.sh" vm:/tmp/gallery/install/
sleep 10
"$V" run "bash /tmp/gallery/install/test-screens.sh all"
scp -q -F "$VM/ssh_config" 'vm:/tmp/gallery/screenshots/*.png' "$OUT/"

log "GNOME: Files and the quick settings, and the app grid"
"$V" desktop gnome
"$V" key esc
"$V" run "nohup nautilus --new-window ~ >/dev/null 2>&1 &"
sleep 15
"$V" key meta_l s
sleep 4
"$V" shot gnome >/dev/null && mv "$VM/shots/gnome.png" "$OUT/"
"$V" key esc
"$V" key meta_l a
sleep 4
"$V" shot gnome-apps >/dev/null && mv "$VM/shots/gnome-apps.png" "$OUT/"
"$V" key esc

log "Xfce: the pieces picked in its settings, the Settings Manager and a notification"
"$V" desktop xfce
"$V" run "xfconf-query -c xsettings -p /Net/ThemeName -s openSUSE-halloween
          xfconf-query -c xsettings -p /Net/IconThemeName -s openSUSE-halloween-adwaita
          xfconf-query -c xfwm4 -p /general/theme -s openSUSE-halloween
          xfconf-query -c xfce4-notifyd -p /theme -n -t string -s openSUSE-halloween
          m=\$(ls /sys/class/drm | sed -n 's/^card[0-9]-//p' | head -1)
          for w in 0 1 2 3; do
              xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor\$m/workspace\$w/last-image -n -t string \
                  -s /usr/share/backgrounds/openSUSEhalloween/night.jpg
              xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor\$m/workspace\$w/image-style -n -t int -s 5
          done
          nohup xfce4-settings-manager >/dev/null 2>&1 &
          sleep 5
          notify-send -i folder-pictures 'Happy Halloween' 'The openSUSE Halloween theme is installed.'"
"$V" point 1500 900   # over the wallpaper: no tooltip in the shot
sleep 4
"$V" shot xfce >/dev/null && mv "$VM/shots/xfce.png" "$OUT/"

"$V" desktop gnome >/dev/null   # leave the VM where vm.sh create leaves it
ls -1 "$OUT"
