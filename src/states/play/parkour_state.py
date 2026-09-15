"""ParkourState: los jugadores se mueven por el mapa y se lanzan/empujan
para pasarse la papa caliente antes de que explote."""

import pygame

from gale.state import BaseState


class ParkourState(BaseState):
    def enter(self, **kwargs) -> None:
        # TODO: personapas: list[Personapa], papa_timer: float
        self.personapas = []
        self.papa_timer: float = 0.0

    def on_input(self, input_id, input_data) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def countdown(self) -> None:
        pass

    def check_collisions(self) -> None:
        pass

    def sink_tiles(self) -> None:
        pass
