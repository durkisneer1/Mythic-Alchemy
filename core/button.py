import pykraken as kn


class Button:
    def __init__(self, text: kn.Text, pos: kn.Vec2):
        self.text = text
        self.pos = pos

        self.rect = text.get_rect()
        self.rect.inflate((20, 10))
        self.rect.top_left = pos

    def is_clicked(self) -> bool:
        mouse_pos = kn.mouse.get_pos()
        mouse_pressed = kn.mouse.is_just_pressed(kn.M_LEFT)
        return mouse_pressed and kn.collision.overlap(self.rect, mouse_pos)

    def draw(self) -> None:
        kn.draw.rect(self.rect, kn.color.DARK_GRAY)
        self.text.draw(self.rect.center, kn.Anchor.CENTER)
