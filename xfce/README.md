# Xfce (planned)

Not built yet. An Xfce edition would add, next to the shared pieces in
[`shared/`](../shared/) (wallpapers, icon theme, Plymouth boot splash,
Firefox theme):

- an xfwm4 window manager theme and a GTK 3 theme in the palette from
  [`art/palette.toml`](../art/palette.toml)
- panel and LightDM greeter settings
- `tools/targets/xfce*.py` build targets with `DESKTOP = "xfce"`, listed in
  [`tools/targets/__init__.py`](../tools/targets/__init__.py)
- install scripts for the Xfce parts

See [`docs/architecture.md`](../docs/architecture.md) for how targets fit
together, and open an issue before starting so the work can be coordinated.
