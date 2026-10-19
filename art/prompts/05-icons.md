# 05 Icons

## Master folder icon

Sets the style for every other icon and ornament: once approved, it is the
one-image style reference (`imageWeight` about 80) for the rest.

| Model | Settings |
|---|---|
| `recraftv4_1_utility_pro_vector` (SVG) | 1:1, count 4 |

> A single file-manager folder icon for a cosy autumn Halloween desktop icon
> theme, flat vector design. The folder has a plum-purple back panel with a
> rounded tab (#7A4E9C) and a warm pumpkin-orange front pocket (#E8751A) with
> softly rounded corners and a slightly lighter apricot top edge (#F5A05A).
> Centred on the front pocket is a small cream (#F2E9E1) maple-leaf emblem.
> Flat shapes with at most two subtle tonal steps per colour, a bold, clear
> silhouette that stays readable at 32 pixels, no outlines, no gradients, no
> texture, no drop shadow, no perspective: straight front view. The folder
> fills the square canvas with an even margin of about one eighth on every
> side, on a plain transparent or white background. No text, no lettering,
> no watermark, no signature.

Each SVG is 2048x2048 with 6–14 paths, a full-canvas white backdrop path,
and C2PA content credentials in `<metadata>`. Previews drop the backdrop and
render with resvg (QuickLook always draws SVGs on white).

| | Notes |
|---|---|
| 1 | Burnt orange, cream leaf with a stem; leaf fades at 16 px |
| 2 | Closest to pumpkin #E8751A, darker plum lip under the tab, white leaf; clearest at 16–22 px |
| 3 | Red-orange, leaf shape OK |
| 4 | Red-orange, leaf built from 10 separate pieces |

**2** approved on 2026-10-19: `art/source/vectors/folder.svg`.

## How the set is built

`tools/vectors.py` reads the Recraft SVGs in `art/source/vectors/` (a flat
list of filled paths), drops the backdrop and the C2PA metadata, and
recomposes them on a 64x64 viewBox, tidied with scour:

- **Folders** (`folder`, `folder-*`, `user-home`, `user-desktop`): the master
  folder's body plus one emblem in place of its leaf. Emblems are one-colour
  glyphs: dark parts become cream, light details the folder's orange. Every
  folder therefore has exactly the same shape.
- **`folder-open`**: the master's own shapes, with the front pocket tilted
  open over a cream sheet.
- **Trash**: the empty cauldron as generated; the full one is the same
  cauldron with the glowing potion and bubbles of a second render on its rim,
  both in the same frame so they line up.
- **Launcher** (`start-here-kde-plasma`, `start-here-kde`, `start-here`): the
  chameleon badge, with its greens moved to the chameleon's openSUSE green.
- **16x16**: the folder without emblem, the home folder with a larger
  cottage, and the cauldron, each filling the 16 px frame.

`make icon-preview` renders the built set at 64/48/32/22/16 px.

## Emblems

| Model | Settings |
|---|---|
| `recraftv4_1_utility_vector` (SVG), no reference | 1:1, count 2, ×9 |

Every prompt is "A simple bold glyph icon of …, " followed by: Solid black flat silhouette on a plain white background, with only a few small white negative-space cut-outs for detail. Single colour, no outlines, no gradients, no shading, chunky shapes that stay readable at 16 pixels, centred and filling most of the square. No text, no lettering, no watermark, no signature.

| Icon | Subject | Chosen |
|---|---|---|
| folder-documents | a rolled parchment scroll, slightly unrolled | 1 (2 looked like a book) |
| folder-download | an acorn with a short, bold downward-pointing arrow directly below it | 2 (bolder arrow) |
| folder-music | a musical eighth note whose flag is a small bat wing | 2 |
| folder-pictures | a picture: a crescent moon above a rounded hill, inside a rounded-square photo frame | 2 (clear frame) |
| folder-videos | an old cinema film reel | 2 |
| folder-templates | a pumpkin-carving stencil: a rounded square card with two triangle eyes, a triangle nose and a jagged smile cut out of it (cut-outs in white negative space) | 1 |
| folder-publicshare | an old hanging candle lantern with a ring handle on top | 1 (simpler) |
| user-home | a small cosy cottage with a pitched roof, a chimney and a round window | 1 |
| user-desktop | a computer monitor on a small stand, with a crescent moon on its screen (screen in white negative space) | 2 (bolder frame) |

Saved as `art/source/vectors/emblem-<subject>.svg`.

## Open folder (not used)

`recraftv4_1_utility_pro_vector`, master as style reference (imageWeight 80),
count 2:

> An open file-manager folder icon in exactly the same flat vector style,
> colours and proportions as the reference folder icon: plum-purple back
> panel with a rounded tab, a darker plum inner lip, and the warm
> pumpkin-orange front pocket with a lighter apricot top edge, now tilted
> open towards the viewer so a few cream sheets of paper peek out of the
> folder. No emblem on the front. Flat shapes, bold clear silhouette
> readable at 32 pixels, no outlines, no gradients, no texture, no drop
> shadow. Centred with an even margin of about one eighth on every side,
> plain white background. No text, no lettering, no watermark, no signature.

Both came out with a magenta plum and angular shapes, so `folder-open` is
made from the master instead (above).

## Trash

`recraftv4_1_utility_pro_vector`, master as style reference (imageWeight 60),
count 4:

> A witch's cauldron used as a trash-can icon, in exactly the same flat
> vector style as the reference folder icon: a round, pot-bellied plum-purple
> cauldron (#8952A0) with a thick darker plum rim (#65367B), a soft lighter
> plum highlight on its belly and three short stubby legs. It is empty. Flat
> shapes with at most two tonal steps per colour, bold clear silhouette
> readable at 32 pixels, no outlines, no gradients, no texture, no drop
> shadow, straight front view. Centred with an even margin of about one
> eighth on every side, plain white background. No text, no lettering, no
> watermark, no signature.

Chose **3** (wide pot, rim bar, stubby legs; lightest plum, so it shows on
the dark view): `trash.svg`.

Full version, same model with cauldron 3 as reference (imageWeight 90),
count 4:

> Exactly the same witch's cauldron icon as the reference, with the same
> shape, size, plum-purple colours, rim and three stubby legs, but now full:
> a glowing pumpkin-orange potion (#E8751A) fills it to just below the rim,
> with three or four round bubbles in candle gold (#F0B429) rising just above
> the rim. Flat vector, same flat style, no outlines, no gradients, no
> texture, no drop shadow, straight front view, centred, plain white
> background. No text, no lettering, no watermark, no signature.

None kept cauldron 3's shape, and all were too dark for the dark view. Only
the potion and bubbles of **4** are used (`potion.svg`), placed on cauldron
3's rim.

## Launcher

`recraftv4_1_utility_pro_vector`, the splash chameleon render as reference
(imageWeight 50), count 4:

> A flat vector application-launcher icon: the head and shoulders of the
> friendly cartoon chameleon from the reference picture, leaf-green with a
> pale yellow-green chin, big round turret eye, wearing its floppy plum witch
> hat with a burnt-orange band and its striped pumpkin-orange and rust scarf,
> shown in three-quarter view inside a round dark night-purple badge
> (#231B2A) with a thin pumpkin-orange ring. Flat shapes, few colours, bold
> clear silhouette readable at 22 pixels, no outlines, no gradients, no
> texture, no drop shadow. Centred, the badge filling the square with a small
> even margin, plain white background outside the badge. No text, no
> lettering, no watermark, no signature.

Chose **3**: round ring, clear head, eye, hat and scarf at 22 px
(`launcher.svg`). Its dark square backdrop is dropped, so the ring is open
on any panel colour, and its teal greens are moved to openSUSE green.
