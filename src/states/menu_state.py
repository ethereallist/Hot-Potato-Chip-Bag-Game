"""MenuState: pantalla de menú principal. Tiene su propio temporizador
(por ejemplo, para animaciones de fondo o un countdown antes de habilitar
"start")."""

import pygame

from gale.state import BaseState


class MenuState(BaseState):
    def enter(self, **kwargs) -> None:
        # TODO: temporizador
        pass

    def on_input(self, input_id, input_data) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass
