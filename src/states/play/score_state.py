"""ScoreState: lleva el puntaje de cada jugador, anima los podios y
decide si el juego terminó o si se pasa a una nueva ronda."""

import random
import pygame

from gale.state import BaseState
import settings
from podio import Podio

# window width: settings.WINDOW_WIDTH
# window height: settings.WINDOW_HEIGHT

_BOTTOM_MARGIN = 0.1 * settings.WINDOW_HEIGHT
_LATERAL_MARGIN = 0.16 * settings.WINDOW_WIDTH
_CENTER_AREA_WIDTH = settings.WINDOW_WIDTH - _LATERAL_MARGIN * 2
_PODIO_SEPARATION_RATIO = 1
_PODIO_WIDTH_RATIO = 2


class ScoreState(BaseState):
    def enter(self, **kwargs) -> None:
        self.player_count = kwargs.get("player_count", 0)
        self.podios = []

        if self.player_count > 0:
            podio_y = settings.WINDOW_HEIGHT - _BOTTOM_MARGIN

            if self.player_count == 1:
                podio_width = float(_CENTER_AREA_WIDTH)
                separation = 0.0
            else:
                total_units = (self.player_count * _PODIO_WIDTH_RATIO) + (
                    (self.player_count - 1) * _PODIO_SEPARATION_RATIO
                )
                unit_width = _CENTER_AREA_WIDTH / float(total_units)
                podio_width = unit_width * _PODIO_WIDTH_RATIO
                separation = unit_width * _PODIO_SEPARATION_RATIO

            current_x = float(_LATERAL_MARGIN)
            for _ in range(self.player_count):
                random_color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
                params = {
                    "x": current_x,
                    "y": podio_y,
                    "height": 200.0,
                    "width": podio_width,
                    "personapa_ref": None,
                    "color": random_color,
                }
                self.podios.append(Podio(params))
                current_x += podio_width + separation

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        for podio in self.podios:
            podio.render(surface)

    def on_input(self, input_id, input_data) -> None:
        pass

    def animate_scores(self) -> None:
        pass

    def verify_end_game(self) -> bool:
        pass
