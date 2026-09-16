"""Personapa: el jugador durante ParkourState."""
 
import pygame
 
 
class Personapa:
    def __init__(self) -> None:
        self.posicion = pygame.Vector2(0, 0)
        self.velocidad_maxima: float = 200  # px/segundo
 
        # Intenciones que llena ControladorDelJugador a través de los Commands
        self.move_intent = pygame.Vector2(0, 0)
        self.main_action_intent: bool = False  # dash
        self.secondary_action_intent: bool = False
 
        self.apariencia = None
        self.es_la_papa: bool = False
        self.esta_vivo: bool = True
        self.tamano: int = 40  # ancho/alto del cuadrito, mientras no hay sprite
        self.collide_box = pygame.Rect(0, 0, self.tamano, self.tamano)
 
    def move(self, dt: float) -> None:
        direccion = self.move_intent
        if direccion.length_squared() > 0:
            direccion = direccion.normalize()
        self.posicion += direccion * self.velocidad_maxima * dt
        self.collide_box.topleft = (self.posicion.x, self.posicion.y)
 
    def dash(self) -> None:
        pass
 
    def handle_collision(self, obj) -> None:
        pass
 
    def render(self, surface: pygame.Surface) -> None:
        # placeholder: cuadrito blanco mientras no hay apariencia/sprite
        pygame.draw.rect(surface, "white", self.collide_box)