# Prompts

One file per generated asset, numbered in the order they were made
(`NN-short-name.md`). Each records everything needed to reproduce or
continue the asset:

- model and settings (size, aspect ratio, seed, image weight)
- the full prompt and negative prompt
- reference images used (paths in `art/source/` or earlier prompt numbers)
- which result was kept, and any post-processing done by hand

Prompt rules for this project:

- Never write "openSUSE", "Geeko" or "logo": the chameleon is an original
  character, inspired by the Geeko, never a copy of the trademark.
- Always add "no text, no lettering, no watermark, no signature".
- Characters to be cut out go on a solid magenta background (never green,
  because the chameleon is green).
