import math
import pykraken as kn
from core.card import Card, CardLocation
from core.constants import CARD_SIZE, SCN_SIZE
from core.deck import get_card_texture
from states.base_state import BaseState
from core.player import Player
from core.bot import Bot
from core.fusion_table import FusionTable
from core.button import Button
from core.sequencer import Sequencer
from core.stats import Stats
from core.enums import StateEnum

from typing import TYPE_CHECKING, override
if TYPE_CHECKING:
    from main import Root


class BattleState(BaseState):
    def __init__(self, root: "Root"):
        super().__init__(root)

        self.player = Player()
        self.bot = Bot()

        self.player_stats = Stats(
            root.font, root.font_sm,
            self.player.health,
            len(self.player.deck) + len(self.player.hand),
            "You"
        )
        self.bot_stats = Stats(
            root.font, root.font_sm,
            self.bot.health,
            len(self.bot.deck),
            "Bot"
        )

        self.background_tex = kn.Texture("assets/background.png")
        self.fusion_table = FusionTable()

        self.dragged_card: Card | None = None

        play_txt = kn.Text(root.font)
        play_txt.text = "Play"
        self.play_btn = Button(play_txt)

        self.battling = False
        self.battle_sequencer = Sequencer([
            {"name": [
                self.fusion_table.hide,
            ], "duration": 0.8},
        ])

        self.played_card: Card | None = None
        self.bot_played_card: Card | None = None

        # Animation state for player card moving result -> lhs slot
        self.play_anim = kn.EasingAnimation(kn.ease.out_cubic, 0.65)
        self.play_start = kn.Vec2()
        self.play_end = kn.Vec2()
        self.played_rect = kn.Rect(0, 0, CARD_SIZE)

        # Animation state for bot card flying in from the right -> result slot
        self.bot_anim = kn.EasingAnimation(kn.ease.out_cubic, 0.65)
        self.bot_start = kn.Vec2()
        self.bot_end = kn.Vec2()
        self.bot_play_rect = kn.Rect(0, 0, CARD_SIZE)

        # Shake / attack resolution (sequential: player then bot)
        self.shake_phase: str = "idle"   # idle -> player -> bot -> done
        self.shake_elapsed = 0.0
        self.shake_duration = 0.35
        self.shake_gap_duration = 0.35
        self.shake_amp = 6.0
        self.shake_freq = 18.0
        self.player_attack_done = False
        self.bot_attack_done = False
        self.cards_used_count = 0

        self.table_show_duration = 0.8

        # Exit animations: slide player card left, bot card right
        self.play_exit_anim = kn.EasingAnimation(kn.ease.in_cubic, 0.55)
        self.play_exit_active = False
        self.play_exit_end = kn.Vec2()

        self.bot_exit_anim = kn.EasingAnimation(kn.ease.in_cubic, 0.55)
        self.bot_exit_active = False
        self.bot_exit_end = kn.Vec2()

        # SFX
        self.card_place_sfx = kn.Audio("assets/audio/card_place.wav", volume=0.5)
        self.play_card_sfx = kn.Audio("assets/audio/play_card.wav", volume=0.2)
        self.card_attack_sfx = kn.Audio("assets/audio/card_attack.wav", volume=0.2)
        self.victory_sfx = kn.Audio("assets/audio/victory.wav", volume=0.3)
        self.lose_sfx = kn.Audio("assets/audio/lose.wav", volume=0.3)

    @override
    def handle_event(self, event: kn.Event) -> None:
        if event.type == kn.MOUSE_BUTTON_DOWN and event.button == kn.M_LEFT:
            mouse_pos = kn.mouse.get_pos()
            for card in self.player.hand:
                if card.location is not CardLocation.HAND:
                    continue

                if card.contains_point(mouse_pos):
                    card.start_drag()
                    self.dragged_card = card
                    return

            # Check lhs fusion slot
            if (kn.collision.overlap(self.fusion_table.lhs_rect, mouse_pos)
                and self.fusion_table.lhs_card is not None
                ):
                self.dragged_card = self.fusion_table.lhs_card
                self.dragged_card.start_drag()
                self.fusion_table.lhs_card = None
                return

            # Check rhs fusion slot
            if (kn.collision.overlap(self.fusion_table.rhs_rect, mouse_pos)
                and self.fusion_table.rhs_card is not None
                ):
                self.dragged_card = self.fusion_table.rhs_card
                self.dragged_card.start_drag()
                self.fusion_table.rhs_card = None
                return

        elif event.type == kn.MOUSE_BUTTON_UP and event.button == kn.M_LEFT:
            if self.dragged_card is None:
                return

            self.dragged_card.update_drag_position()
            dropped_card_rect = self.dragged_card.rect

            # Check if over any fusion slot and place in nearest one
            if (kn.collision.overlap(dropped_card_rect, self.fusion_table.lhs_rect)
                or kn.collision.overlap(dropped_card_rect, self.fusion_table.rhs_rect)):

                self.card_place_sfx.play()

                dx_lhs = dropped_card_rect.x - self.fusion_table.lhs_rect.x
                dx_rhs = dropped_card_rect.x - self.fusion_table.rhs_rect.x

                if abs(dx_lhs) < abs(dx_rhs):
                    if self.fusion_table.lhs_card is not None:
                        self.fusion_table.lhs_card.return_to_hand()
                    self.dragged_card.place_in_slot(self.fusion_table.lhs_rect)
                    self.fusion_table.lhs_card = self.dragged_card
                    self.dragged_card = None
                    return

                if self.fusion_table.rhs_card is not None:
                    self.fusion_table.rhs_card.return_to_hand()

                self.dragged_card.place_in_slot(self.fusion_table.rhs_rect)
                self.fusion_table.rhs_card = self.dragged_card
                self.dragged_card = None
                return

            self.dragged_card.return_to_hand()
            self.dragged_card = None

    @override
    def update(self) -> None:
        if self.play_btn.is_clicked() and not self.battling:
            self.play_card()

        if self.battling:
            self.battle_sequencer.update()
            if self.battle_sequencer.done:
                self.battling = False

        kn.renderer.draw(self.background_tex, anchor=kn.Anchor.TOP_LEFT)
        self.player_stats.render(kn.Vec2(20, 20), kn.Anchor.TOP_LEFT)
        self.bot_stats.render(kn.Vec2(kn.renderer.get_res().x - 20, 20), kn.Anchor.TOP_RIGHT)

        self.play_btn.draw(self.fusion_table.table_rect.top_mid, kn.Anchor.BOTTOM_MID)
        self.fusion_table.render()
        self._render_play_sequence()
        self.player.render_hand()

    def play_card(self) -> None:
        self.played_card = self.fusion_table.fusion_result_card
        if self.played_card is None:
            return

        self.play_card_sfx.play()

        self.battle_sequencer.reset()
        self.battling = True

        # Player animation: move the fusion result to the lhs slot
        self.play_start = kn.Vec2(
            self.fusion_table.fusion_result_rect.top_left.x,
            self.fusion_table.fusion_result_rect.top_left.y
        )
        self.play_end = kn.Vec2(
            self.fusion_table.lhs_rect.top_left.x,
            self.fusion_table.lhs_rect.top_left.y
        )
        self.play_anim.start_pos = self.play_start
        self.play_anim.end_pos = self.play_end
        self.play_anim.restart()
        self.played_rect.top_left = self.play_start

        # Bot draws and animates its card from the right edge toward the fusion result slot
        self.bot_played_card = self.bot.draw_card()
        if self.bot_played_card is not None:
            self.bot_start = kn.Vec2(SCN_SIZE.x + CARD_SIZE.x, self.fusion_table.fusion_result_rect.top_left.y)
            self.bot_end = kn.Vec2(
                self.fusion_table.fusion_result_rect.top_left.x,
                self.fusion_table.fusion_result_rect.top_left.y
            )
            self.bot_anim.start_pos = self.bot_start
            self.bot_anim.end_pos = self.bot_end
            self.bot_anim.restart()
            self.bot_play_rect.top_left = self.bot_start
            self.bot_stats.set_deck_size(len(self.bot.deck))

        # Reset shake state for this battle resolution
        self.shake_phase = "idle"
        self.shake_elapsed = 0.0
        self.player_attack_done = False
        self.bot_attack_done = False
        self.cards_used_count = 0

        # Reset exit state
        self.play_exit_active = False
        self.bot_exit_active = False

        # Build a per-round sequencer timeline
        travel_duration = 0.65
        exit_duration = 0.55
        self.battle_sequencer = Sequencer([
            {"name": [self._seq_start_travel], "duration": travel_duration},
            {"name": [self._seq_start_player_shake], "duration": self.shake_duration},
            {"name": [self._seq_start_gap], "duration": self.shake_gap_duration},
            {"name": [self._seq_start_bot_shake], "duration": self.shake_duration},
            {"name": [self._seq_start_exit], "duration": exit_duration},
            {"name": [self._seq_show_table], "duration": self.table_show_duration},
            {"name": [self._seq_finish_round], "duration": 0.0},
        ])
        self.battling = True

        if self.fusion_table.lhs_card is not None:
            self.cards_used_count += 1
            self.player.hand.remove(self.fusion_table.lhs_card)
            self.fusion_table.lhs_card = None
        if self.fusion_table.rhs_card is not None:
            self.cards_used_count += 1
            self.player.hand.remove(self.fusion_table.rhs_card)
            self.fusion_table.rhs_card = None

    def _render_play_sequence(self) -> None:
        dt = kn.time.get_delta()

        # Player card animation: fusion result slot -> lhs slot
        if not self.play_anim.is_done and self.played_card is not None:
            pos = self.play_anim.step()
            self.played_rect.top_left = pos
        elif self.play_exit_active and not self.play_exit_anim.is_done and self.played_card is not None:
            pos = self.play_exit_anim.step()
            self.played_rect.top_left = pos
        elif self.play_exit_active and self.play_exit_anim.is_done and self.played_card is not None:
            self.played_rect.top_left = self.play_exit_end
        elif self.played_card is not None:
            self.played_rect.top_left = self.play_end

        if self.played_card is not None:
            dst = kn.Rect(self.played_rect.x, self.played_rect.y, self.played_rect.size)
            dst.top_left = self._shake_offset(dst.top_left, owner="player")
            kn.renderer.draw(get_card_texture(self.played_card.ID), dst=dst)

        # Bot card animation: right edge -> fusion result slot
        if self.bot_played_card is not None:
            if not self.bot_anim.is_done:
                pos = self.bot_anim.step()
                self.bot_play_rect.top_left = pos
            elif self.bot_exit_active and not self.bot_exit_anim.is_done:
                pos = self.bot_exit_anim.step()
                self.bot_play_rect.top_left = pos
            elif self.bot_exit_active and self.bot_exit_anim.is_done:
                self.bot_play_rect.top_left = self.bot_exit_end
            else:
                self.bot_play_rect.top_left = self.bot_end

            dst = kn.Rect(self.bot_play_rect.x, self.bot_play_rect.y, self.bot_play_rect.size)
            dst.top_left = self._shake_offset(dst.top_left, owner="bot")
            kn.renderer.draw(get_card_texture(self.bot_played_card.ID), dst=dst)

            if self.bot_anim.is_done:
                # Keep the bot's resting play rect aligned to the result slot
                self.bot.play_rect.top_left = self.bot_end
        # Advance shake timer (phase transitions are driven by sequencer callbacks)
        self._advance_shake_time(dt)

    def _shake_offset(self, base: kn.Vec2, owner: str) -> kn.Vec2:
        if self.shake_phase != owner:
            return base

        phase = self.shake_elapsed * self.shake_freq * (2.0 * math.pi)
        falloff = max(0.0, 1.0 - min(1.0, self.shake_elapsed / self.shake_duration))
        dx = math.sin(phase) * self.shake_amp * falloff
        dy = math.sin(phase * 0.7 + 1.3) * self.shake_amp * falloff
        return base + kn.Vec2(dx, dy)

    def _advance_shake_time(self, dt: float) -> None:
        if self.shake_phase not in ("player", "bot"):
            return
        self.shake_elapsed += dt

    def _start_shake_phase(self, phase: str) -> None:
        self.shake_phase = phase
        self.shake_elapsed = 0.0

        if phase == "player" and not self.player_attack_done and self.played_card and self.bot_played_card:
            dmg_to_bot = max(0, self.played_card.attack - self.bot_played_card.defense)
            self.bot.health -= dmg_to_bot
            self.bot_stats.set_health(self.bot.health)
            self.player_attack_done = True
        elif phase == "bot" and not self.bot_attack_done and self.played_card and self.bot_played_card:
            dmg_to_player = max(0, self.bot_played_card.attack - self.played_card.defense)
            self.player.health -= dmg_to_player
            self.player_stats.set_health(self.player.health)
            self.bot_attack_done = True

        self.card_attack_sfx.play()

    # Sequencer callbacks
    def _seq_start_travel(self) -> None:
        # Animations already configured in play_card; just ensure we restart
        self.play_anim.restart()
        self.bot_anim.restart()
        self.fusion_table.hide()

    def _seq_start_player_shake(self) -> None:
        self._start_shake_phase("player")

    def _seq_start_gap(self) -> None:
        self.shake_phase = "gap"
        self.shake_elapsed = 0.0

    def _seq_start_bot_shake(self) -> None:
        self._start_shake_phase("bot")

    def _seq_start_exit(self) -> None:
        # Player exits left
        if self.played_card is not None:
            self.play_exit_active = True
            self.play_exit_anim.start_pos = kn.Vec2(self.played_rect.top_left.x, self.played_rect.top_left.y)
            self.play_exit_end = kn.Vec2(-CARD_SIZE.x * 1.5, self.played_rect.top_left.y)
            self.play_exit_anim.end_pos = self.play_exit_end
            self.play_exit_anim.restart()

        # Bot exits right
        if self.bot_played_card is not None:
            self.bot_exit_active = True
            self.bot_exit_anim.start_pos = kn.Vec2(self.bot_play_rect.top_left.x, self.bot_play_rect.top_left.y)
            self.bot_exit_end = kn.Vec2(SCN_SIZE.x + CARD_SIZE.x * 1.5, self.bot_play_rect.top_left.y)
            self.bot_exit_anim.end_pos = self.bot_exit_end
            self.bot_exit_anim.restart()

    def _seq_show_table(self) -> None:
        self.fusion_table.show()

        # Refill hands while the table returns
        draws = max(1, min(2, self.cards_used_count)) if self.cards_used_count > 0 else 0
        for _ in range(draws):
            self.player.draw_card()
        self.player_stats.set_deck_size(len(self.player.deck) + len(self.player.hand))

    def _seq_finish_round(self) -> None:
        self.shake_phase = "done"

        # Remove played cards from hands
        if self.played_card is not None and self.played_card in self.player.hand:
            self.player.hand.remove(self.played_card)
        if self.bot_played_card is not None and self.bot_played_card in self.bot.hand:
            self.bot.hand.remove(self.bot_played_card)

        # Clear references to prevent stale rendering
        self.played_card = None
        self.bot_played_card = None

        # Refresh deck counts (total cards for player, deck only for bot)
        self.player_stats.set_deck_size(len(self.player.deck) + len(self.player.hand))
        self.bot_stats.set_deck_size(len(self.bot.deck))

        # Transition checks
        if self.player.health <= 0 and self.bot.health <= 0:
            self.root.theme_music.pause()
            self.root.current_state = StateEnum.STALE
            return

        if self.player.health <= 0:
            self.root.theme_music.pause()
            self.lose_sfx.play()
            self.root.current_state = StateEnum.LOSE
            return
        if self.bot.health <= 0:
            self.root.theme_music.pause()
            self.victory_sfx.play()
            self.root.current_state = StateEnum.WIN
            return

        player_cards_left = len(self.player.deck) + len(self.player.hand)
        bot_cards_left = len(self.bot.deck) + len(self.bot.hand)
        if player_cards_left == 0 or bot_cards_left == 0:
            self.root.theme_music.pause()
            self.root.current_state = StateEnum.STALE
