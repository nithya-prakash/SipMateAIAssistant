import json
import glob
import random
import os
from characters.character import Character, RendererType

_RENDERER_MAP = {
    "vector": RendererType.VECTOR,
    "lottie": RendererType.LOTTIE,
    "static_image": RendererType.STATIC_IMAGE,
}


class CharacterRegistry:
    def __init__(self):
        self.characters = []
        self.recent_history = []
        self._load_manifests()

    def _load_manifests(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manifest_path = os.path.join(base_dir, "manifests", "*.json")
        for filepath in sorted(glob.glob(manifest_path)):
            with open(filepath, "r") as f:
                data = json.load(f)
                renderer = _RENDERER_MAP.get(data.get("renderer", "static_image"), RendererType.STATIC_IMAGE)
                c = Character(
                    id=data["id"],
                    name=data.get("name", data["id"].replace("_", " ").title()),
                    category=data.get("category", "sipmate_original"),
                    personality=data.get("personality", ""),
                    renderer_type=renderer,
                    movement_style=data.get("movement_style", data.get("behavior", "walk_across")),
                    animation_type=data.get("animation_type", "bounce"),
                    messages=data.get("messages", []),
                    asset_path=data.get("asset", ""),
                    sound_path=data.get("sound", ""),
                    emoji=data.get("emoji", ""),
                    metadata=data.get("metadata", {}),
                )
                self.characters.append(c)

    def get_all(self):
        return list(self.characters)

    def get_by_category(self, category: str):
        return [c for c in self.characters if c.category == category]

    def get_random_character(self, pool=None) -> Character:
        """Pick randomly from `pool` (or the full roster), avoiding immediate repeats
        via a short rolling history shared across all modes that call this."""
        source = pool if pool is not None else self.characters
        if not source:
            source = self.characters

        available = [c for c in source if c.id not in self.recent_history]
        if not available:
            available = source
            self.recent_history.clear()

        chosen = random.choice(available)
        self.recent_history.append(chosen.id)
        if len(self.recent_history) > 7:
            self.recent_history.pop(0)

        return chosen

    def get_character(self, character_id: str) -> Character:
        for c in self.characters:
            if c.id == character_id:
                return c
        return self.characters[0] if self.characters else None
