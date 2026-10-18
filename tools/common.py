# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""Paths, palette access and small helpers shared by the build tools."""

import hashlib
import re
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
CACHE = BUILD / "cache"
VERSION = "2026.10.0"


def load_palette():
    """Return {name: "#RRGGBB"} with [roles] resolved to colours."""
    data = tomllib.loads((ROOT / "art/palette.toml").read_text())
    colors = {k: v.upper() for k, v in data["colors"].items()}
    for role, value in data.get("roles", {}).items():
        colors[role] = colors.get(value, value).upper()
    return colors


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(color):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in (rgb(color) if isinstance(color, str) else color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def fill_tokens(text, values, fmt=lambda v: v):
    """Replace every @name@ token; fail loudly on unknown ones."""
    def sub(m):
        name = m.group(1)
        if name not in values:
            raise KeyError(f"unknown token @{name}@")
        return fmt(values[name])
    return re.sub(r"@([A-Za-z_][A-Za-z0-9_]*)@", sub, text)


def fetch(url, sha256, dest):
    """Download url to dest once, verifying its pinned SHA-256."""
    dest = Path(dest)
    if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest() != sha256:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=30) as r:
            data = r.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != sha256:
            raise RuntimeError(f"{url}: SHA-256 {digest} does not match the pin {sha256}")
        dest.write_bytes(data)
    return dest


def write(path, content, mode=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)
    if mode is not None:
        path.chmod(mode)
    return path
