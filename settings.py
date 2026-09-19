"""Settings del proyecto, sobreescribiendo gale.conf.global_settings.

Gale lee este archivo automáticamente si está en la raíz del proyecto
(mismo nivel que main.py).
"""

import os
import pathlib
import pygame

BASE_DIR = pathlib.Path(__file__).parent

from gale import frames

from gale.input_handler import (
    InputHandler,
    GAMEPAD_AXIS_RIGHT_X,
    GAMEPAD_AXIS_RIGHT_Y,
    GAMEPAD_BUTTON_X,
    GAMEPAD_BUTTON_B,
    GAMEPAD_BUTTON_DPAD_UP,
    GAMEPAD_BUTTON_DPAD_DOWN,
    GAMEPAD_BUTTON_DPAD_LEFT,
    GAMEPAD_BUTTON_DPAD_RIGHT,
)

# TODO: resolución de ventana / resolución virtual
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
# usado por src/states/map/map.py
TILE_SIZE = 48

SHAPES = {
    "cursor" : pygame.image.load(BASE_DIR / "assets" / "images" / "cursor_shape.png"),
}

TEXTURES = {
    "floor_tiles" : pygame.image.load(BASE_DIR / "assets" / "images" / "floor_tiles.png"),
    "wall_tiles" : pygame.image.load(BASE_DIR / "assets" / "images" / "wall_tiles.png"),
}

FRAMES = {
    "floor_tiles" : frames.generate_frames(TEXTURES["floor_tiles"], TILE_SIZE, TILE_SIZE + 10),
    "wall_tiles" : frames.generate_frames(TEXTURES["wall_tiles"], TILE_SIZE, TILE_SIZE + 10),
}

SOUNDS = {
    "lobby": "assets/sounds/lobby.mp3",
    "parkour": "assets/sounds/parkour.mp3",
    "victory": "assets/sounds/victory.mp3",
    "click": "assets/sounds/click.mp3",
    "hover": "assets/sounds/hover.mp3",
    "screams": [
        f"assets/sounds/scream-{i}.mp3" for i in range(1, 14)
    ]
}

# Le dice a SDL que cargue esta base de datos de mapeos ANTES de
# inicializar nada de mandos, para que mandos que no traen mapeo nativo
# en macOS (como algunos Xbox 360 Controller) sean reconocidos como
# "Game Controller", que es lo que Gale escucha por debajo. Tiene que
# ir ANTES de pygame.init().
_gamecontrollerdb_path = pathlib.Path(__file__).parent / "gamecontrollerdb.txt"
if _gamecontrollerdb_path.exists():
    os.environ["SDL_GAMECONTROLLERCONFIG_FILE"] = str(_gamecontrollerdb_path)

pygame.init()
InputHandler.init_gamepads()

# --- Jugador 1: teclado (WASD + E dash + Q secundaria) ---
InputHandler.set_keyboard_action(pygame.K_a, "p1_left")
InputHandler.set_keyboard_action(pygame.K_d, "p1_right")
InputHandler.set_keyboard_action(pygame.K_w, "p1_up")
InputHandler.set_keyboard_action(pygame.K_s, "p1_down")
InputHandler.set_keyboard_action(pygame.K_e, "p1_main")
InputHandler.set_keyboard_action(pygame.K_q, "p1_secondary")

# --- Jugador 2: teclado (flechas + SPACE dash + ENTER/RETURN secundaria) ---
InputHandler.set_keyboard_action(pygame.K_LEFT, "p2_left")
InputHandler.set_keyboard_action(pygame.K_RIGHT, "p2_right")
InputHandler.set_keyboard_action(pygame.K_UP, "p2_up")
InputHandler.set_keyboard_action(pygame.K_DOWN, "p2_down")
InputHandler.set_keyboard_action(pygame.K_SPACE, "p2_main")
InputHandler.set_keyboard_action(pygame.K_RETURN, "p2_secondary")

# --- Jugador 3: teclado (flechas + P dash + O secundaria) ---
InputHandler.set_keyboard_action(pygame.K_j, "p3_left")
InputHandler.set_keyboard_action(pygame.K_l, "p3_right")
InputHandler.set_keyboard_action(pygame.K_i, "p3_up")
InputHandler.set_keyboard_action(pygame.K_k, "p3_down")
InputHandler.set_keyboard_action(pygame.K_p, "p3_main")
InputHandler.set_keyboard_action(pygame.K_o, "p3_secondary")

# --- Jugador 4: teclado (flechas + Y dash + R secundaria) ---
InputHandler.set_keyboard_action(pygame.K_f, "p4_left")
InputHandler.set_keyboard_action(pygame.K_h, "p4_right")
InputHandler.set_keyboard_action(pygame.K_t, "p4_up")
InputHandler.set_keyboard_action(pygame.K_g, "p4_down")
InputHandler.set_keyboard_action(pygame.K_y, "p4_main")
InputHandler.set_keyboard_action(pygame.K_r, "p4_secondary")

# TODO: resolución de ventana / resolución virtual
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
# usado por src/states/map/map.py
TILE_SIZE = 50
