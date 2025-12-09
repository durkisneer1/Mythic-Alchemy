import pykraken as kn
from states.base_state import BaseState
from core.enums import StateEnum
from core.button import Button
from core.constants import SCN_SIZE

from typing import TYPE_CHECKING, override
if TYPE_CHECKING:
    from main import Root

TITLE_OFFSET = kn.Vec2(0, -60)
BTN_OFFSET = kn.Vec2(0, 60)
BTN_GAP = 240


class StaleState(BaseState):
    def __init__(self, root: "Root"):
        super().__init__(root)
        self.bg_tex = kn.Texture("assets/background.png")

        self.title_txt = kn.Text(root.font_lg)
        self.title_txt.text = "Stalemate"
        self.title_rect = self.title_txt.get_rect()
        self.title_rect.center = SCN_SIZE / 2 + TITLE_OFFSET

        retry_txt = kn.Text(root.font)
        retry_txt.text = "Retry"
        self.retry_btn = Button(retry_txt)

        menu_txt = kn.Text(root.font)
        menu_txt.text = "Menu"
        self.menu_btn = Button(menu_txt)

    @override
    def handle_event(self, event: kn.Event) -> None:
        pass

    def _draw_buttons(self) -> None:
        center = SCN_SIZE / 2 + BTN_OFFSET
        self.retry_btn.draw(center + kn.Vec2(-BTN_GAP / 2, 0), kn.Anchor.CENTER)
        self.menu_btn.draw(center + kn.Vec2(BTN_GAP / 2, 0), kn.Anchor.CENTER)

    @override
    def update(self) -> None:
        if self.retry_btn.is_clicked():
            self.root.states[StateEnum.BATTLE] = self.root._make_battle_state()
            self.root.current_state = StateEnum.BATTLE
            self.root.theme_music.play(loop=True)
            return

        if self.menu_btn.is_clicked():
            self.root.current_state = StateEnum.MENU
            self.root.theme_music.play(loop=True)
            return

        kn.renderer.draw(self.bg_tex, anchor=kn.Anchor.TOP_LEFT)
        self.title_txt.draw(self.title_rect.center, kn.Anchor.CENTER)
        self._draw_buttons()
