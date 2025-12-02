import pykraken as kn
from core.card import Card
from random import shuffle
import json


# Global card textures - loaded once, shared by all cards
_card_textures: list[kn.Texture] | None = None


def load_card_textures() -> None:
    global _card_textures

    if _card_textures is not None:
        return  # Already loaded

    with open("assets/cards.json") as f:
        card_data_list = json.load(f)["cards"]

    _card_textures = [kn.Texture(card_data["image_path"]) for card_data in card_data_list]


def get_card_texture(index: int) -> kn.Texture:
    return _card_textures[index]


def load_deck() -> list[Card]:
    with open("assets/cards.json") as f:
        card_data_list = json.load(f)["cards"]

    cards: list[Card] = []
    for _ in range(3):  # 3 copies of each card for testing
        for idx, card_data in enumerate(card_data_list):
            cards.append(Card(
                texture_index=idx,
                attack=card_data["attack"],
                defense=card_data["defense"]
            ))

    shuffle(cards)
    return cards
