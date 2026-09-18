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
from gale.timer import Timer
from enum import IntEnum

import pygame
import random

class TileType(IntEnum):
    FLOOR = 0
    HOLE = 1
    WALL = 2
    SUNKEN = 3  # casilla que se ha hundido (se interpreta igual que HOLE a nivel de logica)

COLOR_PALETTE = {
    TileType.FLOOR: (170, 150, 120),
    TileType.HOLE: (50, 50, 50),
    TileType.SUNKEN: (50, 50, 50),
    TileType.WALL: (240, 240, 240),
}

TILE_TEXTURES = {
    TileType.FLOOR: settings.TEXTURES["floor_tiles"],
    TileType.HOLE: None,
    TileType.SUNKEN: None,
    TileType.WALL: settings.TEXTURES["wall_tiles"],
}

TILE_FRAMES = {
    TileType.FLOOR: settings.FRAMES["floor_tiles"],
    TileType.HOLE: [],
    TileType.SUNKEN: [],
    TileType.WALL: settings.FRAMES["wall_tiles"],
}
      
class VisualData():
    def __init__(
        self,
        frame_id: int,
    ):
        self.frame_id = frame_id
        self.y_offset = 0
        self.transparent_texture = None
        

class Map:
    def __init__(self, x: float, y: float, columns: int, rows: int) -> None:
        self.x = x
        self.y = y
        self.columns = columns
        self.rows = rows
        self.tile_size = settings.TILE_SIZE

        self.tile_layer = [
            [TileType.FLOOR for _ in range(columns)] for _ in range(rows)
        ]
        
        self.visual_data_layer = []
        self.set_up_visual_data_layer()
        
        self.tile_animations = []
        
        self.object_layer = [
            [-1 for _ in range(columns)] for _ in range(rows)
        ]
        self.object_counter = 0
        self.objects = {}

        self.sink_layer = []
        self.sink_list = []
        self.nonfloor_tile_count = 0
        self.recount_nonfloor_tiles()
        self.reset_sinking()

    # --- Construcción (ConstructionState) ---

    def set_up_visual_data_layer(self) -> None:
        for i in range(self.columns):
            col = []
            for j in range(self.rows):
                frame = random.randint(
                    0,
                    max(0,len(TILE_FRAMES[self.tile_layer[j][i]]) - 1)
                )
                col.append(VisualData(frame))
            self.visual_data_layer.append(col)

    def pos_is_inside_map(self, x: float, y: float) -> bool:
        return (
            (self.x <= x < self.x + self.columns * self.tile_size)
            and (self.y <= y < self.y + self.rows * self.tile_size)
        )

    def index_is_inside_map(self, col: int, row: int) -> bool:
        return (0 <= col < self.columns) and (0 <= row < self.rows)

    def pos_to_index(self, x: float, y: float) -> tuple[int, int]:
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
        tile = self.tile_layer[row][col]
        return TileType.HOLE if tile == TileType.SUNKEN else tile

    def get_tile_by_index(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        tile = self.tile_layer[row][col]
        return TileType.HOLE if tile == TileType.SUNKEN else tile

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
        self.tile_layer[row][col] = tile
        return True

    def set_tile_by_index(self, col: int, row: int, tile: TileType):
        if not self.index_is_inside_map(col, row):
            return False
        self.tile_layer[row][col] = tile
        return True

    def get_obj_by_pos(self, x: float, y: float):
        if not self.pos_is_inside_map(x, y):
            return None
        col, row = self.pos_to_index(x, y)
        return self.objects.get(self.object_layer[row][col])

    def get_obj_by_indexes(self, col: int, row: int):
        if not self.index_is_inside_map(col, row):
            return None
        return self.objects.get(self.object_layer[row][col])

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

    # --- Hundimiento progresivo de casillas (sistema de tu compañero) ---

    def reset_sinking(self) -> None:
        nonfloor_count_so_far = 0
        self.sink_layer = []
        floor_list = []
        nonfloor_list = []

        for i in range(self.columns):
            col = []
            self.sink_layer.append(col)
            for j in range(self.rows):
                if self.tile_layer[j][i] == TileType.FLOOR:
                    col.append(j + i * self.rows - nonfloor_count_so_far)
                    floor_list.append((i, j))
                else:
                    col.append(self.columns * self.rows - 1 - nonfloor_count_so_far)
                    nonfloor_list.append((i, j))
                    nonfloor_count_so_far += 1

        self.sink_list = floor_list
        for i in range(nonfloor_count_so_far):
            index_pair = nonfloor_list[nonfloor_count_so_far - 1 - i]
            self.sink_list.append(index_pair)

    def unsink(self):
        for i in range(self.columns):
            for j in range(self.rows):
                if self.tile_layer[j][i] == TileType.SUNKEN:
                    self.tile_layer[j][i] = TileType.FLOOR

    def recount_nonfloor_tiles(self):
        count = 0
        for i in range(self.columns):
            for j in range(self.rows):
                if not self.tile_layer[j][i] == TileType.FLOOR:
                    count += 1
        self.nonfloor_tile_count = count

    def swap_sinking_data(self, number: int, other: int) -> None:
        other_indx = self.sink_list[other]
        self.sink_list[other] = self.sink_list[number]
        self.sink_list[number] = other_indx
        self.sink_layer[self.sink_list[number][0]][self.sink_list[number][1]] = number
        self.sink_layer[self.sink_list[other][0]][self.sink_list[other][1]] = other

    def register_sink(self, x: float, y: float) -> None:
        if not self.pos_is_inside_map(x, y):
            return

        col, row = self.pos_to_index(x, y)
        if not self.tile_layer[row][col] == TileType.FLOOR:
            return

        old_number = self.sink_layer[col][row]
        new_number = max(0, old_number - 3)
        self.swap_sinking_data(old_number, new_number)

    def sink_random_tile(self) -> None:
        first_nonfloor_tile = self.columns * self.rows - self.nonfloor_tile_count
        if first_nonfloor_tile == 0:
            return
        r = random.random()
        rsqr = r * r
        number = int((first_nonfloor_tile - 1) * rsqr)
        self.sink_tile(number)
        self.swap_sinking_data(number, first_nonfloor_tile - 1)

    def sink_tile(self, number: int) -> None:
        col, row = self.sink_list[number]
        self.nonfloor_tile_count += 1
        self.tile_animations.append(
            TileAnimation(
                col,
                row,
                self.tile_layer[row][col],
                self.visual_data_layer[col][row].frame_id,
                self
            )
        )

    def update(self, dt: float) -> None:
        for a in self.tile_animations:
            a.update(dt)
        self.tile_animations = [a for a in self.tile_animations if not a.stage == AnimationStage.FINISHED]

    # --- Render ---

    def render(self, surface: pygame.Surface) -> None:
        for row in range(self.rows):
            for col in range(self.columns):
                tile_value = self.get_tile_by_index(col, row)
                if tile_value == TileType.HOLE:
                    continue
                
                color = COLOR_PALETTE.get(tile_value, (0, 0, 0))
                pos_x = self.x + (col * self.tile_size)
                pos_y = self.y + (row * self.tile_size)
                y_offset = self.visual_data_layer[col][row].y_offset
                
                if not (texture := TILE_TEXTURES[tile_value]) == None:
                    frame_id = self.visual_data_layer[col][row].frame_id
                    surface.blit(texture, (pos_x, pos_y + y_offset), TILE_FRAMES[tile_value][frame_id])
                else:
                    rect = pygame.Rect(pos_x, pos_y + y_offset, self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, color, rect)
                    pygame.draw.rect(surface, (0, 0, 0), rect, width=1)

SHAKING_DURATION = 0.7
SHAKE_HEIGHT = 10
SHAKE_LOOPS = 3
SHAKE_PERIOD = 1/SHAKE_LOOPS

SINKING_DURATION = 0.8
SINK_DISTANCE = settings.TILE_SIZE * 2

class AnimationStage(IntEnum):
    STILL = 0
    SHAKING = 1
    SINKING = 2
    FINISHED = 3

class TileAnimation():
    def __init__(
        self,
        col: int,
        row: int,
        tile_type: TileType,
        frame: int,
        map_ref: Map
    ):
        self.map_ref = map_ref
        self.col = col
        self.row = row
        self.alpha_rate = 1
        self.rate = 0
        self.texture = TILE_TEXTURES[tile_type].subsurface(
            TILE_FRAMES[tile_type][frame]
        ).copy()
        self.stage = AnimationStage.STILL
        
        self.start_animation()
    
    def start_animation(self) -> None:
        self.map_ref.visual_data_layer[self.col][self.row].texture = self.texture
        self.shake_animation()
    
    def shake_animation(self) -> None:
        self.stage = AnimationStage.SHAKING
        Timer.tween(
            SHAKING_DURATION,
            [(self,{"rate": 1})],
            ease_function_name="out_cubic",
            on_finish=self.sink_animation
        )
    
    def sink_animation(self) -> None:
        self.stage = AnimationStage.SINKING
        self.rate = 0
        Timer.tween(
            SHAKING_DURATION,
            [(self,{"rate": 1,"alpha_rate": 0})],
            ease_function_name="out_cubic",
            on_finish=self.finish
        )
        
    def finish(self) -> None:
        self.map_ref.tile_layer[self.row][self.col] = TileType.SUNKEN
        self.map_ref.visual_data_layer[self.col][self.row].texture = None
        self.stage = AnimationStage.FINISHED
        
    def update(self, dt: float) -> None:
        v_d = self.map_ref.visual_data_layer[self.col][self.row]
        if self.stage == AnimationStage.SHAKING:
            loop = self.rate//SHAKE_PERIOD #which loop are we in
            loop_progress = self.rate*SHAKE_LOOPS - loop #value from 0 to 1 indicating the animation loop progress
            shift_rate = 1 - abs(1 - loop_progress * 2) #goes from 0 to 1 to 0
            v_d.y_offset = shift_rate*SHAKE_HEIGHT
        elif self.stage == AnimationStage.SINKING:
            v_d.y_offset = self.rate * SINK_DISTANCE
            self.texture.set_alpha(max(0,min(255*self.alpha_rate,255)))