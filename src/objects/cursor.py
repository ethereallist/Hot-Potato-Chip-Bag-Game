"""Cursor: controlado por un jugador durante ConstructionState para
tomar un Objeto de la CajaDeItems y colocarlo en el mapa."""

import pygame


class Cursor:
    def __init__(self) -> None:
        self.posicion = pygame.Vector2()
        self.velocidad = pygame.Vector2()
        self.intencion = None  # TODO: moverse, accion
        self.color = None
        self.sombrero = None
        self.contenido = None  # Objeto | None

    def select_item(self, obj) -> None:
        pass

    def rotate_item(self) -> None:
        pass

    def place_item(self) -> None:
        pass
