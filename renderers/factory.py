from characters.character import RendererType
from renderers.vector_assets import AnimatedVectorWidget
from renderers.lottie_renderer import LottieRenderer

class RendererFactory:
    @staticmethod
    def create_renderer(character):
        if character.renderer_type == RendererType.LOTTIE:
            return LottieRenderer(character)
        else:
            return AnimatedVectorWidget(character.id)
