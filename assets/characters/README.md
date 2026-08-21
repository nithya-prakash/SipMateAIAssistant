# Character assets needed

None of the 24 characters have real artwork yet. The app runs fully without any
of these — `StaticCharacterWidget` (renderers/static_character.py) falls back
gracefully when a file below is missing:

- **dog, cat, ghost, airplane, rocket, penguin** fall back to the existing
  hand-drawn procedural vector art in `renderers/vector_assets.py` (already
  decent-looking, no action needed unless you want real illustrations instead).
- **Everyone else** (frog, sloth, and all 16 Disney characters) falls back to a
  generated placeholder badge: a soft colored circle with the character's emoji.

To upgrade a character to real artwork, drop a PNG here with the exact filename
below (transparent background recommended, roughly square, at least 300x300px)
and it's picked up automatically next launch - no code changes needed.

Do not source Disney character artwork from the internet without checking the
license; these are placeholders specifically so the app works before any
properly-licensed assets exist.

## SipMate Originals
- dog.png
- ghost.png
- airplane.png
- cat.png
- penguin.png
- frog.png
- rocket.png
- sloth.png

## Disney Princesses
- snow_white.png
- cinderella.png
- aurora.png
- ariel.png
- belle.png
- jasmine.png
- pocahontas.png
- mulan.png
- tiana.png
- rapunzel.png
- merida.png
- moana.png
- raya.png

## Disney Favorites
- elsa.png
- anna.png
- mirabel.png
