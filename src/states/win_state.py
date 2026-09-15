"""WinState: pantalla de victoria. Tiene su propio temporizador (por
ejemplo, antes de volver automáticamente al menú)."""

import pygame

from gale.state import BaseState


class WinState(BaseState):
    def enter(self, **kwargs) -> None:
        # TODO: temporizador, jugador ganador
        pass

    def on_input(self, input_id, input_data) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass
