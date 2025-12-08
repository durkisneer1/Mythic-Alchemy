import pykraken as kn
from random import shuffle
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.card import Card


Combo = tuple[int, int]

_card_textures: list[kn.Texture] = []
_fusion_table: dict[Combo, "Card"] = {}


def load_fusion_table() -> None:
    from core.card import Card
    global _fusion_table

    if _fusion_table:
        return  # Already loaded

    with open("assets/cards.json") as f:
        for card_data in json.load(f)["cards"]:
            if card_data["class"] != "Fusion":
                continue

            combo = tuple(card_data["combo"])
            _fusion_table[combo] = Card(
                ID=card_data["id"],
                attack=card_data["attack"],
                defense=card_data["defense"]
            )


def check_fusion(combo: Combo) -> "Card | None":
    card = _fusion_table.get(combo)
    flipped_card = _fusion_table.get((combo[1], combo[0]))

    if card is not None:
        return card
    if flipped_card is not None:
        return flipped_card

    return None


def load_card_textures() -> None:
    global _card_textures

    if _card_textures:
        return  # Already loaded

    with open("assets/cards.json") as f:
        for card_data in json.load(f)["cards"]:
            _card_textures.append(kn.Texture(card_data["image_path"]))


def get_card_texture(index: int) -> kn.Texture:
    return _card_textures[index]


def load_deck() -> list["Card"]:
    from core.card import Card

    with open("assets/cards.json") as f:
        card_data_list = json.load(f)["cards"]

    cards: list[Card] = []
    for _ in range(2):  # Two of each card per deck
        for card_data in card_data_list:
            if card_data["class"] == "Fusion":
                continue  # Skip fusion cards in deck loading

            cards.append(Card(
                ID=card_data["id"],
                attack=card_data["attack"],
                defense=card_data["defense"]
            ))

    shuffle(cards)
    return cards
