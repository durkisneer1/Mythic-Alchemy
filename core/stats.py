import pykraken as kn

HEALTH_OFFSET = kn.Vec2(192, 121)
DECK_OFFSET = kn.Vec2(192, 33)
NAME_OFFSET = kn.Vec2(20, 6)
RIBBON_OFFSET = kn.Vec2(40, -8)


class Stats:
    panel_texture: kn.Texture | None = None
    panel_rect: kn.Rect | None = None
    ribbon_texture: kn.Texture | None = None
    ribbon_rect: kn.Rect | None = None

    def __init__(self, font: kn.Font, font_sm: kn.Font, health: int, deck_size: int, name: str):
        if Stats.panel_texture is None:
            Stats.panel_texture = kn.Texture("assets/stats_panel.png")
            Stats.panel_rect = Stats.panel_texture.get_rect()
        if Stats.ribbon_texture is None:
            Stats.ribbon_texture = kn.Texture("assets/name_ribbon.png")
            Stats.ribbon_rect = Stats.ribbon_texture.get_rect()

        self.name_txt = kn.Text(font_sm)
        self.name_txt.text = name
        self.name_rect = self.name_txt.get_rect()
        self.name_rect.inflate((64, 0))

        self.health_txt = kn.Text(font)
        self.health_txt.text = str(health)

        self.deck_txt = kn.Text(font)
        self.deck_txt.text = str(deck_size)

    def set_health(self, health: int) -> None:
        self.health_txt.text = str(health)

    def set_deck_size(self, size: int) -> None:
        self.deck_txt.text = str(size)

    def render(self, pos: kn.Vec2, anchor: kn.Anchor) -> None:
        if anchor == kn.Anchor.TOP_LEFT:
            Stats.panel_rect.top_left = pos

            Stats.ribbon_rect.top_left = Stats.panel_rect.bottom_left + RIBBON_OFFSET
            self.name_rect.top_left = Stats.panel_rect.bottom_left + NAME_OFFSET

            health_pos = Stats.panel_rect.top_left + HEALTH_OFFSET
            deck_pos = Stats.panel_rect.top_left + DECK_OFFSET

        elif anchor == kn.Anchor.TOP_RIGHT:
            Stats.panel_rect.top_right = pos

            # Mirror offsets so right-side ribbon/name/text align symmetrically
            Stats.ribbon_rect.top_right = Stats.panel_rect.bottom_right + kn.Vec2(-RIBBON_OFFSET.x, RIBBON_OFFSET.y)
            self.name_rect.top_right = Stats.panel_rect.bottom_right + kn.Vec2(-NAME_OFFSET.x - 4, NAME_OFFSET.y)

            health_pos = Stats.panel_rect.top_right + kn.Vec2(-HEALTH_OFFSET.x, HEALTH_OFFSET.y)
            deck_pos = Stats.panel_rect.top_right + kn.Vec2(-DECK_OFFSET.x, DECK_OFFSET.y)

        kn.renderer.draw(Stats.ribbon_texture, dst=Stats.ribbon_rect)
        kn.renderer.draw(Stats.panel_texture, dst=Stats.panel_rect)

        self.health_txt.draw(health_pos)
        self.deck_txt.draw(deck_pos)

        self.name_txt.draw(self.name_rect.top_mid, anchor=kn.Anchor.TOP_MID)
