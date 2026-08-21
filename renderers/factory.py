from characters.character import RendererType
from renderers.vector_assets import AnimatedVectorWidget
from renderers.lottie_renderer import LottieRenderer
from renderers.static_character import StaticCharacterWidget

class RendererFactory:
    @staticmethod
    def create_renderer(character):
        if character.renderer_type == RendererType.LOTTIE:
            return LottieRenderer(character)
        elif character.renderer_type == RendererType.STATIC_IMAGE:
            return StaticCharacterWidget(character)
        else:
            return AnimatedVectorWidget(character.id)
