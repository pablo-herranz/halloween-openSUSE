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

## Panel garland (widgets/panel-background overlay, tiled)

Aspect ratio 2:1:

> A thin horizontal autumn vine garland border that spans the full width,
> entering at the left edge and leaving at the right edge at exactly
> mid-height: a gently waving dark brown vine with small maple leaves in
> pumpkin orange (#E8751A), ember red (#B84A17) and candle gold (#F0B429),
> evenly spaced. Flat vector, few colours, no outlines, no gradients, no
> texture, no shadow, plain white background. No text, no lettering, no
> watermark, no signature.

Chose **2** (clearer wave): `garland.svg`. The tile is the garland followed
by its mirror image, so the ends always meet. It is drawn 12 px tall, so it
reads as a fine festive trim; coordinates are cut to 3 significant digits.

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
