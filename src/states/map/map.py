"""Mapa: la grilla del nivel, manipulable por los jugadores durante
ConstructionState y usada para las colisiones durante ParkourState.

Tiene dos capas:
- una grilla con el TIPO de cada casilla (suelo, hueco, pared)
- otra grilla con el ÍNDICE del Objeto colocado en cada casilla (o None)

Cada tipo de casilla resuelve la colisión con una Personapa de forma
distinta (ver diagrama: suelo no hace nada, hueco hace caer al jugador
salvo que esté en dash, pared lo empuja hacia afuera).
"""

import settings
from enum import IntEnum, auto

import pygame


class TileType(IntEnum):
    FLOOR = 0
    HOLE = 1
    WALL = 2

COLOR_PALETTE = {
    TileType.FLOOR: (170, 150, 120),   # marron
    TileType.HOLE: (50, 50, 50),     # Gris oscuro
    TileType.WALL: (240, 240, 240), # Gris claro
}

class Map:
    def __init__(self, x: float, y: float, columns: int, rows: int) -> None:
        self.x = x
        self.y = y
        self.columns = columns #cantidad de columnas
        self.rows = rows #cantidad de filas
        self.tile_size = settings.TILE_SIZE 

        # Capa 1: tipo de cada casilla (Grid2D de TileType)
        self.tile_layer = [
            [TileType.FLOOR for _ in range(columns)] for _ in range(rows)
        ]

        # Capa 2: índice del Objeto colocado en cada casilla (o None)
        self.object_layer = [
            [None for _ in range(columns)] for _ in range(rows)
        ]

        # Lista de Objetos colocados en el mapa
        self.objects = []

        # TODO: tiempo de pisado por casilla, usado en ParkourState
        # para priorizar qué casillas se hunden primero
        self.stood_time_layer = [[0.0 for _ in range(columns)] for _ in range(rows)]

    # --- Construcción (ConstructionState) ---

    def get_containing_tile(self, x: int, y: int) -> TileType:
        pass

    def get_tile(self, y:int,)

    def set_tile(self, x: int, y: int, tipo: TileType) -> None:
        pass

    def mover_tile(self, origen: tuple, destino: tuple) -> None:
        pass

    def rotar_tile(self, x: int, y: int) -> None:
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
        for row in range(self.rows):
            for col in range(self.columns):
                tile_value = self.tile_layer[row][col]
                
                # Obtiene el color correspondiente al valor (usa negro si no existe)
                color = COLOR_PALETTE.get(tile_value, (0, 0, 0))
                
                # Cálculo de la posición individual de cada rectángulo
                pos_x = self.x + (col * self.tile_size)
                pos_y = self.y + (row * self.tile_size)
                
                # Dibuja el rectángulo relleno
                rect = pygame.Rect(pos_x, pos_y, self.tile_size,  self.tile_size)
                pygame.draw.rect(surface, color, rect)
                
                # Opcional: Dibuja un borde delgado para delimitar las casillas
                pygame.draw.rect(surface, (0, 0, 0), rect, width=1)