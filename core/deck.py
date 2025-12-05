import pykraken as kn
from random import shuffle
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.card import Card


Combo = tuple[int, int]

_card_textures: list[kn.Texture] = []
_fusion_table: dict[Combo, int] = {}


def load_fusion_table() -> None:
    global _fusion_table

    if _fusion_table:
        return  # Already loaded

    with open("assets/cards.json") as f:
        for fusion_data in json.load(f)["cards"]:
            if fusion_data["class"] != "Fusion":
                continue

            combo = tuple(fusion_data["combo"])
            _fusion_table[combo] = fusion_data["id"]


def check_fusion(combo: Combo) -> int | None:
    card_id = _fusion_table.get(combo)
    flipped_id = _fusion_table.get((combo[1], combo[0]))

    if card_id is not None:
        return card_id
    if flipped_id is not None:
        return flipped_id

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
    for _ in range(2):  # Multiple copies of each card for testing
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
