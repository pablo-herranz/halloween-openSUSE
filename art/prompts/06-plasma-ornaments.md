# 06 Plasma style ornaments

`recraftv4_1_utility_vector` (SVG), no reference, count 2 each.
`tools/vectors.py` turns them into the ornaments that `tools/plasma_style.py`
places into Breeze's SVGs.

## Popup sprig (dialogs/background overlay, top right)

> A small decorative autumn corner sprig for a user interface: three maple
> leaves in pumpkin orange (#E8751A), ember red (#B84A17) and candle gold
> (#F0B429) on a short dark brown twig with two small plum berries (#A77BCA),
> the twig coming in diagonally from the top-right corner. Flat vector, few
> colours, no outlines, no gradients, no texture, no shadow, plain white
> background. No text, no lettering, no watermark, no signature.

Chose **2** (adds a gold leaf): `sprig.svg`, cropped to its content. Its
backdrop comes in several pieces where the twig touches the edge; white
pieces touching the canvas edge are dropped.

## Panel garland (dropped)

A tiled vine garland along the panel's top edge, from a 2:1
`recraftv4_1_utility_vector` render ("a thin horizontal autumn vine garland
border that spans the full width …"). On the real panel it read as
a busy dotted line and the owner found it disruptive, so it was removed on
2026-10-19: the panel keeps Breeze's plain frame in the autumn colours.

## Clock face (widgets/clock.svg `ClockFace`)

> A pumpkin seen straight from the front as a perfectly round, symmetrical
> flat disc, for use as an analog clock dial: warm pumpkin-orange (#E8751A)
> with soft lighter and darker vertical ribs, a short dark green-brown stem
> at the top, no carved face, nothing in the centre. Flat vector, few
> colours, no outlines, no gradients, no texture, no shadow, centred, filling
> the square with a small margin, plain white background. No text, no
> numbers, no lettering, no watermark, no signature.

Chose **1** (more ribs): `clock.svg`. The pumpkin body (not the stem) is
centred on (100, 100) of a 200x200 element, because the hands turn around
its centre; twelve candle notches are drawn on top.
