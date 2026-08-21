# Character assets

The 8 SipMate Originals all have real, illustrated Lottie animations in this
folder - no placeholders needed:

- dog.json - "Yoga Dog"
- ghost.json
- airplane.json - "Aeroplane Flying"
- cat.json - "Black cat" by PoPoF
- penguin.json - penguin jump, by ankur k
- frog.json
- rocket.json - "Rocket Lunch"
- sloth.json - "Sloth doing meditation"

Sourced from LottieFiles' free tier (Lottie Simple License - commercial use
allowed, no attribution required).

If a character's asset ever goes missing, `renderers/static_character.py`
falls back gracefully: to the hand-drawn vector art in
`renderers/vector_assets.py` for dog/cat/ghost/airplane/rocket/penguin, or to
a generated emoji-badge placeholder otherwise - the app never fails to render
a character for lack of an asset.

To add a new character, drop a `.json` (Lottie) or `.png` (static image)
file here with a filename matching a manifest's `"asset"` field in
`characters/manifests/`.
