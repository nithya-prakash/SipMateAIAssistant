from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any


class RendererType(Enum):
    VECTOR = "vector"          # hand-drawn procedural QPainter shapes
    LOTTIE = "lottie"          # rlottie-backed illustrated animation
    STATIC_IMAGE = "static_image"  # a real asset image, animated procedurally


class CharacterCategory(str, Enum):
    SIPMATE_ORIGINAL = "sipmate_original"
    DISNEY_PRINCESS = "disney_princess"
    DISNEY_FAVORITE = "disney_favorite"


@dataclass
class Character:
    id: str
    name: str
    category: str
    personality: str
    renderer_type: RendererType
    movement_style: str    # how it enters/exits the screen (walk_across, float, launch_upward, ...)
    animation_type: str    # how it behaves once on screen (bounce, float, pulse, hop, ...)
    messages: List[str] = field(default_factory=list)
    asset_path: str = ""   # relative path under assets/characters/, may not exist yet
    sound_path: str = ""   # filename under sounds/effects/, may not exist yet
    emoji: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
