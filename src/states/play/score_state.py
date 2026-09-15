"""ScoreState: lleva el puntaje de cada jugador, anima los podios y
decide si el juego terminó o si se pasa a una nueva ronda."""

import pygame

from gale.state import BaseState


class ScoreState(BaseState):
    def enter(self, **kwargs) -> None:
        # TODO: podios: list[Podio], panel: PanelDeInformacion
        self.podios = []
        self.panel = None

    def on_input(self, input_id, input_data) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def animate_scores(self) -> None:
        pass

    def verify_end_game(self) -> bool:
        pass
