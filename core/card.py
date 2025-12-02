from dataclasses import dataclass


@dataclass
class Card:
    texture_index: int
    attack: int
    defense: int
    is_occupied: bool = False
