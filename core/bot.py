import pykraken as kn
from random import random, shuffle
from core.card import Card
from core.constants import CARD_SIZE, SCN_SIZE
from core.deck import load_deck, get_card_texture, check_fusion


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

        fused_card = self._maybe_fuse_from_deck()
        if fused_card is not None:
            self.hand.append(fused_card)
            self.played_card = fused_card
            return fused_card

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

    def _maybe_fuse_from_deck(self) -> Card | None:
        if len(self.deck) < 2:
            return None

        if random() >= 0.5:
            return None

        indices = list(range(len(self.deck)))
        shuffle(indices)

        for i, first in enumerate(indices):
            for second in indices[i + 1:]:
                fusion = check_fusion((self.deck[first].ID, self.deck[second].ID))
                if fusion is None:
                    continue

                for idx in sorted((first, second), reverse=True):
                    self.deck.pop(idx)

                return Card(
                    ID=fusion.ID,
                    attack=fusion.attack,
                    defense=fusion.defense
                )

        return None
