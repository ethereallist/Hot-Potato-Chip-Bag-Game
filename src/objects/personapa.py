"""Personapa: el jugador durante ParkourState."""

import pygame


class Personapa:
    def __init__(self) -> None:
        self.posicion = pygame.Vector2()
        self.velocidad = pygame.Vector2()
        self.intenciones = None  # TODO: movimiento, dash
        self.apariencia = None
        self.es_la_papa: bool = False
        self.esta_vivo: bool = True
        self.collide_box = pygame.Rect(0, 0, 0, 0)

    def move(self) -> None:
        pass

    def dash(self) -> None:
        pass

    def handle_collision(self, obj) -> None:
        pass
