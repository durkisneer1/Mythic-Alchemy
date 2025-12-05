import pykraken as kn


class Button:
    def __init__(self, text: kn.Text, pos: kn.Vec2):
        self.text = text
        self.pos = pos

        self.rect = text.get_rect()
        self.rect.inflate((20, 10))
        self.rect.top_left = pos

    def draw(self) -> None:
        kn.draw.rect(self.rect, kn.color.DARK_GRAY)
        self.text.draw(self.rect.center, kn.Anchor.CENTER)