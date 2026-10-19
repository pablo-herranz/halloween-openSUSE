# 08 More icons: web browser, file types, devices, folders

The icon theme's second round: an original web-browser icon (used for Firefox
too, instead of a modified Firefox logo), file-type icons, drives and media,
and more folder variants. Same pipeline as before: SVG masters in
`art/source/vectors/`, composed by `tools/vectors.py`.

## Colour icons

`recraftv4_1_utility_pro_vector`, the master folder as style reference
(imageWeight 60). Each prompt is the subject, then "An icon for a cosy autumn
Halloween desktop icon theme, in exactly the same flat vector style as the reference folder icon: very few large flat shapes, at most two tonal steps per colour, no stripes, no patterns, soft rounded corners, palette of pumpkin orange (#E8751A), apricot (#F5A05A), plum (#8952A0), dark plum (#65367B) and cream (#F2E9E1) or candle gold (#F0B429). Bold clear silhouette readable at 22 pixels, no outlines, no gradients, no texture, no drop shadow. Centred with an even margin, plain white background. No text, no letters, no numbers, no logo, no watermark, no signature."

| Master | Subject | Count | Chosen |
|---|---|---|---|
| `app-browser` | A web-browser application icon: a round glowing globe like a crystal ball, deep plum-purple with pumpkin-orange meridian and latitude lines, and a small cream bat flying along an orbit arc around it ("no fox"). | 4 | 2 |
| `mime-page` | A blank document file icon: an upright cream paper sheet with softly rounded corners, its top-right corner folded down in apricot, and a narrow dark plum strip along its left edge like a binding. Nothing printed on the page. | 4 | 1 |
| `device-harddisk` | A hard disk drive icon: a flat rectangular plum-purple drive box seen from the front, with a thin pumpkin-orange front strip and one small glowing candle-gold activity light. | 2 | 2 |
| `device-usb` | A USB flash drive icon: a pumpkin-orange USB stick standing diagonally, with a cream metal connector at its top end and a small plum keyring loop at the bottom. | 2 | 2 (came out pumpkin-shaped) |
| `device-optical` | An optical disc icon: a round shiny disc in cream and apricot with a dark plum centre hole and a soft pumpkin-orange reflection band. | 2 | 1 |
| `device-server` | A network server icon: a small upright plum-purple server tower with three horizontal pumpkin-orange drive bays and a few candle-gold status lights. | 2 | 2 |

## Emblem glyphs

`recraftv4_1_utility_vector`, no reference, count 2 each. Each prompt is "A
simple bold glyph icon of …" followed by: Solid black flat silhouette on a plain white background, with only a few small white negative-space cut-outs for detail. Single colour, no outlines, no gradients, no shading, very simple chunky shapes that stay readable at 16 pixels, centred and filling most of the square. No text, no lettering, no watermark, no signature.

| Master | Subject | Chosen |
|---|---|---|
| `glyph-cloud` | a fluffy cloud with a small crescent moon peeking out behind it | 2 |
| `glyph-hourglass` | an old hourglass with sand running down | 1 |
| `glyph-gamepad` | a game controller with a small pumpkin face on it (eyes and buttons in white negative space) | 2 |
| `glyph-chest` | a small closed treasure chest with a lock | 2 |

## How they are used

- **Browser:** `app-browser` for `web-browser`, `internet-web-browser`,
  `firefox`, `firefox-esr`, `org.mozilla.firefox`,
  `firefox-developer-edition` and `firefox-nightly`.
- **File types:** the `mime-page` master with an emblem on the sheet, dark
  parts in pumpkin. Specific names (`image-png`, `audio-mpeg`, …) are listed
  as well as the generic ones, because file managers ask for those first.
  - quill: text and markdown
  - scroll: PDF and office documents
  - picture: images
  - note: audio
  - reel: video
  - chest: archives and packages
  - spider web: HTML
  - wand: scripts, JSON and XML
  - gear: programs and libraries
  - `inode-directory` is the folder icon.
- **Devices:** the hard drive for every drive and partition name, the USB
  stick for removable media and flash cards, the disc for optical media, the
  server for network places.
- **Folders**, the master folder with an emblem:
  - wand: `folder-development` (Projects)
  - cloud: `folder-cloud`
  - hourglass: `folder-recent`
  - gamepad: `folder-games`
  - spider web: `folder-network` and `folder-remote`
  - ghosts: `folder-image-people`
  - bat bookmark: `folder-favorites`
