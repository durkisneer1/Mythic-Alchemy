from enum import IntEnum, auto


class StateEnum(IntEnum):
    NONE = 0
    MENU = auto()
    BATTLE = auto()
    WIN = auto()
    LOSE = auto()
    STALE = auto()
