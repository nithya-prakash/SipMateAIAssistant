from datetime import date
from characters.character import CharacterCategory
from characters.registry import CharacterRegistry


class CharacterSelector:
    """Picks which character to show for the next reminder, based on the user's
    configured character_mode. All state it needs (mode, single-character choice,
    favorites) lives in Settings, so it stays stateless/replaceable itself."""

    def __init__(self, registry: CharacterRegistry, settings_manager):
        self.registry = registry
        self.settings_manager = settings_manager

    def select(self):
        settings = self.settings_manager.settings
        mode = getattr(settings, "character_mode", "random")

        if mode == "single":
            char = self.registry.get_character(settings.selected_character_id)
            if char:
                return char
            mode = "random"  # configured id no longer exists - fall back gracefully

        if mode == "daily_rotation":
            return self._daily_rotation()

        if mode == "favorites":
            favorites = [c for c in self.registry.get_all() if c.id in settings.favorite_character_ids]
            if favorites:
                return self.registry.get_random_character(pool=favorites)
            mode = "random"  # no favorites picked yet - fall back gracefully

        if mode == "sipmate_originals":
            return self.registry.get_random_character(pool=self.registry.get_by_category(CharacterCategory.SIPMATE_ORIGINAL))

        # Any other/stale mode value (e.g. a leftover "princess_mode" from an old
        # settings.json) falls back to plain random rather than erroring.
        return self.registry.get_random_character()

    def _daily_rotation(self):
        roster = self.registry.get_all()
        if not roster:
            return None
        index = date.today().toordinal() % len(roster)
        return roster[index]
