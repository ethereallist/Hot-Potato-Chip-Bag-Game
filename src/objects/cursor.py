"""Cursor: controlado por un jugador durante ConstructionState para
tomar un Objeto de la CajaDeItems y colocarlo en el mapa."""

import pygame

from gale.timer import Timer

_CURSOR_QUICKNESS = 80
_CURSOR_TARGET_OFFSET = pygame.Vector2(10,10)
_CURSOR_ANIMATION_DURATION = 0.2

class Cursor:
    def __init__(self, x: float, y: float, texture: pygame.Surface) -> None:
        self.position = pygame.Vector2(x, y)
        self.width, self.height = texture.get_size()
        self.animating = False
        
        # Intents filled in by PlayerController through the Commands
        self.move_intent = pygame.Vector2(0, 0) # normalized vector indicating the intended movement direction
        self.main_action_intent: bool = False  # click
        self.secondary_action_intent: bool = False
        
        self.texture: pygame.Surface = texture
        self.rate = 0
    
    def finish_animation(self):
        self.rate = 0
        self.animating = False

    def click_animation(self):
        self.animating = True
        self.rate = -1
        
        Timer.tween(
            _CURSOR_ANIMATION_DURATION,
            [(self,{"rate": 1})],
            ease_function_name="out_cubic",
            on_finish=self.finish_animation
        )

    def update(self, dt: float):
        if self.main_action_intent and not self.animating:
            self.click_animation()
            self.main_action_intent = False #the intent is consumed
        
        if (
            not self.animating
            and self.move_intent.length_squared() > 0.1
        ):
                self.position += self.move_intent.normalize() * _CURSOR_QUICKNESS * dt
    
    def render(self, surface: pygame.Surface):
        pos = self.position + _CURSOR_TARGET_OFFSET * (1 - abs(self.rate))
        surface.blit(self.texture, pos)
