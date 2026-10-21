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
        size = (self.virtual_width, self.virtual_height)
        try:
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.SCALED)
        except pygame.error:
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

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

    # Sustituye al __render de Gale: mismo trabajo, pero escalando
    # con la proporción correcta y centrando con barras negras.
    def _Game__render(self) -> None:
        self.render_surface.fill((0, 0, 0))
        self.render(self.render_surface)

        screen_w, screen_h = self.screen.get_size()
        scale = min(screen_w / self.virtual_width, screen_h / self.virtual_height)
        new_w = int(self.virtual_width * scale)
        new_h = int(self.virtual_height * scale)

        scaled = pygame.transform.smoothscale(self.render_surface, (new_w, new_h))

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, ((screen_w - new_w) // 2, (screen_h - new_h) // 2))
        pygame.display.update()