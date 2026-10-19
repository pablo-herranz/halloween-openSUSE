# GNOME (planned)

Not built yet. A GNOME edition would add, next to the shared pieces in
[`shared/`](../shared/) (wallpapers, icon theme, Plymouth boot splash,
Firefox theme):

- a GTK 3/4 theme and a GNOME Shell theme in the palette from
  [`art/palette.toml`](../art/palette.toml)
- a GDM login screen background
- `tools/targets/gnome*.py` build targets with `DESKTOP = "gnome"`, listed in
  [`tools/targets/__init__.py`](../tools/targets/__init__.py)
- install scripts for the GNOME parts

See [`docs/architecture.md`](../docs/architecture.md) for how targets fit
together, and open an issue before starting so the work can be coordinated.
