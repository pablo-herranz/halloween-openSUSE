#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Talk to the test VM's QEMU monitor (QMP), for vm.sh.

usage: qmp.py SOCKET shot FILE.png | key KEY... | point X Y | click X Y | quit
Keys are QEMU qcodes (esc, ret, meta_l, s, …); X Y are pixels of the VM's
display ($HALLOWEEN_VM_RES, 1920x1080 by default), sent through its USB tablet.
"""

import json
import os
import socket
import sys

WIDTH, HEIGHT = (int(v) for v in os.environ.get("HALLOWEEN_VM_RES", "1920x1080").split("x"))


def main():
    sock, what, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    s = socket.socket(socket.AF_UNIX)
    s.connect(sock)
    f = s.makefile("rw")

    def cmd(name, **arguments):
        f.write(json.dumps({"execute": name, **({"arguments": arguments} if arguments else {})}) + "\n")
        f.flush()
        while True:
            reply = json.loads(f.readline())
            if "return" in reply or "error" in reply:
                if "error" in reply:
                    sys.exit(f"qmp {name}: {reply['error']['desc']}")
                return reply

    json.loads(f.readline())  # greeting
    cmd("qmp_capabilities")
    if what == "shot":
        cmd("screendump", filename=args[0], format="png")
    elif what == "key":
        cmd("send-key", keys=[{"type": "qcode", "data": k} for k in args])
    elif what in ("point", "click"):
        x, y = (round(int(v) / size * 32767) for v, size in zip(args, (WIDTH, HEIGHT), strict=True))
        cmd("input-send-event", events=[{"type": "abs", "data": {"axis": "x", "value": x}},
                                        {"type": "abs", "data": {"axis": "y", "value": y}}])
        for down in (True, False) if what == "click" else ():
            cmd("input-send-event", events=[{"type": "btn", "data": {"down": down, "button": "left"}}])
    elif what == "quit":
        cmd("quit")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
