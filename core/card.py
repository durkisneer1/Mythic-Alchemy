from dataclasses import dataclass


@dataclass
class Card:
    ID: int
    attack: int
    defense: int
    is_occupied: bool = False
