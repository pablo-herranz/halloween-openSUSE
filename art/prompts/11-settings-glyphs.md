# 11 Settings glyphs: KDE System Settings and GNOME Settings

Glyphs for the settings that still showed stock icons: KDE System
Settings' modules and categories, carved into the pumpkin master, and
GNOME Settings' sidebar panels, as one-colour icons. Generated with the
Picsart `gen-ai` command-line tool. An adversarial review measured every
glyph at 16 and 22 px; the ones whose details fell below a pixel were made
again with simpler wordings, and the plug, disk and mug glyphs were dropped.

`recraftv4_1_utility_vector`, no reference, count 2 each. Each prompt is "A
simple bold glyph icon of …" followed by:

> Solid black flat silhouette on a plain white background, with only a few small white negative-space cut-outs for detail. Single colour, no outlines, no gradients, no shading, very simple chunky shapes that stay readable at 16 pixels, centred and filling most of the square. No text, no lettering, no watermark, no signature.

| Master | Subject | Chosen | Used for |
|---|---|---|---|
| `glyph-palette` | an artist's paint palette with a thumb hole and four round paint dots | 1 | Colors, Gamma; GNOME Color Management |
| `glyph-cursor` | the classic desktop mouse pointer: an upright arrow pointing to the top left, its straight left edge vertical, with a short stem at its lower right, like the default cursor | 1 (second wording; the first, "a bold mouse pointer arrow, slightly tilted, with a short tail", read as a paper plane) | Pointers |
| `glyph-speech` | a rounded speech bubble with two large round holes in it, the gaps between them as wide as the holes | 2 (second wording; the three dots of the first merged at 16 px) | User Feedback |
| `glyph-globe` | a globe made of three thick curved bands, with wide gaps between them at least a seventh of its width, nothing else | 1 (second wording; the first, with lines of latitude and a moon, was a dark ball at 16 px) | Region & Language; GNOME Region & Language |
| `glyph-magnifier` | a magnifying glass with a round lens and a thick handle | 2 | Search, Plasma Search; GNOME Search |
| `glyph-stylus` | a bold drawing stylus alone, lying diagonally, with a big pointed nib and a thick body | 1 (second wording; the pen on a tablet vanished at 16 px) | Drawing Tablet; GNOME Graphics Tablets |
| `glyph-touch` | a hand with the index finger raised, tapping, with two small arcs above the fingertip | 2 | Touchscreen |
| `glyph-shield` | a shield with a small keyhole in its middle | 1 | Security & Privacy; GNOME Privacy & Security |
| `glyph-printer` | a printer seen straight from the front: a flat top with one tall sheet of paper standing up out of it, a straight-sided body and one wide slot | 1 (second wording; the first read as a cauldron) | GNOME Printers |
| `glyph-heart` | a heart shape with one small leaf on its top, the leaf at least as wide as a fifth of the heart | 1 (replaces a steaming mug, too close to a programming language's mark) | GNOME Wellbeing |

Existing glyphs and emblems cover the other entries (`SETTINGS` and
`GNOME_SETTINGS` in `tools/vectors.py`). At 16 and 22 px, the sizes
settings lists use, the pumpkin fills the icon and the glyph nearly fills
the pumpkin (`16x16/apps`, `22x22/apps`).
