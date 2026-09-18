"""Definicion de la clase Transition, util para realizar efectos visuales
y suavizar el cambio entre estados del videojuego."""

import pygame
import settings
from gale.timer import Timer

_DEFAULT_COLOR = (40, 40, 40)

class TransitionBase:
    def __init__(self, duration: float = 1, **kwargs) -> None:
        self.finished = False
        self.color = kwargs.get("color", _DEFAULT_COLOR)
        self.rate = 0 #rate is a value between 0 and 1, represents the progress of the transition 
        self.o_f = kwargs.get("on_finish", None)
        e_f = kwargs.get("ease_function_name", "linear")
        if not self.o_f == None:
            Timer.tween(
                duration,
                [(self,{"rate":1})],
                ease_function_name=e_f,
                on_finish=self.finish
            )
        else:
            Timer.tween(
                duration,
                [(self,{"rate":1})],
                ease_function_name=e_f
            )
        
    def finish(self) -> None:
        self.finished = True
        self.o_f()
    
    def render(self, surface: pygame.Surface) -> None:
        pass
    
class FadeInOut(TransitionBase):
    def __init__(self, duration: float, **kwargs) -> None:
        super().__init__(duration, **kwargs)
        self.fade_out = kwargs.get("fade_out", True)

    def render(self, surface: pygame.Surface) -> None:
        temp_surface = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        temp_surface.fill(self.color)
        alpha = 0
        if self.fade_out:
            alpha = int(self.rate * 255)
        else:
            alpha = int((1.0 - self.rate) * 255)
        
        alpha = max(0, min(255, alpha))

        temp_surface.set_alpha(alpha)
        surface.blit(temp_surface, (0, 0))