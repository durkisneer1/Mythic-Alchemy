import pykraken as kn
from core.card import Card
from core.deck import load_deck, get_card_texture
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

    def to_dst(self, idx: int) -> kn.Rect:
        x_offset = (SCN_SIZE.x - (len(self.hand) * CARD_SIZE.x)) / 2
        return kn.Rect(
            x_offset + idx * CARD_SIZE.x,
            SCN_SIZE.y - CARD_SIZE.y - 50,
            CARD_SIZE
        )

    def render_hand(self) -> None:
        for idx, card in enumerate(self.hand):
            if card.is_occupied:
                continue  # Skip rendering occupied card here

            kn.renderer.draw(
                get_card_texture(card.ID),
                dst=self.to_dst(idx)
            )
