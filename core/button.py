import pykraken as kn


class Button:
    def __init__(self, text: kn.Text):
        self.text = text
        self.rect = text.get_rect()
        self.rect.inflate((24, 12))

        self.outline_rect = self.rect.copy()
        self.outline_rect.inflate((4, 4))

        # Base styling
        self.base_color = '#283540'
        self.outline_color = '#14182E'
        self.hover_color = '#30435a'
        self.base_text_color = self.text.color
        self.hover_text_color = '#FFAE70'

    def is_clicked(self) -> bool:
        mouse_pos = kn.mouse.get_pos()
        mouse_pressed = kn.mouse.is_just_pressed(kn.M_LEFT)
        return mouse_pressed and kn.collision.overlap(self.rect, mouse_pos)

    def draw(self, pos: kn.Vec2, anchor: kn.Anchor = kn.Anchor.TOP_LEFT) -> None:
        mouse_pos = kn.mouse.get_pos()

        if anchor == kn.Anchor.BOTTOM_MID:
            self.rect.bottom_mid = pos
        elif anchor == kn.Anchor.CENTER:
            self.rect.center = pos

        hovered = kn.collision.overlap(self.rect, mouse_pos)

        self.outline_rect.center = self.rect.center
        kn.draw.rect(self.outline_rect, self.outline_color)
        kn.draw.rect(self.rect, self.hover_color if hovered else self.base_color)

        # Text color swap on hover
        prev_color = self.text.color
        self.text.color = self.hover_text_color if hovered else self.base_text_color
        self.text.draw(self.rect.center, kn.Anchor.CENTER)
        self.text.color = prev_color
