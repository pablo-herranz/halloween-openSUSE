# 02 Splash and boot-splash chameleon

The chameleon from the concept sheet, alone, for the Plasma splash
(`hero.png`, 512 px) and the Plymouth watermark (300 px).

| Model | Settings | References |
|---|---|---|
| `gemini-3.1-flash-image` (Nano Banana 2) | 1K, 1:1, count 2, thinkingLevel high | `art/source/concept-sheet.png` |

Prompt:

> Using the chameleon character from the reference sheet (image 1), keeping
> exactly the same proportions, colours, floppy plum witch hat with
> burnt-orange band and striped pumpkin-orange and rust knitted scarf, draw
> one single full-body illustration of it: the chameleon in three-quarter
> view, sitting and hugging a carved jack-o'-lantern that glows warmly with
> candlelight, its long tail rolled into a tight spiral beside it, big
> friendly turret eyes looking at the viewer. Same cosy storybook gouache
> style and warm candle-lit light. Centred, the whole character, hat, tail
> and pumpkin fully visible with a generous empty margin all around. Plain
> flat solid magenta background (#FF00FF), perfectly even, no ground, no
> cast shadow, no gradient, no vignette, no other objects. No text, no
> lettering, no watermark, no signature.

## Result

Both matched the concept (mirror images of each other). Chose **A**:
pumpkin on the left, tail on the right.

## Post-processing

1. Picsart background removal (model `picsart-sod-v8-2`): clean edge, no
   magenta left in visible pixels.
2. `tools/cutout.py <cut-out.png> art/source/hero.png`:
   drops matting specks (alpha ≤ 16), removes magenta spill from soft edges,
   trims to the subject with 16 px padding (760x855).
