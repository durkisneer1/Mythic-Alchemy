import math
from enum import Enum, auto
import pykraken as kn
from core.deck import get_card_texture
from core.utils import exp_lerp


HOVER_RAISE = 20
HOVER_SCALE = 1.08
HOVER_ROTATION = math.radians(6)
HOVER_EPSILON = 1e-3
HOVER_SPEED = 10.0

ENTRY_OFFSET = 280
ENTRY_EPSILON = 1e-3
ENTRY_SPEED = 8.0

DRAG_TILT_MAX = math.radians(12)
DRAG_TILT_DAMP = 8.0
DRAG_TILT_SENS = 0.004


class CardLocation(Enum):
    HAND = auto()
    SLOT = auto()
    DRAG = auto()


class Card:
    def __init__(
        self,
        ID: int,
        attack: int,
        defense: int
    ):
        self.ID = ID
        self.attack = attack
        self.defense = defense
        self.location = CardLocation.HAND
        self.rotation = 0.0
        self.scale = 1.0
        self.dy = 0.0

        self.dragging = False
        self.drag_offset = kn.Vec2()

        self.texture = get_card_texture(ID)
        self.rect = self.texture.get_rect()
        self.anchor_pos = kn.Vec2(self.rect.x, self.rect.y)
        self.base_size = kn.Vec2(self.rect.size.x, self.rect.size.y)

        self.hover_amount = 0.0
        self.hover_target = 0.0
        self.hover_offset = 0.0
        self.entry_progress = 0.0
        self.entry_target = 0.0
        self.entry_offset = 0.0
        self.drag_rotation = 0.0
        self.drag_tilt_dir = 1.0

    def set_drag(self, drag: bool):
        self.dragging = drag
        if drag:
            self.drag_offset = kn.mouse.get_pos() - self.rect.top_left
            height = self.rect.size.y or 1.0
            pivot_ratio = self.drag_offset.y / height
            self.drag_tilt_dir = -1.0 if pivot_ratio > 0.5 else 1.0
        else:
            self.drag_tilt_dir = 1.0

    def move_to(self, top_left: kn.Vec2) -> None:
        self.anchor_pos = kn.Vec2(top_left.x, top_left.y)
        self._sync_rect_with_anchor()

    def contains_point(self, point: kn.Vec2) -> bool:
        return kn.collision.overlap(self._hover_hit_rect(), point)

    def update_drag_position(self) -> None:
        if self.dragging:
            self.rect.top_left = kn.mouse.get_pos() - self.drag_offset
            rel_x = kn.mouse.get_rel().x

            # impulse based on horizontal movement
            self.drag_rotation += rel_x * DRAG_TILT_SENS * self.drag_tilt_dir
            self.drag_rotation = max(-DRAG_TILT_MAX, min(DRAG_TILT_MAX, self.drag_rotation))

        # time-based damping so it feels the same at any FPS
        self.drag_rotation *= math.exp(-DRAG_TILT_DAMP * kn.time.get_delta())

    def begin_hand_entry(self) -> None:
        self.location = CardLocation.HAND
        self.entry_progress = 1.0
        self.entry_target = 0.0
        self.entry_offset = ENTRY_OFFSET
        self.dy = self.entry_offset
        self._sync_rect_with_anchor()

    def start_drag(self) -> None:
        self.entry_progress = 0.0
        self.entry_offset = 0.0
        self.set_hovered(False)
        self._settle_hover()
        self.location = CardLocation.DRAG
        self.set_drag(True)

    def place_in_slot(self, slot_rect: kn.Rect) -> None:
        self.move_to(kn.Vec2(slot_rect.x, slot_rect.y))
        self._settle_hover()
        self.set_drag(False)
        self.entry_progress = 0.0
        self.entry_offset = 0.0
        self.location = CardLocation.SLOT

    def return_to_hand(self) -> None:
        self.set_drag(False)
        self.location = CardLocation.HAND

    def set_hovered(self, hovered: bool) -> None:
        self.hover_target = 1.0 if hovered else 0.0

    def update_hand_motion(self, dt: float) -> None:
        self._update_entry_motion(dt)
        self._update_hover_motion(dt)

        if self.location is CardLocation.HAND and not self.dragging:
            self.hover_offset = -HOVER_RAISE * self.hover_amount
            self.dy = self.entry_offset + self.hover_offset
            self.scale = 1.0 + (HOVER_SCALE - 1.0) * self.hover_amount
            self.rotation = HOVER_ROTATION * self.hover_amount
            self._sync_rect_with_anchor()

    def has_hover_elevation(self) -> bool:
        return self.hover_amount > HOVER_EPSILON

    def _sync_rect_with_anchor(self) -> None:
        size = self.base_size * self.scale
        offset = (size - self.base_size) * 0.5
        top_left = kn.Vec2(
            self.anchor_pos.x - offset.x,
            self.anchor_pos.y + self.dy - offset.y
        )
        self.rect = kn.Rect(top_left.x, top_left.y, size)

    def _hover_hit_rect(self) -> kn.Rect:
        size = self.base_size * self.scale
        offset = (size - self.base_size) * 0.5
        top_left = kn.Vec2(
            self.anchor_pos.x - offset.x,
            self.anchor_pos.y - offset.y
        )
        return kn.Rect(top_left.x, top_left.y, size)

    def _settle_hover(self) -> None:
        self.hover_amount = 0.0
        self.hover_target = 0.0
        self.hover_offset = 0.0
        self.scale = 1.0
        self.rotation = 0.0
        self.dy = self.entry_offset
        self._sync_rect_with_anchor()

    def _update_entry_motion(self, dt: float) -> None:
        if self.location is not CardLocation.HAND or self.dragging:
            self.entry_progress = 0.0
            self.entry_offset = 0.0
            return

        self.entry_progress = exp_lerp(
            self.entry_progress,
            self.entry_target,
            ENTRY_SPEED,
            dt
        )

        if abs(self.entry_target - self.entry_progress) < ENTRY_EPSILON:
            self.entry_progress = self.entry_target

        self.entry_offset = ENTRY_OFFSET * self.entry_progress

    def _update_hover_motion(self, dt: float) -> None:
        if self.location is not CardLocation.HAND or self.dragging:
            self.hover_target = 0.0

        self.hover_amount = exp_lerp(
            self.hover_amount,
            self.hover_target,
            HOVER_SPEED,
            dt
        )

        if abs(self.hover_target - self.hover_amount) < HOVER_EPSILON:
            self.hover_amount = self.hover_target

    def draw(self):
        combined_rotation = self.rotation + self.drag_rotation
        prev_angle = self.texture.angle
        self.texture.angle = combined_rotation
        kn.renderer.draw(self.texture, dst=self.rect)
        self.texture.angle = prev_angle
