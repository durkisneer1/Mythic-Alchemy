import pykraken as kn
from core.constants import SCN_SIZE
from core.deck import load_card_textures
from states.base_state import BaseState
from states.battle_state import BattleState
from core.enums import StateEnum


class Root:
    def __init__(self):
        kn.init()
        kn.window.create("Card Game", SCN_SIZE)
        kn.time.set_target(240)

        load_card_textures()

        self.font = kn.Font("kraken-clean", 32)

        self.states: dict[StateEnum, BaseState] = {
            StateEnum.BATTLE: BattleState(self),
        }
        self.current_state = StateEnum.BATTLE

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
