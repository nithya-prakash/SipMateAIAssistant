from dataclasses import dataclass
from enum import Enum
from typing import List

class RendererType(Enum):
    VECTOR = "vector"
    LOTTIE = "lottie"

@dataclass
class Character:
    id: str
    name: str
    renderer_type: RendererType
    movement_style: str  # e.g., "fly_across", "bounce", "float"
    messages: List[str]
    personality_traits: List[str]
    asset_path: str = "" # Empty if procedural
