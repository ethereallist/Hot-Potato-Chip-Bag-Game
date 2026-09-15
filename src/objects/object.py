"""Object: pieza colocable del mapa, manipulada durante ConstructionState
y con la que las Personapas colisionan durante ParkourState."""

import pygame


class Object:
    def __init__(self) -> None:
        self.posicion = pygame.Vector2()
        self.orientacion: int = 0
        self.forma_de_casillas = None  # TODO: forma/shape sobre la grilla
        self.collidebox = pygame.Rect(0, 0, 0, 0)

    def on_collide(self) -> None:
        pass
