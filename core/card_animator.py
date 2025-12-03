import pykraken as kn

from core.card import Card


class CardAnimator:
    def __init__(self):
        self.rotation = 0.0
        self.scale = 1.0
        self.t = 0.0
        self.animation_speed = 5.0

    def on_enter(self) -> None:
        self.scale = 1.1

    def on_exit(self) -> None:
        self.scale = 1.0

    def update(self, card_rect: kn.Rect) -> None:
        self.t += kn.time.get_delta() * self.animation_speed
        if self.t > 1.0:
            self.t = 1.0

        mouse_pos = kn.mouse.get_pos()
        if kn.collision.overlap(card_rect, mouse_pos):
            self.on_enter()
        else:
            self.on_exit()
