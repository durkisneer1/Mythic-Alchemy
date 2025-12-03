import pykraken as kn
from core.card import Card
from core.constants import CARD_SIZE
from core.deck import get_card_texture
from states.base_state import BaseState
from core.player import Player
from core.fusion_table import FusionTable

from typing import TYPE_CHECKING, override
if TYPE_CHECKING:
    from main import Root


class BattleState(BaseState):
    def __init__(self, root: "Root"):
        super().__init__(root)

        self.player = Player()
        for _ in range(5):
            self.player.draw_card()

        self.fusion_table = FusionTable()

        self.dragged_card: Card | None = None
        self.drag_cursor_offset = kn.Vec2(0, 0)

    @override
    def handle_event(self, event: kn.Event) -> None:
        if event.type == kn.MOUSE_BUTTON_DOWN and event.button == kn.M_LEFT:
            for idx, card in enumerate(self.player.hand):
                if (kn.collision.overlap(self.player.to_dst(idx), kn.mouse.get_pos())
                    and not card.is_occupied
                    ):
                    card.is_occupied = True
                    self.dragged_card = card
                    self.drag_cursor_offset = kn.mouse.get_pos() - self.player.to_dst(idx).top_left
                    return

            # Check lhs fusion slot
            if (kn.collision.overlap(self.fusion_table.lhs_rect, kn.mouse.get_pos())
                and self.fusion_table.lhs_card is not None
                ):
                self.dragged_card = self.fusion_table.lhs_card
                self.fusion_table.lhs_card = None
                self.drag_cursor_offset = kn.mouse.get_pos() - self.fusion_table.lhs_rect.top_left
                return

            # Check rhs fusion slot
            if (kn.collision.overlap(self.fusion_table.rhs_rect, kn.mouse.get_pos())
                and self.fusion_table.rhs_card is not None
                ):
                self.dragged_card = self.fusion_table.rhs_card
                self.fusion_table.rhs_card = None
                self.drag_cursor_offset = kn.mouse.get_pos() - self.fusion_table.rhs_rect.top_left
                return

        elif event.type == kn.MOUSE_BUTTON_UP and event.button == kn.M_LEFT:
            if self.dragged_card is None:
                return

            dropped_card_rect = get_card_texture(self.dragged_card.ID).get_rect()
            dropped_card_rect.top_left += kn.mouse.get_pos() - self.drag_cursor_offset

            # Check if over any fusion slot and place in nearest one
            if (kn.collision.overlap(dropped_card_rect, self.fusion_table.lhs_rect)
                or kn.collision.overlap(dropped_card_rect, self.fusion_table.rhs_rect)):

                dx_lhs = dropped_card_rect.x - self.fusion_table.lhs_rect.x
                dx_rhs = dropped_card_rect.x - self.fusion_table.rhs_rect.x

                if abs(dx_lhs) < abs(dx_rhs):
                    if self.fusion_table.lhs_card is not None:
                        self.fusion_table.lhs_card.is_occupied = False
                    self.fusion_table.lhs_card = self.dragged_card
                    self.dragged_card = None
                    return

                if self.fusion_table.rhs_card is not None:
                    self.fusion_table.rhs_card.is_occupied = False
                self.fusion_table.rhs_card = self.dragged_card
                self.dragged_card = None
                return

            self.dragged_card.is_occupied = False
            self.dragged_card = None

    @override
    def update(self) -> None:
        kn.renderer.clear()

        self.player.render_hand()
        self.fusion_table.render()

        if self.dragged_card is not None:
            kn.renderer.draw(
                get_card_texture(self.dragged_card.ID),
                pos=kn.mouse.get_pos() - self.drag_cursor_offset,
                anchor=kn.Anchor.TOP_LEFT
            )
