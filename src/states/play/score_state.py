"""ScoreState: lleva el puntaje de cada jugador, anima los podios y
decide si el juego terminó o si se pasa a una nueva ronda."""

import random
import pygame
from gale.timer import Timer

from gale.state import BaseState
import settings
from src.objects.podio import Podio

# window width: settings.WINDOW_WIDTH
# window height: settings.WINDOW_HEIGHT

_BOTTOM_MARGIN = 0.1 * settings.WINDOW_HEIGHT
_TOP_MARGIN = 0.4 * settings.WINDOW_HEIGHT
_LATERAL_MARGIN = 0.16 * settings.WINDOW_WIDTH
_CENTER_AREA_WIDTH = settings.WINDOW_WIDTH - _LATERAL_MARGIN * 2
_PODIO_TARGET_HEIGHT = settings.WINDOW_HEIGHT - _BOTTOM_MARGIN - _TOP_MARGIN
_PODIO_SEPARATION_RATIO = 1
_PODIO_WIDTH_RATIO = 2


class ScoreState(BaseState):
    def enter(self, **kwargs) -> None:
        self.play_state = kwargs["play_state"]
        self.death_log = kwargs.get("death_log", [])
        self.podios = []
        self.interact_allowed = False

        if self.play_state.player_count > 0:
            podio_y = settings.WINDOW_HEIGHT - _BOTTOM_MARGIN

            total_units = (self.play_state.player_count * _PODIO_WIDTH_RATIO) + (
                (self.play_state.player_count - 1) * _PODIO_SEPARATION_RATIO
            )
            unit_width = _CENTER_AREA_WIDTH / float(total_units)
            podio_width = unit_width * _PODIO_WIDTH_RATIO
            separation = unit_width * _PODIO_SEPARATION_RATIO
            to_tween = []

            current_x = float(_LATERAL_MARGIN)
            for i in range(self.play_state.player_count):
                random_color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
                params = {
                    "x": current_x,
                    "y": podio_y,
                    "height": 5.0,
                    "width": podio_width,
                    "personapa_ref": None,
                    "color": random_color,
                }
                self.podios.append(Podio(params))
                current_x += podio_width + separation
                
                to_tween.append(
                    (
                        self.podios[i],
                        {
                            "height" : 5 + _PODIO_TARGET_HEIGHT * self.play_state.scores[i]/self.play_state.target_score
                        }
                    )
                )
            
            Timer.after(5,self.allow_interaction)
            Timer.tween(0.6, to_tween, ease_function_name="out_cubic", on_finish=lambda: Timer.after(0.3,self.update_scores))
    
    def update_scores(self):
        to_tween = []
        if len(self.death_log) == 0:
            return
        for i in range(self.play_state.player_count):
            if self.death_log[i]:
                self.play_state.scores[i] += 1
                to_tween.append((
                    self.podios[i],
                    {
                        "height" : 5 + _PODIO_TARGET_HEIGHT * self.play_state.scores[i]/self.play_state.target_score
                    }
                ))
        Timer.tween(1, to_tween, ease_function_name="out_cubic")

    def update(self, dt: float) -> None:
        pass
        
    def allow_interaction(self):
        self.interact_allowed = True

    def render(self, surface: pygame.Surface) -> None:
        for podio in self.podios:
            podio.render(surface)

    def on_input(self, input_id, input_data) -> None:
        if self.interact_allowed:
            self.state_machine.change("parkour", play_state=self.play_state)

    def animate_scores(self) -> None:
        pass

    def verify_end_game(self) -> bool:
        pass
