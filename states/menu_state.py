import pykraken as kn
from core.enums import StateEnum
from states.base_state import BaseState
from core.button import Button
from core.constants import SCN_SIZE

from typing import TYPE_CHECKING, override
if TYPE_CHECKING:
    from main import Root

TITLE_OFFSET = kn.Vec2(0, -140)
SUBTITLE_OFFSET = kn.Vec2(0, -60)
START_OFFSET = kn.Vec2(0, 80)
QUIT_OFFSET = kn.Vec2(0, 180)


class MenuState(BaseState):
    def __init__(self, root: "Root"):
        super().__init__(root)

        self.bg_tex = kn.Texture("assets/background.png")

        self.title_txt = kn.Text(root.font_rune)
        self.title_txt.text = "Mythic Alchemy"
        self.title_rect = self.title_txt.get_rect()
        self.title_rect.center = kn.renderer.get_res() / 2 + TITLE_OFFSET

        self.subtitle_txt = kn.Text(root.font_sm)
        self.subtitle_txt.text = "Forge fusions. Command the arcane."
        self.subtitle_rect = self.subtitle_txt.get_rect()
        self.subtitle_rect.center = kn.renderer.get_res() / 2 + SUBTITLE_OFFSET

        start_txt = kn.Text(root.font)
        start_txt.text = "Begin the Duel"
        self.start_btn = Button(start_txt)

        quit_txt = kn.Text(root.font)
        quit_txt.text = "Quit"
        self.quit_btn = Button(quit_txt)

        self.footer_txt = kn.Text(root.font_sm)
        self.footer_txt.text = "Left click & drag cards to fuse"
        self.footer_rect = self.footer_txt.get_rect()
        self.footer_rect.bottom_mid = kn.Vec2(SCN_SIZE.x / 2, SCN_SIZE.y - 40)

    @override
    def handle_event(self, event: kn.Event) -> None:
        pass

    @override
    def update(self) -> None:
        if self.start_btn.is_clicked():
            # Rebuild battle state to ensure fresh decks/health/UI each run
            self.root.states[StateEnum.BATTLE] = self.root._make_battle_state()
            self.root.current_state = StateEnum.BATTLE
        if self.quit_btn.is_clicked():
            kn.window.close()

        # Background
        kn.renderer.draw(self.bg_tex, anchor=kn.Anchor.TOP_LEFT)

        # Title & subtitle
        self.title_txt.draw(self.title_rect.center, kn.Anchor.CENTER)
        self.subtitle_txt.draw(self.subtitle_rect.center, kn.Anchor.CENTER)

        # Start button
        self.start_btn.draw(kn.renderer.get_res() / 2 + START_OFFSET, kn.Anchor.CENTER)

        # Quit button
        self.quit_btn.draw(kn.renderer.get_res() / 2 + QUIT_OFFSET, kn.Anchor.CENTER)

        # Footer hint
        self.footer_txt.draw(self.footer_rect.bottom_mid, kn.Anchor.BOTTOM_MID)
