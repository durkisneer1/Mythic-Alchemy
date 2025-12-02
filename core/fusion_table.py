import pykraken as kn
from core.card import Card
from core.deck import get_card_texture
from core.constants import CARD_SIZE, SCN_SIZE

class FusionTable:
    def __init__(self):
        self.lhs_card: Card | None = None
        self.rhs_card: Card | None = None
        self.fusion_result: Card | None = None

        mid_x, mid_y = SCN_SIZE / 2
        gap = 60

        self.lhs_rect = kn.Rect(0, 0, CARD_SIZE)
        self.lhs_rect.center = (mid_x - CARD_SIZE.x - gap, mid_y)

        self.rhs_rect = kn.Rect(0, 0, CARD_SIZE)
        self.rhs_rect.center = (mid_x, mid_y)

        self.fusion_result_rect = kn.Rect(0, 0, CARD_SIZE)
        self.fusion_result_rect.center = (mid_x + CARD_SIZE.x + gap, mid_y)

    def render(self) -> None:
        kn.draw.rect(self.lhs_rect, kn.color.DARK_GRAY)
        kn.draw.rect(self.rhs_rect, kn.color.DARK_GRAY)
        kn.draw.rect(self.fusion_result_rect, kn.color.DARK_GRAY)

        if self.lhs_card is not None:
            kn.renderer.draw(
                get_card_texture(self.lhs_card.texture_index),
                dst=self.lhs_rect
            )

        if self.rhs_card is not None:
            kn.renderer.draw(
                get_card_texture(self.rhs_card.texture_index),
                dst=self.rhs_rect
            )

        # Check if fusion result can be rendered
        if self.lhs_card is None or self.rhs_card is None:
            return

        kn.renderer.draw(
            get_card_texture(self.fusion_result.texture_index),
            dst=self.fusion_result_rect
        )
