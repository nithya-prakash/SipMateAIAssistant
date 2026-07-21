import json
import glob
import random
import os
from characters.character import Character, RendererType

class CharacterRegistry:
    def __init__(self):
        self.characters = []
        self.recent_history = []
        self._load_manifests()

    def _load_manifests(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manifest_path = os.path.join(base_dir, "manifests", "*.json")
        for filepath in glob.glob(manifest_path):
            with open(filepath, "r") as f:
                data = json.load(f)
                renderer = RendererType.VECTOR if data.get("renderer") == "vector" else RendererType.LOTTIE
                c = Character(
                    id=data["id"],
                    name=data["id"].capitalize(),
                    renderer_type=renderer,
                    movement_style=data.get("behavior", "fly_across"),
                    messages=data.get("messages", []),
                    personality_traits=[data.get("personality", "neutral")]
                )
                self.characters.append(c)

    def get_random_character(self) -> Character:
        available = [c for c in self.characters if c.id not in self.recent_history]
        if not available:
            available = self.characters
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
