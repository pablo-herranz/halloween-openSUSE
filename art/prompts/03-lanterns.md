# 03 Pumpkin lanterns

The five lanterns in the Plasma splash light up one by one, so the lit and
unlit versions must have exactly the same outline.

## Lit

| Model | Settings | References |
|---|---|---|
| `gemini-3.1-flash-image` | 1K, 1:1, count 2 | concept sheet (for style) |

> A single small carved jack-o'-lantern pumpkin, in the same cosy storybook
> gouache style as the jack-o'-lantern in the reference image (image 1).
> Seen from the front, round and slightly squat, warm pumpkin-orange with
> soft ribs, a short curly green-brown stem with one small leaf and a curl of
> vine. Friendly smiling carved face with triangle eyes, glowing warm golden
> from a candle inside. Only the pumpkin: no chameleon, no animal, no hat, no
> other objects. Centred, the whole pumpkin fully visible with a generous
> empty margin all around. Plain flat solid magenta background (#FF00FF),
> perfectly even, no ground, no cast shadow, no gradient, no vignette. No
> text, no lettering, no watermark, no signature.

A came out photo-realistic; chose **B**, which matches the gouache style.

## Unlit

An edit of lit B, so the shape stays the same.

| Model | Settings | References |
|---|---|---|
| `gemini-3.1-flash-image` | 1K, 1:1, count 1 | lit B |

> Edit image 1: the very same carved jack-o'-lantern pumpkin, keeping
> exactly the same shape, size, position, stem, leaves, vine curl, carved
> face and storybook gouache style, but with the candle blown out. The carved
> eyes, nose and mouth are now dark, deep shadowy brown-black openings with
> no glow, and the pumpkin skin no longer has any warm inner light, just soft
> even daylight. Keep the plain flat solid magenta background (#FF00FF)
> exactly as it is, no ground, no cast shadow. No text, no lettering, no
> watermark, no signature.

The outlines differ by 256 of 1,048,576 pixels.

## Post-processing

1. `picsart_remove_bg` on lit B.
2. `tools/cutout.py lit-b-cut.png art/source/lantern-lit.png`
3. `tools/cutout.py lit-b-cut.png art/source/lantern-unlit.png --colour-from unlit-b.png`:
   the unlit master reuses the lit cut-out's alpha, so both line up exactly
   (653x659).
