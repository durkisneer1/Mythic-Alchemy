import pykraken as kn
from core.card import Card, CardLocation
from core.deck import load_deck
from core.constants import SCN_SIZE, CARD_SIZE


class Player:
    def __init__(self, health: int = 20):
        self.health = health
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
        anchored_cards = [card for card in self.hand if card.location is CardLocation.HAND]
        total = len(anchored_cards)
        mouse_pos = kn.mouse.get_pos()

        layered_cards: list[Card] = []
        base_cards: list[Card] = []
        
        hover_claimed = False
        for idx, card in enumerate(anchored_cards):
            card.move_to(self.to_hand_pos(idx, total))

            should_hover = False
            if not hover_claimed and card.contains_point(mouse_pos):
                should_hover = True
                hover_claimed = True

            card.set_hovered(should_hover)
            card.update_hand_motion()

            (layered_cards if card.has_hover_elevation() else base_cards).append(card)

        for card in base_cards:
            card.draw()
        for card in layered_cards:
            card.draw()

        for card in self.hand:
            if card.location is CardLocation.DRAG:
                card.set_hovered(False)
                card.update_hand_motion()
                card.draw()
