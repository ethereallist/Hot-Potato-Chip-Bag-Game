"""Mapa: la grilla del nivel, manipulable por los jugadores durante
ConstructionState y usada para las colisiones durante ParkourState.

Tiene dos capas:
- una grilla con el TIPO de cada casilla (suelo, hueco, pared)
- otra grilla con el ÍNDICE del Objeto colocado en cada casilla (o None)

Cada tipo de casilla resuelve la colisión con una Personapa de forma
distinta (ver diagrama: suelo no hace nada, hueco hace caer al jugador
salvo que esté en dash, pared lo empuja hacia afuera).
"""

from enum import Enum, auto

import pygame


class TipoCasilla(Enum):
    SUELO = auto()
    HUECO = auto()
    PARED = auto()


class Mapa:
    def __init__(self, ancho: int, alto: int) -> None:
        self.ancho = ancho
        self.alto = alto

        # Capa 1: tipo de cada casilla (Grid2D de TipoCasilla)
        self.capa_casillas = [
            [TipoCasilla.SUELO for _ in range(ancho)] for _ in range(alto)
        ]

        # Capa 2: índice del Objeto colocado en cada casilla (o None)
        self.capa_indices_objetos = [
            [None for _ in range(ancho)] for _ in range(alto)
        ]

        # Lista de Objetos colocados en el mapa
        self.objetos = []

        # TODO: tiempo de pisado por casilla, usado en ParkourState
        # para priorizar qué casillas se hunden primero
        self.tiempo_pisado = [[0.0 for _ in range(ancho)] for _ in range(alto)]

    # --- Construcción (ConstructionState) ---

    def get_casilla(self, x: int, y: int) -> TipoCasilla:
        pass

    def set_casilla(self, x: int, y: int, tipo: TipoCasilla) -> None:
        pass

    def mover_casilla(self, origen: tuple, destino: tuple) -> None:
        pass

    def rotar_casilla(self, x: int, y: int) -> None:
        pass

    def colocar_objeto(self, obj, x: int, y: int) -> None:
        pass

    def quitar_objeto(self, x: int, y: int) -> None:
        pass

    def posicion_valida(self, x: int, y: int) -> bool:
        pass

    # --- Parkour (ParkourState): colisión según tipo de casilla ---

    def colisionar(self, personapa, x: int, y: int) -> None:
        """Despacha al método de colisión correspondiente según el tipo
        de casilla en (x, y)."""
        pass

    def colisionar_suelo(self, personapa) -> None:
        pass

    def colisionar_hueco(self, personapa) -> None:
        pass

    def colisionar_pared(self, personapa) -> None:
        pass

    # --- Hundimiento progresivo de casillas ---

    def registrar_pisado(self, x: int, y: int, dt: float) -> None:
        pass

    def hundir_casillas_random(self) -> None:
        pass

    # --- Render ---

    def render(self, surface: pygame.Surface) -> None:
        pass