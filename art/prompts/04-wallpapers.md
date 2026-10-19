# 04 Wallpapers

Composition rules: the chameleon in the right third; calm sky on the left
and in the centre for desktop icons; the bottom tenth quiet for the panel;
nothing important outside the central 90% of the width (the 16:10 crop).

## Dusk drafts (1K)

Same prompt for both models, concept sheet as the reference:

| Model | Settings | Drafts |
|---|---|---|
| `flux-2-pro` | 1K, 16:9, count 2 | A, B |
| `gemini-3.1-flash-image` | 1K, 16:9, count 2 | C, D |

> Wide cosy autumn Halloween landscape illustration in soft storybook
> gouache style, for a desktop wallpaper. Dusk in a misty birch forest
> clearing: a big warm harvest moon rising low over soft rolling hills, the
> sky fading from deep plum at the top to apricot and amber near the
> horizon, maple leaves in rust, pumpkin-orange and gold drifting through the
> air. In the right third of the picture, the chameleon character from the
> reference image (image 1), with the same green body, plum witch hat and
> striped knitted scarf, sits on a curved mossy birch branch with its tail
> curled in a spiral, beside a few carved jack-o'-lanterns glowing with
> candlelight. The left two-thirds and the centre are calm open sky and
> gentle mist with no detailed objects. The bottom tenth is a quiet, dark,
> simple foreground of grass and fallen leaves. Calm, friendly, not scary.
> No text, no lettering, no watermark, no signature.

| | Notes |
|---|---|
| A | Already night; pumpkins clutter the left |
| B | Calm, but a small chameleon and pumpkins cut off by the 16:10 crop |
| C | Lovely sky, but the chameleon and pumpkins sit outside the 16:10 crop |
| D | Best fit: chameleon at 72–93% of the width, calm left and centre, quiet bottom |

## Night drafts (1K), from dusk D

| Model | Settings | References | Drafts |
|---|---|---|---|
| `gemini-3.1-flash-image` | 1K, 16:9, count 2 | dusk D, concept sheet | E, F |

> Edit image 1 into the very same scene at night. Keep exactly the same
> composition and framing: the same birch trees, hills, mossy branch, the
> chameleon (same character as image 2) in the same pose and position, the
> same jack-o'-lanterns, and the moon in the same place. Change only the
> time of day: now it is a deep, calm moonlit night. The sky is a deep
> plum-black night sky fading to dusky aubergine near the hills, with a few
> faint stars. The moon glows pale cream-gold with a soft halo. A soft
> silvery mist lies over the hills. The jack-o'-lanterns glow brightly with
> warm orange candlelight, casting a warm rim light on the chameleon's face,
> scarf and the branch. A few maple leaves still drift. Same cosy storybook
> gouache style. The left two-thirds stay calm and uncluttered and the
> bottom tenth stays dark and quiet. Friendly, not scary. No text, no
> lettering, no watermark, no signature.

| | Notes |
|---|---|
| E | Same composition as D, stars, glowing lanterns |
| F | Same, but candle flames stick out of the pumpkin tops |

Chosen: **D** (dusk) and **E** (night).

## 4K finals

| Model | Settings | References |
|---|---|---|
| `gemini-3.1-flash-image` | 4K (5504x3072), 16:9, count 2 | dusk D, concept sheet |
| `gemini-3.1-flash-image` | 4K (5504x3072), 16:9, count 2 | dusk final, night E, concept sheet |

Dusk prompt:

> Re-create image 1 as a high-resolution final for a 4K desktop wallpaper.
> Keep it exactly the same picture: the same composition and framing, every
> birch tree, branch, hill, leaf, the moon and the three jack-o'-lanterns in
> the same place and size, the same colours and dusk light. The chameleon is
> the character from image 2 and stays in the same pose and position as in
> image 1, with the same green body, plum witch hat with burnt-orange band
> and striped knitted scarf. Only add fine detail: crisp clean outlines, soft
> gouache paper texture, smooth even sky gradients without banding or noise.
> No text, no lettering, no watermark, no signature.

Night prompt: the night draft prompt above, with image 1 the dusk final,
"matching the night lighting and colours of image 2" (night E), the
chameleon from image 3, and "crisp clean outlines, smooth even sky gradients
without banding or noise".

Both pairs stayed close to the drafts (mean colour difference 4.5–5.4 of 255
at draft size). Chosen: dusk **#2** (smoother sky than #1) as
`art/source/wallpaper-dusk.png`, night **#1** (closest to E, warmer lantern
light on the face) as `art/source/wallpaper-night.png`. The night final lines
up with the dusk final better than draft E did, so Plasma's day/night switch
keeps everything in place.

## Crops

`art/crops.toml`:

- focus_x 0.55 for both: the 16:10 crop (90% of the width) takes from the
  left only, so the chameleon (73–93% of the width) keeps its tail.
- `[splash] box`: the splash backdrop is the calm left part of the night
  master, so the splash's own chameleon isn't doubled.
