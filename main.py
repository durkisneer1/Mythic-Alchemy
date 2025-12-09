import pykraken as kn
from core.constants import SCN_SIZE
from core.deck import load_card_textures, load_fusion_table
from states.base_state import BaseState
from states.battle_state import BattleState
from states.win_state import WinState
from states.lose_state import LoseState
from states.stale_state import StaleState
from core.enums import StateEnum
from states.menu_state import MenuState


class Root:
    def __init__(self):
        kn.init()

        kn.window.create("Mythic Alchemy", SCN_SIZE)
        # kn.window.set_fullscreen(True)
        kn.time.set_target(240)

        load_card_textures()
        load_fusion_table()

        self.font = kn.Font("assets/fonts/oldenglishtextmt.ttf", 64)
        self.font_sm = kn.Font("assets/fonts/oldenglishtextmt.ttf", 38)
        self.font_lg = kn.Font("assets/fonts/oldenglishtextmt.ttf", 128)
        self.font_rune = kn.Font("assets/fonts/RUNE.TTF", 96)

        self.states: dict[StateEnum, BaseState] = {
            StateEnum.MENU: MenuState(self),
            StateEnum.BATTLE: BattleState(self),
            StateEnum.WIN: WinState(self),
            StateEnum.LOSE: LoseState(self),
            StateEnum.STALE: StaleState(self),
        }
        self.current_state = StateEnum.MENU

        self.theme_music = kn.AudioStream("assets/audio/theme.wav", volume=0.3)
        self.theme_music.play(fade_in_ms=2000, loop=True)

    def _make_battle_state(self) -> BattleState:
        return BattleState(self)

    def __del__(self):
        kn.quit()

    def run(self):
        while kn.window.is_open():
            state = self.states[self.current_state]

            for event in kn.event.poll():
                state.handle_event(event)

            state.update()
            kn.renderer.present()


if __name__ == "__main__":
    Root().run()
