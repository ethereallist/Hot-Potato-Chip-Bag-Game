"""Clase principal del juego.

Hereda de gale.game.Game y sustituye al GameStateManager / GameState
del diagrama: en Gale ese rol lo cumplen Game + gale.state.StateMachine,
cuyos estados (MenuState, PlayState, WinState) heredan de BaseState.
"""

import pygame

from gale.game import Game
from gale.state import StateMachine

from src.states.menu_state import MenuState
from src.states.play_state import PlayState
from src.states.win_state import WinState


class HotPotatoChipBagGame(Game):
    def init(self) -> None:
        self.state_machine = StateMachine(
            {
                "menu": MenuState,
                "play": PlayState,
                "win": WinState,
            }
        )
        self.state_machine.change("menu")

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)

    def on_input(self, input_id, input_data) -> None:
        self.state_machine.on_input(input_id, input_data)