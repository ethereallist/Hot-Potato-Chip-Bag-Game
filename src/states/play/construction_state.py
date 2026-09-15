"""ConstructionState: los jugadores toman objetos de la caja de items y
los colocan/rotan en el mapa para definir el terreno de la próxima
ronda de ParkourState."""

import pygame

from gale.state import BaseState


class ConstructionState(BaseState):
    def enter(self, **kwargs) -> None:
        # TODO: caja: CajaDeItems, cursores: list[Cursor]
        self.caja = None
        self.cursores = []

    def on_input(self, input_id, input_data) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def validate_position(self, pos: pygame.Vector2) -> bool:
        pass

    def place_object(self, obj) -> None:
        pass
