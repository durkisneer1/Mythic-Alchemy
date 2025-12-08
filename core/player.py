import pykraken as kn
from core.card import Card, CardLocation
from core.deck import load_deck
from core.constants import SCN_SIZE, CARD_SIZE


class Player:
    def __init__(self):
        self.health = 50
        self.hand: list[Card] = []
        self.deck = load_deck()

    def draw_card(self) -> None:
        if self.deck:
            card = self.deck.pop()
            self.hand.append(card)
            card.begin_hand_entry()

    def to_hand_pos(self, idx: int, count: int) -> kn.Vec2:
        x_offset = (SCN_SIZE.x - (count * CARD_SIZE.x)) / 2
        return kn.Vec2(
            x_offset + idx * CARD_SIZE.x,
            SCN_SIZE.y - CARD_SIZE.y - 50
        )

    def render_hand(self) -> None:
        dt = kn.time.get_delta()

        anchored_cards = [card for card in self.hand if card.location is CardLocation.HAND]
        total = len(anchored_cards)
        mouse_pos = kn.mouse.get_pos()

        hovered_card: Card | None = None

        # Position, hover detection, and motion
        for idx, card in enumerate(anchored_cards):
            card.move_to(self.to_hand_pos(idx, total))

            if hovered_card is None and card.contains_point(mouse_pos):
                hovered_card = card

            card.set_hovered(card is hovered_card)
            card.update_drag_position()
            card.update_hand_motion(dt)

        # Draw all hand cards except the hovered one
        for card in anchored_cards:
            if card is hovered_card:
                continue
            card.draw()

        # Draw hovered card on top
        if hovered_card is not None:
            hovered_card.draw()

        # Dragged cards render above everything else
        for card in self.hand:
            if card.location is CardLocation.DRAG:
                card.set_hovered(False)
                card.update_drag_position()
                card.update_hand_motion(dt)
                card.draw()
