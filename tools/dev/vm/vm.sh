#!/bin/bash
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Development helper: a throwaway openSUSE Tumbleweed VM with GNOME and Xfce,
# for trying the theme on desktops other than your own. It runs headless on
# any x86_64 Linux host with KVM and QEMU:
#   sudo zypper in --no-recommends qemu-x86 qemu-tools qemu-hw-display-virtio-vga xorriso
# Everything lives in $HALLOWEEN_VM (default ~/vm-halloween). The VM's SSH is
# on 127.0.0.1:$HALLOWEEN_VM_PORT (default 2222) with a key made for it, and
# screenshots come from QEMU's monitor, so no display is needed.
#
# usage: vm.sh create               download and verify the cloud image, make the
#                                   disk and cloud-init seed, boot, install the desktops
#        vm.sh boot | stop          start the VM / shut it down
#        vm.sh ssh [CMD]            a shell, or CMD, in the VM as user geeko
#        vm.sh run CMD              CMD inside the logged-in desktop session
#        vm.sh install TARBALL      install a release tarball (make dist) the way a
#                                   package does, with its defaults
#        vm.sh desktop gnome|xfce   log in to that desktop automatically (reboots)
#        vm.sh shot NAME            screenshot to $HALLOWEEN_VM/shots/NAME.png
#        vm.sh key KEY...           press keys (QEMU qcodes: esc, ret, meta_l, s, …)
#        vm.sh click X Y            click at pixels X Y of the 1920x1080 display
set -euo pipefail

VM=${HALLOWEEN_VM:-$HOME/vm-halloween}
PORT=${HALLOWEEN_VM_PORT:-2222}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
IMAGES=https://download.opensuse.org/tumbleweed/appliances
IMAGE=openSUSE-Tumbleweed-Minimal-VM.x86_64-Cloud.qcow2
# The desktops, plus what the minimal image lacks for a usable session
PATTERNS="gnome_basis xfce_basis x11"
PACKAGES="gdm lightdm lightdm-gtk-greeter gnome-shell-extension-user-theme xdg-desktop-portal-gnome"
PACKAGES+=" nautilus gnome-console xfce4-notifyd xfce4-terminal make rsync"

log() { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
vssh() { ssh -F "$VM/ssh_config" vm "$@"; }
qmp() { python3 "$HERE/qmp.py" "$VM/qmp.sock" "$@"; }

wait_ssh() {
    for _ in $(seq 1 120); do
        vssh true 2>/dev/null && return
        sleep 5
    done
    die "the VM didn't come up; see $VM/serial.log"
}

wait_session() {  # wait_session PROCESS: until the desktop runs, plus time to settle
    for _ in $(seq 1 60); do
        vssh "pgrep -u geeko -x $1 >/dev/null" 2>/dev/null && { sleep 15; return; }
        sleep 5
    done
    die "no $1 session started"
}

boot() {
    [ -e "$VM/qemu.pid" ] && kill -0 "$(cat "$VM/qemu.pid")" 2>/dev/null && { log "already running"; return; }
    log "booting the VM"
    qemu-system-x86_64 -enable-kvm -cpu host -smp 4 -m 4G -machine q35 \
        -drive if=virtio,file="$VM/disk.qcow2" -drive if=virtio,format=raw,readonly=on,file="$VM/seed.iso" \
        -nic user,model=virtio-net-pci,hostfwd=tcp:127.0.0.1:"$PORT"-:22 \
        -device virtio-vga,xres=1920,yres=1080 -device qemu-xhci -device usb-kbd -device usb-tablet \
        -display none -serial file:"$VM/serial.log" \
        -qmp unix:"$VM/qmp.sock",server=on,wait=off -pidfile "$VM/qemu.pid" -daemonize
    wait_ssh
}

create() {
    [ -e "$VM/disk.qcow2" ] && die "$VM/disk.qcow2 exists; remove $VM to start over"
    mkdir -p "$VM/seed"
    log "downloading $IMAGE"
    curl -sSfL -o "$VM/$IMAGE" "$IMAGES/$IMAGE"
    curl -sSf -o "$VM/$IMAGE.sha256" "$IMAGES/$IMAGE.sha256"
    (cd "$VM" && sha256sum -c "$IMAGE.sha256")
    qemu-img create -q -f qcow2 -F qcow2 -b "$VM/$IMAGE" "$VM/disk.qcow2" 30G
    ssh-keygen -q -t ed25519 -N '' -C halloween-vm -f "$VM/id"
    cat > "$VM/seed/user-data" <<EOF
#cloud-config
users:
  - name: geeko
    groups: [wheel]
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    shell: /bin/bash
    ssh_authorized_keys:
      - $(cat "$VM/id.pub")
EOF
    printf 'instance-id: halloween-vm\nlocal-hostname: halloween-vm\n' > "$VM/seed/meta-data"
    xorriso -as mkisofs -quiet -o "$VM/seed.iso" -V cidata -J -r "$VM/seed/"
    cat > "$VM/ssh_config" <<EOF
Host vm
  HostName 127.0.0.1
  Port $PORT
  User geeko
  IdentityFile $VM/id
  UserKnownHostsFile $VM/known_hosts
  StrictHostKeyChecking accept-new
  ConnectTimeout 5
EOF
    boot
    log "updating the VM and installing GNOME and Xfce"
    vssh "sudo zypper -n --quiet dup --no-recommends && sudo zypper -n --quiet in -t pattern $PATTERNS \
          && sudo zypper -n --quiet in $PACKAGES"
    # Test-machine settings only: no idle lock, blanking or welcome tour
    vssh "sudo tee /usr/share/glib-2.0/schemas/99_halloween-vm.gschema.override >/dev/null && sudo glib-compile-schemas /usr/share/glib-2.0/schemas" <<'EOF'
[org.gnome.desktop.session]
idle-delay=uint32 0
[org.gnome.desktop.screensaver]
lock-enabled=false
[org.gnome.shell]
welcome-dialog-last-shown-version='999'
[org.gnome.settings-daemon.plugins.power]
sleep-inactive-ac-type='nothing'
[org.gnome.desktop.interface]
enable-animations=false
EOF
    # shellcheck disable=SC2016  # expanded in the VM
    vssh 'mkdir -p ~/.config Desktop Documents Downloads Music Pictures Videos Public Templates
          for d in DESKTOP:Desktop DOCUMENTS:Documents DOWNLOAD:Downloads MUSIC:Music PICTURES:Pictures \
                   VIDEOS:Videos PUBLICSHARE:Public TEMPLATES:Templates; do
              printf "XDG_%s_DIR=\"\$HOME/%s\"\n" "${d%%:*}" "${d#*:}"
          done > ~/.config/user-dirs.dirs
          sudo systemctl set-default graphical.target'
    desktop gnome
}

desktop() {
    case ${1:-} in
        gnome) dm=gdm session=gnome process=gnome-shell ;;
        xfce) dm=lightdm session=xfce process=xfdesktop ;;
        *) die "usage: vm.sh desktop gnome|xfce" ;;
    esac
    log "logging in to $session automatically with $dm"
    vssh "printf '[User]\nSession=$session\nSystemAccount=false\n' | sudo tee /var/lib/AccountsService/users/geeko >/dev/null
          sudo sed -i -e 's/^DISPLAYMANAGER=.*/DISPLAYMANAGER=\"$dm\"/' \
                      -e 's/^DISPLAYMANAGER_AUTOLOGIN=.*/DISPLAYMANAGER_AUTOLOGIN=\"geeko\"/' /etc/sysconfig/displaymanager
          sudo mkdir -p /etc/lightdm/lightdm.conf.d
          printf '[Seat:*]\nautologin-user=geeko\nautologin-session=xfce\nuser-session=xfce\n' \
              | sudo tee /etc/lightdm/lightdm.conf.d/90-halloween-vm.conf >/dev/null
          sudo systemctl disable gdm.service lightdm.service 2>/dev/null
          sudo systemctl enable --force $dm.service 2>/dev/null
          sudo systemctl reboot" || true
    sleep 30
    wait_ssh
    wait_session "$process"
}

install_tarball() {
    local tarball=${1:?usage: vm.sh install halloween-openSUSE-VERSION.tar.gz} name
    name=$(basename "$tarball" .tar.gz)
    log "installing $name like a package, with its defaults"
    scp -q -F "$VM/ssh_config" "$tarball" vm:/tmp/
    vssh "cd /tmp && rm -rf $name && tar xzf $name.tar.gz && cd $name \
          && sudo make uninstall >/dev/null && sudo make install install-defaults >/dev/null \
          && sudo glib-compile-schemas /usr/share/glib-2.0/schemas && sudo dconf update \
          && for t in /usr/share/icons/openSUSE-halloween*; do sudo gtk-update-icon-cache -q -f \$t; done"
}

run() {  # in the session, with its environment
    vssh "pid=\$(pgrep -u geeko -x gnome-shell || pgrep -u geeko -x xfce4-session) || { echo 'no desktop session' >&2; exit 1; }
          while IFS= read -r -d '' v; do
              case \$v in XDG_CURRENT_DESKTOP=*|WAYLAND_DISPLAY=*|DISPLAY=*|XAUTHORITY=*|DBUS_SESSION_BUS_ADDRESS=*|XDG_SESSION_TYPE=*|XDG_RUNTIME_DIR=*) export \"\$v\" ;; esac
          done < /proc/\$(echo \$pid | cut -d' ' -f1)/environ
          $*"
}

cmd=${1:-}
shift || true
case $cmd in
    create) create ;;
    boot) boot ;;
    stop) vssh 'sudo systemctl poweroff' 2>/dev/null || qmp quit ;;
    ssh) vssh "$@" ;;
    run) run "$@" ;;
    install) install_tarball "$@" ;;
    desktop) desktop "$@" ;;
    shot) mkdir -p "$VM/shots" && qmp shot "$VM/shots/${1:?usage: vm.sh shot NAME}.png" && echo "$VM/shots/$1.png" ;;
    key) qmp key "$@" ;;
    click) qmp click "$@" ;;
    *) sed -n '/^# usage:/,/^set -euo/p' "$0" | sed '$d; s/^# \{0,1\}//' >&2; exit 2 ;;
esac
