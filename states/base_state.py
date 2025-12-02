from abc import ABC, abstractmethod
from pykraken import Event

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Root


class BaseState(ABC):
    def __init__(self, root: "Root") -> None:
        super().__init__()

        self.root = root

    @abstractmethod
    def handle_event(self, event: Event) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
