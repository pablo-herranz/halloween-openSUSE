# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: GPL-2.0-or-later
"""What the build targets share: the palette, the art masters, and the list
of drawn placeholders used in place of missing masters."""

from functools import cached_property

from PIL import Image

import placeholders as ph
from common import ROOT, load_palette


class Context:
    def __init__(self):
        self.palette = load_palette()
        self.placeholders = []

    def master(self, name, make):
        """art/source/<name>.{png,jpg,webp} if present, otherwise make() a placeholder."""
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            f = ROOT / "art/source" / (name + ext)
            if f.exists():
                if f.read_bytes()[:40].startswith(b"version https://git-lfs"):
                    raise SystemExit(f"{f} is a Git LFS pointer: run `git lfs pull` first")
                return Image.open(f)
        self.placeholders.append(name)
        return make()

    @cached_property
    def wallpapers(self):
        """The dusk (light) and night (dark) wallpaper masters."""
        return {v: self.master(f"wallpaper-{v}", lambda v=v: ph.wallpaper(self.palette, v)).convert("RGB")
                for v in ("dusk", "night")}

    @cached_property
    def hero(self):
        return self.master("hero", lambda: ph.hero(self.palette)).convert("RGBA")

    @cached_property
    def lanterns(self):
        """(lit, unlit) pumpkin lanterns; both share one outline."""
        p = self.palette
        return (self.master("lantern-lit", lambda: ph.pumpkin(p, 192, lit=True)).convert("RGBA"),
                self.master("lantern-unlit", lambda: ph.pumpkin(p, 192, lit=False)).convert("RGBA"))
