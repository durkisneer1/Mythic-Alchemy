import pykraken as kn
from core.card import Card
from core.constants import CARD_SIZE, SCN_SIZE
from core.deck import load_deck, get_card_texture


class Bot:
    def __init__(self):
        self.health = 30
        self.deck = load_deck()
        self.hand: list[Card] = []
        self.played_card: Card | None = None

        # Bot plays from the top-center of the screen to keep it clear of the player's hand and fusion slots.
        self.play_rect = kn.Rect(0, 0, CARD_SIZE)
        self.play_rect.center = kn.Vec2(SCN_SIZE.x / 2, CARD_SIZE.y / 2 + 40)

    def draw_card(self) -> Card | None:
        if not self.deck:
            self.played_card = None
            return None

        card = self.deck.pop()
        self.hand.append(card)
        self.played_card = card
        return card

    def draw_to_hand(self) -> Card | None:
        if not self.deck:
            return None

        card = self.deck.pop()
        self.hand.append(card)
        return card

    def render_played_card(self) -> None:
        if self.played_card is None:
            return

        kn.renderer.draw(get_card_texture(self.played_card.ID), dst=self.play_rect)
