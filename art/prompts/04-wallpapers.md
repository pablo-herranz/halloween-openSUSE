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

Proposed pair: **D** (dusk) and **E** (night), waiting for approval.
`art/crops.toml` moves the 16:10 crop to focus_x 0.55 so the chameleon keeps
a margin.
