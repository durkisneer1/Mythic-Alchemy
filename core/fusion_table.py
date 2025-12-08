import pykraken as kn
from core.card import Card
from core.deck import get_card_texture, check_fusion
from core.constants import CARD_SIZE, SCN_SIZE

class FusionTable:
    def __init__(self):
        self.table_tex = kn.Texture("assets/fusion_table.png")
        self.table_rect = self.table_tex.get_rect()

        self.slot_gap = 60

        self.lhs_card: Card | None = None
        self.rhs_card: Card | None = None
        self.fusion_result_card: Card | None = None

        mid_x, mid_y = SCN_SIZE / 2
        self.table_rect.center = (mid_x, mid_y)
        self._home_pos = kn.Vec2(self.table_rect.top_left.x, self.table_rect.top_left.y)

        # Slot offsets relative to the table center so they move together during animations.
        self.lhs_offset = kn.Vec2(-(CARD_SIZE.x + self.slot_gap), 0)
        self.rhs_offset = kn.Vec2(0, 0)
        self.result_offset = kn.Vec2(CARD_SIZE.x + self.slot_gap, 0)

        self.lhs_rect = kn.Rect(0, 0, CARD_SIZE)
        self.rhs_rect = kn.Rect(0, 0, CARD_SIZE)
        self.fusion_result_rect = kn.Rect(0, 0, CARD_SIZE)
        self._sync_slot_positions()

        self.hiding = False
        self.hide_anim = kn.EasingAnimation(kn.ease.out_cubic, 0.8)
        self.hide_anim.start_pos = self.table_rect.top_left
        self.hide_anim.end_pos = self.table_rect.top_left + kn.Vec2(0, SCN_SIZE.y)
        self.hide_anim_time = 0.8

    def hide(self) -> None:
        self.hiding = True
        self.hide_anim.start_pos = kn.Vec2(self.table_rect.top_left.x, self.table_rect.top_left.y)
        self.hide_anim.end_pos = self._home_pos + kn.Vec2(0, SCN_SIZE.y)
        self.hide_anim.restart()

    def show(self) -> None:
        self.hiding = True
        current = kn.Vec2(self.table_rect.top_left.x, self.table_rect.top_left.y)
        self.hide_anim.start_pos = current
        self.hide_anim.end_pos = self._home_pos
        self.hide_anim.restart()

    def _sync_slot_positions(self) -> None:
        center = self.table_rect.center
        self.lhs_rect.center = center + self.lhs_offset
        self.rhs_rect.center = center + self.rhs_offset
        self.fusion_result_rect.center = center + self.result_offset

    def render(self) -> None:
        if self.hiding:
            self.table_rect.top_left = self.hide_anim.step()
            if self.hide_anim.is_done:
                self.hiding = False
        self._sync_slot_positions()

        kn.renderer.draw(self.table_tex, self.rhs_rect.center, anchor=kn.Anchor.CENTER)

        def draw_slot(card: Card | None, rect: kn.Rect) -> bool:
            if card is None:
                return False

            kn.renderer.draw(get_card_texture(card.ID), dst=rect)
            return True

        lhs_present = draw_slot(self.lhs_card, self.lhs_rect)
        rhs_present = draw_slot(self.rhs_card, self.rhs_rect)

        # If only one card is present, draw it in the fusion result slot
        if lhs_present ^ rhs_present:
            solo_card = self.lhs_card or self.rhs_card
            kn.renderer.draw(
                get_card_texture(solo_card.ID),
                dst=self.fusion_result_rect
            )
            self.fusion_result_card = solo_card
        else:
            self.fusion_result_card = None

        # If both cards are present, check for fusion result
        if self.lhs_card is None or self.rhs_card is None:
            return

        combo = (self.lhs_card.ID, self.rhs_card.ID)
        fused_card = check_fusion(combo)
        if fused_card is not None:
            kn.renderer.draw(
                get_card_texture(fused_card.ID),
                dst=self.fusion_result_rect
            )
            self.fusion_result_card = fused_card
        else:
            self.fusion_result_card = None
