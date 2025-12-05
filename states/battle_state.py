import pykraken as kn
from core.card import Card, CardLocation
from states.base_state import BaseState
from core.player import Player
from core.fusion_table import FusionTable
from core.button import Button

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

        play_txt = kn.Text(root.font)
        play_txt.text = "Play"
        self.play_btn = Button(play_txt, kn.Vec2(50, 50))

    @override
    def handle_event(self, event: kn.Event) -> None:
        if event.type == kn.MOUSE_BUTTON_DOWN and event.button == kn.M_LEFT:
            mouse_pos = kn.mouse.get_pos()
            for card in self.player.hand:
                if card.location is not CardLocation.HAND:
                    continue

                if card.contains_point(mouse_pos):
                    card.start_drag()
                    self.dragged_card = card
                    return

            # Check lhs fusion slot
            if (kn.collision.overlap(self.fusion_table.lhs_rect, mouse_pos)
                and self.fusion_table.lhs_card is not None
                ):
                self.dragged_card = self.fusion_table.lhs_card
                self.dragged_card.start_drag()
                self.fusion_table.lhs_card = None
                return

            # Check rhs fusion slot
            if (kn.collision.overlap(self.fusion_table.rhs_rect, mouse_pos)
                and self.fusion_table.rhs_card is not None
                ):
                self.dragged_card = self.fusion_table.rhs_card
                self.dragged_card.start_drag()
                self.fusion_table.rhs_card = None
                return

        elif event.type == kn.MOUSE_BUTTON_UP and event.button == kn.M_LEFT:
            if self.dragged_card is None:
                return

            self.dragged_card.update_drag_position()
            dropped_card_rect = self.dragged_card.rect

            # Check if over any fusion slot and place in nearest one
            if (kn.collision.overlap(dropped_card_rect, self.fusion_table.lhs_rect)
                or kn.collision.overlap(dropped_card_rect, self.fusion_table.rhs_rect)):

                dx_lhs = dropped_card_rect.x - self.fusion_table.lhs_rect.x
                dx_rhs = dropped_card_rect.x - self.fusion_table.rhs_rect.x

                if abs(dx_lhs) < abs(dx_rhs):
                    if self.fusion_table.lhs_card is not None:
                        self.fusion_table.lhs_card.return_to_hand()
                    self.dragged_card.place_in_slot(self.fusion_table.lhs_rect)
                    self.fusion_table.lhs_card = self.dragged_card
                    self.dragged_card = None
                    return

                if self.fusion_table.rhs_card is not None:
                    self.fusion_table.rhs_card.return_to_hand()
                    
                self.dragged_card.place_in_slot(self.fusion_table.rhs_rect)
                self.fusion_table.rhs_card = self.dragged_card
                self.dragged_card = None
                return

            self.dragged_card.return_to_hand()
            self.dragged_card = None

    @override
    def update(self) -> None:
        kn.renderer.clear()

        self.play_btn.draw()

        self.fusion_table.render()
        self.player.render_hand()
