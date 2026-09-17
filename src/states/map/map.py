"""Mapa: la grilla del nivel, manipulable por los jugadores durante
ConstructionState y usada para las colisiones durante ParkourState.

Tiene dos capas:
- una grilla con el TIPO de cada casilla (suelo, hueco, pared)
- otra grilla con el ÍNDICE del Objeto colocado en cada casilla (o -1)

Cada tipo de casilla resuelve la colisión con una Personapa de forma
distinta (suelo no hace nada, hueco hace caer al jugador salvo que esté
en dash, pared lo empuja hacia afuera).
"""

import settings
from enum import IntEnum

import pygame


class TileType(IntEnum):
    FLOOR = 0
    HOLE = 1
    WALL = 2


COLOR_PALETTE = {
    TileType.FLOOR: (170, 150, 120),   # marron
    TileType.HOLE: (50, 50, 50),       # gris oscuro
    TileType.WALL: (240, 240, 240),    # gris claro
}


class Map:
    def __init__(self, x: float, y: float, columns: int, rows: int) -> None:
        self.x = x
        self.y = y
        self.columns = columns  # cantidad de columnas
        self.rows = rows        # cantidad de filas
        self.tile_size = settings.TILE_SIZE

        # Capa 1: tipo de cada casilla. Indexado [row][col], igual que en
        # render() y en add_object() más abajo.
        self.tile_layer = [
            [TileType.FLOOR for _ in range(columns)] for _ in range(rows)
        ]

        # Capa 2: índice del Objeto colocado en cada casilla (o -1)
        self.object_layer = [
            [-1 for _ in range(columns)] for _ in range(rows)
        ]

        self.object_counter = 0
        self.objects = {}

        # tiempo de pisado por casilla, usado para priorizar qué casillas
        # se hunden primero. Indexado [row][col].
        self.stood_time_layer = [[0.0 for _ in range(columns)] for _ in range(rows)]

    # --- Construcción (ConstructionState) ---

    def pos_is_inside_map(self, x: float, y: float) -> bool:
        return (
            (self.x <= x < self.x + self.columns * self.tile_size)
            and (self.y <= y < self.y + self.rows * self.tile_size)
        )

    def index_is_inside_map(self, col: int, row: int) -> bool:
        # BUG arreglado: era "<=" (permitía un índice de más, fuera de rango)
        return (0 <= col < self.columns) and (0 <= row < self.rows)

    def pos_to_index(self, x: float, y: float) -> tuple[int, int]:
        # BUG arreglado: faltaba restar self.x/self.y antes de dividir por
        # tile_size, así que si el mapa no arrancaba en (0, 0) el índice
        # calculado quedaba mal.
        if not self.pos_is_inside_map(x, y):
            return (-1, -1)

        col = int((x - self.x) // self.tile_size)
        row = int((y - self.y) // self.tile_size)
        return (col, row)

    def index_to_pos(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return (self.x + col * self.tile_size, self.y + row * self.tile_size)

    def index_to_rel_pos(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return (col * self.tile_size, row * self.tile_size)

    def get_tile_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x, y):
            return None
        col, row = self.pos_to_index(x, y)
        return self.tile_layer[row][col]  # BUG arreglado: estaba [col][row]

    def get_tile_by_index(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return self.tile_layer[row][col]  # BUG arreglado: estaba [col][row]

    def get_rect_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x, y):
            return None
        col, row = self.pos_to_index(x, y)
        return self.get_rect_by_index(col, row)

    def get_rect_by_index(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return pygame.Rect(
            self.x + col * self.tile_size,
            self.y + row * self.tile_size,
            self.tile_size,
            self.tile_size,
        )

    def set_tile_by_pos(self, x: float, y: float, tile: TileType):
        if not self.pos_is_inside_map(x, y):
            return False
        col, row = self.pos_to_index(x, y)
        self.tile_layer[row][col] = tile  # BUG arreglado: estaba [col][row]
        return True

    def set_tile_by_index(self, col: int, row: int, tile: TileType):
        if not self.index_is_inside_map(col, row):
            return False
        self.tile_layer[row][col] = tile  # BUG arreglado: estaba [col][row]
        return True

    def get_obj_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x, y):
            return None
        col, row = self.pos_to_index(x, y)
        # BUG arreglado: decía self.obj_layer (no existe); es self.object_layer
        index = self.object_layer[row][col]
        return self.objects.get(index)

    def get_obj_by_indexes(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        index = self.object_layer[row][col]
        return self.objects.get(index)

    def get_obj_key_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x, y):
            return None
        col, row = self.pos_to_index(x, y)
        return self.object_layer[row][col]

    def get_obj_key_by_indexes(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return self.object_layer[row][col]

    def remove_object_by_indexes(self, col: int, row: int, recursion_key: int = -1):
        if not self.index_is_inside_map(col, row):
            return

        tile_key = self.object_layer[row][col]
        if recursion_key == -1:
            if tile_key == -1:
                return
            self.object_layer[row][col] = -1
            self.object_removal_recursion(col, row, tile_key)
            self.objects.pop(tile_key, None)
        elif recursion_key == tile_key:
            self.object_layer[row][col] = -1
            self.object_removal_recursion(col, row, recursion_key)

    def object_removal_recursion(self, col: int, row: int, recursion_key: int):
        self.remove_object_by_indexes(col - 1, row, recursion_key)
        self.remove_object_by_indexes(col, row + 1, recursion_key)
        self.remove_object_by_indexes(col + 1, row, recursion_key)
        self.remove_object_by_indexes(col, row - 1, recursion_key)

    def add_object(self, obj, base_indices: tuple, relative_indices_list: list) -> None:
        self.objects[self.object_counter] = obj
        base_col, base_row = base_indices

        for rel_col, rel_row in relative_indices_list:
            target_col = base_col + rel_col
            target_row = base_row + rel_row
            if self.index_is_inside_map(target_col, target_row):
                self.object_layer[target_row][target_col] = self.object_counter

        self.object_counter += 1

    # --- Parkour (ParkourState): colisión según tipo de casilla ---

    def resolve_tile_collision(self, personapa, col: int, row: int) -> None:
        """Aplica el efecto correspondiente según el tipo de casilla en
        (col, row): suelo no hace nada, hueco hace caer (salvo dash),
        pared empuja hacia afuera."""
        tile = self.get_tile_by_index(col, row)

        if tile == TileType.HOLE:
            if not personapa.is_dashing:
                personapa.is_alive = False
        elif tile == TileType.WALL:
            tile_rect = self.get_rect_by_index(col, row)
            if not personapa.collide_box.colliderect(tile_rect):
                return
            overlap = personapa.collide_box.clip(tile_rect)
            if overlap.width < overlap.height:
                if personapa.collide_box.centerx < tile_rect.centerx:
                    personapa.position.x -= overlap.width
                else:
                    personapa.position.x += overlap.width
            else:
                if personapa.collide_box.centery < tile_rect.centery:
                    personapa.position.y -= overlap.height
                else:
                    personapa.position.y += overlap.height
            personapa.collide_box.topleft = (personapa.position.x, personapa.position.y)
        # TileType.FLOOR: no pasa nada

    # --- Hundimiento progresivo de casillas ---

    def registrar_pisado(self, col: int, row: int, dt: float) -> None:
        if self.index_is_inside_map(col, row):
            self.stood_time_layer[row][col] += dt

    def hundir_casillas_random(self) -> None:
        import random

        candidatos = []
        pesos = []
        for row in range(self.rows):
            for col in range(self.columns):
                if self.tile_layer[row][col] == TileType.FLOOR and self.stood_time_layer[row][col] > 0:
                    candidatos.append((col, row))
                    pesos.append(self.stood_time_layer[row][col])

        if not candidatos:
            return

        col, row = random.choices(candidatos, weights=pesos, k=1)[0]
        self.set_tile_by_index(col, row, TileType.HOLE)

    # --- Render ---

    def render(self, surface: pygame.Surface) -> None:
        for row in range(self.rows):
            for col in range(self.columns):
                tile_value = self.tile_layer[row][col]
                color = COLOR_PALETTE.get(tile_value, (0, 0, 0))
                pos_x = self.x + (col * self.tile_size)
                pos_y = self.y + (row * self.tile_size)
                rect = pygame.Rect(pos_x, pos_y, self.tile_size, self.tile_size)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, width=1)