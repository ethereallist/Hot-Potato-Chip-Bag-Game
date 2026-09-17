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
import random


class TileType(IntEnum):
    FLOOR = 0
    HOLE = 1
    WALL = 2

COLOR_PALETTE = {
    TileType.FLOOR: (170, 150, 120),    # marron
    TileType.HOLE: (50, 50, 50),        # Gris oscuro
    TileType.SUNKEN: (50, 50, 50),      # Gris oscuro
    TileType.WALL: (240, 240, 240),     # Gris claro
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
            [-1 for _ in range(columns)] for _ in range(rows)
        ]

        # diccionario de Objetos colocados en el mapa
        # la key de un objeto es un numero
        self.object_counter = 0
        self.objects = {}

        # Lista y tabla de hundimiento, usado en ParkourState
        # para priorizar qué casillas se hunden primero
        self.sink_layer = []
        self.sink_list = []
        self.nonfloor_tile_count = 0
        self.recount_nonfloor_tiles()
        self.restart_sinking_structures()
    # --- Construcción (ConstructionState) ---

    def pos_is_inside_map(self, x: float, y: float) -> bool:
        return (
            (self.x <= x < self.x + self.columns * self.tile_size)
            and (self.y <= y < self.y + self.rows * self.tile_size)
        )
        
    def index_is_inside_map(self, col: int, row: int) -> bool:
        return (
            (0 <= col <= self.columns)
            and (0 <= row <= self.rows)
        )
        
    def pos_to_index(self, x: float, y: float) -> tuple(int,int):
        if not self.pos_is_inside_map(x,y):
            return (-1,-1)
            
        return (x//self.tile_size, y//self.tile_size)
        
    def index_to_pos(self, col: int, row: int):
        if not self.index_is_inside_map(col,row):
            return None
            
        return (self.x + col * self.tile_size, self.y + row * self.tile_size )
        
    def index_to_rel_pos(self, col: int, row: int):
        if not self.index_is_inside_map(col,row):
            return None
            
        return (col * self.tile_size, row * self.tile_size )
        
    def get_tile_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x,y):
            return None
        
        col, row = self.pos_to_index(x,y)
        tile = self.tile_layer[col][row]
        return TileType.HOLE if tile == TileType.SUNKEN else tile

    def get_tile_by_index(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        
        tile = self.tile_layer[col][row]
        return TileType.HOLE if tile == TileType.SUNKEN else tile
        
    def get_rect_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x,y):
            return None
        
        col, row = self.pos_to_index(x,y)
        return pygame.Rect(
            col * self.tile_size,
            row * self.tile_size,
            self.tile_size,
            self.tile_size
        )

    def get_rect_by_index(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        
        return pygame.Rect(
            col * self.tile_size,
            row * self.tile_size,
            self.tile_size,
            self.tile_size
        )
        
    def set_tile_by_pos(self, x: float, y: float, tile: TileType):
        if not self.pos_is_inside_map(x,y):
            return False
        
        col, row = self.pos_to_index(x,y)
        self.tile_layer[col][row] = tile
        return True

    def set_tile_by_index(self, col: int, row: int, tile: TileType):
        if not self.index_is_inside_map(col, row):
            return False
        
        self.tile_layer[col][row] = tile
        return True
        
    def get_obj_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x,y):
            return None
        
        col, row = self.pos_to_index(x,y)
        index = self.obj_layer[col][row]
        return self.objects[index]

    def get_obj_by_indexes(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        
        index = self.obj_layer[col][row]
        return self.objects[index]
        
    def get_obj_key_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x,y):
            return None
        
        col, row = self.pos_to_index(x,y)
        return self.obj_layer[col][row]

    def get_obj_key_by_indexes(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        
        return self.obj_layer[col][row]
        
    def remove_object_by_indexes(self, col: int, row: int, recursion_key: int = -1):
        if not self.index_is_inside_map(col, row):
            return
            
        tile_key = self.obj_layer[col][row]
        if recursion_key == -1: #no es un llamado recursivo
            if tile_key == -1: #la casilla esta vacia
                return
            else: #la casilla no estaba vacia
                self.obj_layer[col][row] = -1 #la vaciamos
                #llamamos recursivamente en las cuatro casillas adjacentes
                self.object_removal_recursion(col, row, tile_key)
                #tras la resolucion de los llamados recursivos
                #quitamos el objeto respectivo del diccionario
                self.objects.pop(tile_key) 
        elif recursion_key == tile_key: #si es llamado recursivo
            #como la casilla actual coincide
            #con el key que queremos eliminar del mapa
            self.obj_layer[col][row] = -1 #la vaciamos
            #llamamos recursivamente en las cuatro casillas adjacentes
            self.object_removal_recursion(col, row, recursion_key)
            
        #en caso de hacer un llamado recursivo sobre una casilla
        #no vacia pero de otra clave, simplemente se ignora
    
    def object_removal_recursion(self, col: int, row: int, recursion_key: int):
        self.remove_object_by_indexes(col - 1, row, recursion_key) #arriba
        self.remove_object_by_indexes(col, row + 1, recursion_key) #derecha        
        self.remove_object_by_indexes(col + 1, row, recursion_key) #abajo
        self.remove_object_by_indexes(col, row - 1, recursion_key) #izquierda
        
    def add_object(self, obj, base_indices: tuple[int, int], relative_indices_list: list[tuple[int, int]]) -> None:
        """
        Añade un objeto al diccionario de objetos y asigna el ID del objeto en
        las casillas de object_layer resultantes de sumar los índices relativos.
        """
        # 1. Guardar el objeto en el diccionario usando el contador como clave
        self.objects[self.object_counter] = obj
        
        base_col, base_row = base_indices

        # 2. Asignar el ID del objeto en cada posición calculada
        for rel_col, rel_row in relative_indices_list:
            target_col = base_col + rel_col
            target_row = base_row + rel_row

            # Verificar que la casilla destino esté dentro de los límites del mapa
            if self.index_is_inside_map(target_col, target_row):
                self.object_layer[target_row][target_col] = self.object_counter

        # 3. Incrementar el contador para el próximo objeto
        self.object_counter += 1

    # --- Hundimiento progresivo de casillas ---

    def reset_sinking(self) -> None:
        nonfloor_count_so_far = 0
        self.sink_layer = []
        floor_list = []
        nonfloor_list = []
        
        for i in range(self.columns):
            col = []
            self.sink_layer.append(col) 
            for j in range(self.rows):
                if self.tile_layer[i][j] == TileType.FLOOR:
                    col.append(j + i * self.rows - nonfloor_count_so_far)
                    floor_list.append((i,j))
                else:
                    col.append(self.columns * self.rows - 1 - nonfloor_count_so_far)
                    nonfloor_list.append((i,j))
                    nonfloor_count_so_far += 1
        
        self.sink_list = floor_list
        for i in range(nonfloor_count_so_far):
            index_pair = nonfloor_list[nonfloor_count_so_far - 1 - i]
            self.sink_list.append(index_pair)
                    
    def unsink(self):
        for i in range(columns): 
            for j in range(rows):
                if self.tile_layer[i][j] == TileType.SUNKEN:
                    self.tile_layer [i][j] = TileType.FLOOR
                    
    def recount_nonfloor_tiles(self):
        count = 0
        for i in range(columns): 
            for j in range(rows):
                if not self.tile_layer[i][j] == TileType.FLOOR:
                    count += 1
        self.nonfloor_tile_count = count
        
    def swap_sinking_data(self, number: int, other: int) ->:
        other_indx = self.sink_list[other]
        self.sink_list[other] = self.sink_list[number]
        self.sink_list[number] = other_indx
        self.sink_layer[self.sink_list[number][0]][self.sink_list[number][1]] = number
        self.sink_layer[self.sink_list[other][0]][self.sink_list[other][1]] = other
        
    def register_sink(self, x: float, y: float, dt: float) -> None:
        if not self.pos_is_inside_map(x,y):
            return
        
        col, row = pos_to_index(x,y)
        if not self.tile_layer[col][row] == TileType.FLOOR:
            return
        
        old_number = self.sink_layer[col][row]
        new_number = max(0, old_number - 3)
        self.swap_sinking_data(old_number, new_number)
        
    def sink_random_tile(self) -> None:
        first_nonfloor_tile = self.columns * self.rows - self.nonfloor_tile_count
        
        if first_nonfloor_tile == 0:
            return
        
        r = random.random()
        rsqr = r*r
        number = int((first_nonfloor_tile - 1) * rsqr)
        self.sink_tile(number)
        self.swap_sinking_data(number, first_nonfloor_tile - 1)
        
    def sink_tile(self, number: int) -> None:
        col, row = self.sink_list[number]
        self.tile_layer[col][row] = TileType.SUNKEN
        self.nonfloor_tile_count += 1

    # --- Render ---

    def render(self, surface: pygame.Surface) -> None:
        for row in range(self.rows):
            for col in range(self.columns):
                tile_value = self.get_tile_by_index[row][col]
                
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