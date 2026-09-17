"""Settings del proyecto, sobreescribiendo gale.conf.global_settings.

Gale lee este archivo automáticamente si está en la raíz del proyecto
(mismo nivel que main.py).
"""

import os
import pathlib

import pygame
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

# --- Jugador 1: teclado (WASD + espacio dash + E secundaria) ---
InputHandler.set_keyboard_action(pygame.K_a, "p1_left")
InputHandler.set_keyboard_action(pygame.K_d, "p1_right")
InputHandler.set_keyboard_action(pygame.K_w, "p1_up")
InputHandler.set_keyboard_action(pygame.K_s, "p1_down")
InputHandler.set_keyboard_action(pygame.K_SPACE, "p1_main")
InputHandler.set_keyboard_action(pygame.K_e, "p1_secondary")

# --- Jugador 2: teclado (flechas + Z dash + X secundaria) ---
InputHandler.set_keyboard_action(pygame.K_LEFT, "p2_left")
InputHandler.set_keyboard_action(pygame.K_RIGHT, "p2_right")
InputHandler.set_keyboard_action(pygame.K_UP, "p2_up")
InputHandler.set_keyboard_action(pygame.K_DOWN, "p2_down")
InputHandler.set_keyboard_action(pygame.K_z, "p2_main")
InputHandler.set_keyboard_action(pygame.K_x, "p2_secondary")

# --- Jugador 3: mando (gamepad_id=0) ---
# Movimiento con el STICK DERECHO
InputHandler.set_gamepad_axis_action(GAMEPAD_AXIS_RIGHT_X, "axis_x", gamepad_id=0)
InputHandler.set_gamepad_axis_action(GAMEPAD_AXIS_RIGHT_Y, "axis_y", gamepad_id=0)
# D-pad también sirve para moverse (alternativa al stick)
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_DPAD_LEFT, "p3_left", gamepad_id=0)
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_DPAD_RIGHT, "p3_right", gamepad_id=0)
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_DPAD_UP, "p3_up", gamepad_id=0)
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_DPAD_DOWN, "p3_down", gamepad_id=0)
# Dash con el botón X
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_X, "p3_main", gamepad_id=0)
InputHandler.set_gamepad_button_action(GAMEPAD_BUTTON_B, "p3_secondary", gamepad_id=0)

# TODO: jugador 4 por un segundo mando (gamepad_id=1), mismo patrón que
# el jugador 3 pero con gamepad_id=1.

# TODO: resolución de ventana / resolución virtual
# WINDOW_WIDTH = 1280
# WINDOW_HEIGHT = 720

# usado por src/states/map/map.py
TILE_SIZE = 50