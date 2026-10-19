# 07 Start menu and app icons

Goal: every icon in the app launcher Halloween-themed, including Discover
(the store). Icon names come from the Kickoff and kicker
binaries on Plasma 6.8 and the menu's `.desktop` and `.directory` files.

Not redrawn: brand logos of other projects (Firefox, Qt D-Bus Viewer, the
ArtCraft suite, btop), like the distribution logo. A Halloween Firefox look
belongs in a Firefox theme instead.

## Colour app icons

| Model | Settings |
|---|---|
| `recraftv4_1_utility_vector`, master folder as style reference (imageWeight 70) | count 2, ×18 |
| `recraftv4_1_utility_pro_vector`, same reference (imageWeight 60) | count 2, ×3 retries |

Every standard prompt is the subject sentence followed by:

> An application icon for a cosy autumn Halloween desktop icon theme, in exactly the same flat vector style as the reference folder icon: flat shapes with at most two tonal steps per colour, soft rounded corners, palette of pumpkin orange (#E8751A), apricot (#F5A05A), plum (#8952A0), dark plum (#65367B), cream (#F2E9E1), candle gold (#F0B429) and night purple (#231B2A). Bold clear silhouette readable at 32 pixels, no outlines, no gradients, no texture, no drop shadow, straight front view. Centred with an even margin of about one eighth on every side, plain white background. No text, no letters, no numbers, no watermark, no signature.

| Master | Icon names | Subject | Chosen |
|---|---|---|---|
| `app-discover` | plasmadiscover (Discover, the store) | A plum-purple shopping bag with pumpkin-orange rope handles and a small cream bat emblem on its front. | 1 |
| `app-konsole` | utilities-terminal, utilities-terminal_su, org.kde.konsole | A dark night-purple terminal window with a plum title bar, showing a glowing pumpkin-orange prompt chevron and a short candle-gold cursor line. | 1 |
| `app-kate` | kate, org.kde.kate | A cream parchment page with a few plum lines of writing and a dark plum quill pen with a pumpkin-orange feather resting across it. | 2 |
| `app-spectacle` | spectacle, org.kde.spectacle | A plum-purple vintage camera whose big round lens shows a cream full moon. | 2 |
| `app-ark` | ark, org.kde.ark | A small wooden treasure chest in pumpkin orange and apricot, bound with dark plum bands and a candle-gold clasp. | 1 |
| `app-gwenview` | gwenview, org.kde.gwenview | A framed picture: a cream crescent moon over plum hills on a night-purple sky, in a pumpkin-orange rounded frame. | 2 |
| `app-help` | help-browser, khelpcenter | A glowing crystal ball, cream and apricot inside, resting on a plum stand. | 2 |
| `app-infocenter` | hwinfo, org.kde.kinfocenter | An open spell book with plum covers and cream pages, a small candle-gold star glowing above it. | 2 |
| `app-kwallet` | kwalletmanager | A pumpkin-orange leather coin pouch tied with a plum cord and a candle-gold clasp. | 2 |
| `app-menuedit` | kmenuedit | A cream list card with three plum lines and a pumpkin-orange quill pen beside it. | 1 |
| `app-qrca` | org.kde.qrca | A pumpkin-orange square camera viewfinder with four corner brackets and a plum eye in the centre. | 2 |
| `app-skanpage` | skanpage | A plum flatbed scanner with its lid slightly open and a glowing pumpkin-orange light bar, a small maple leaf on the glass. | 1 |
| `app-sysmon` | utilities-system-monitor | A night-purple screen in a plum frame showing a glowing pumpkin-orange heartbeat line. | 2 |
| `app-bug` | tools-report-bug (crash viewer) | A friendly round plum spider with eight short legs and two big cream eyes. | 2 |
| `app-emoji` | preferences-desktop-emoticons | A smiling carved jack-o'-lantern face, pumpkin orange with a candle-gold glowing smile and triangle eyes, a short dark stem. | 1 |

The standard model added stripes and patterns; three that read badly at
22 px were redone with the Pro model, adding "very few large flat shapes, no
stripes, no patterns, no decoration" and "readable at 22 pixels":

| Master | Icon names | Subject | Chosen |
|---|---|---|---|
| `app-settings` | preferences-system, systemsettings | A single pumpkin-orange gear wheel with eight chunky rounded teeth and a friendly jack-o'-lantern face (two triangle eyes and a smile) cut into its centre, showing dark plum through the cut-outs. | Pro 1 |
| `app-kdeconnect` | kdeconnect | A plum-purple smartphone standing in front of a pumpkin-orange laptop screen, the phone's night-purple screen showing a small cream bat. | Pro 1 |
| `app-bridge` | org.kde.xwaylandvideobridge | A small arched plum-purple stone bridge with a single round arch, and one small pumpkin-orange bat flying above it ("no individual stones"). | Pro 1 |

Dolphin (`org.kde.dolphin`, `system-file-manager`) is the master folder with
a bat emblem, the way Breeze's is a folder with a dolphin.

## Symbolic menu icons

| Model | Settings |
|---|---|
| `recraftv4_1_utility_vector`, no reference | count 2, ×18 |

Every prompt is "A simple bold glyph icon of …" followed by:

> Solid black flat silhouette on a plain white background, with only a few small white negative-space cut-outs for detail. Single colour, no outlines, no gradients, no shading, very simple chunky shapes that stay readable at 16 pixels, centred and filling most of the square. No text, no lettering, no watermark, no signature.

| Master | Icon names | Subject | Chosen |
|---|---|---|---|
| `emblem-bat` | Dolphin's folder emblem | a bat with spread wings, seen from the front | 1 |
| `glyph-bookmark` | bookmarks, favorites | a bookmark ribbon whose bottom edge is cut in the shape of bat wings | 2 |
| `glyph-grid` | applications-all-symbolic | four small round pumpkins arranged in a two-by-two grid | 1 |
| `glyph-wand` | applications-development-symbolic | a magic wand with a small star at its tip and two tiny sparkles | 1 |
| `glyph-brush` | applications-graphics-symbolic | a paintbrush with a single drip of paint falling from its tip | 2 |
| `glyph-crystal` | help-about-symbolic | a crystal ball on a small stand | 1 |
| `glyph-web` | applications-internet-symbolic | a round spider web | 1 |
| `glyph-quill` | applications-office-symbolic | a quill pen standing in an ink pot | 2 |
| `glyph-gear` | applications-system-symbolic, preferences-system-symbolic | a gear wheel with a jack-o'-lantern face cut out of its centre (face cut-outs in white negative space) | 2 |
| `glyph-broom` | applications-utilities-symbolic | a witch's broom | 2 |
| `glyph-signpost` | compass (the Places tab) | a wooden signpost with two arrow-shaped boards pointing left and right | 2 |
| `glyph-sleep` | system-suspend | a bat hanging upside down asleep with its wings folded around it | 1 |
| `glyph-coffin` | system-suspend-hibernate | a closed coffin seen from the front | 1 |
| `glyph-reboot` | system-reboot | a circular refresh arrow made of a curling vine, with a small leaf at its tip | 2 |
| `glyph-candle` | system-shutdown | a candle that has just been blown out, with a curling wisp of smoke above its wick | 2 |
| `glyph-lock` | system-lock-screen | a padlock with a keyhole shaped like a small pumpkin (keyhole in white negative space) | 2 |
| `glyph-door` | system-log-out | an arched wooden door standing half open, with a small arrow leading out through it | 2 |
| `glyph-ghosts` | system-switch-user | two small friendly ghosts side by side (eyes in white negative space) | 1 |

Multimedia (`applications-multimedia-symbolic`) reuses the bat-wing note
emblem.

`tools/vectors.py` writes these in KDE's symbolic format: 16x16, the
`current-color-scheme` stylesheet and `ColorScheme-Text` with
`fill="currentColor"`, so they take the colour scheme's text colour. Each
dark shape and the light details drawn on top of it become one even-odd path,
so the details are real holes on any background.
