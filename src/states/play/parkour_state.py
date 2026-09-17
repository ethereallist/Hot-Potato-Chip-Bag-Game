"""ParkourState: los jugadores se mueven por el mapa y se lanzan/empujan
para pasarse la papa caliente antes de que explote."""

import random

import pygame

from gale.state import BaseState

from src.objects.personapa import Personapa
from src.objects.player_controller import PlayerController
from src.objects.gamepad_direct import GamepadDirectController
from src.states.map.map import Map, TileType


# Jugadores 1 y 2: teclado, vía Gale (funciona bien por eventos)
KEYBOARD_PLAYER_CONFIGS = [
    {
        "device": "keyboard",
        "left": "p1_left", "right": "p1_right", "up": "p1_up", "down": "p1_down",
        "main_action": "p1_main", "secondary_action": "p1_secondary",
    },
    {
        "device": "keyboard",
        "left": "p2_left", "right": "p2_right", "up": "p2_up", "down": "p2_down",
        "main_action": "p2_main", "secondary_action": "p2_secondary",
    },
]

START_POSITIONS = [(100, 100), (600, 100), (100, 400), (600, 400)]

COUNTDOWN_DURATION = 3.0
ROUND_DURATION = 20.0
SINK_START_DELAY = 6.0
SINK_INTERVAL = 2.0


class ParkourState(BaseState):
    def enter(self, **kwargs) -> None:
        self.personapas: list[Personapa] = []
        self.controllers: list[PlayerController] = []  # solo teclado, vía Gale

        for config, start_pos in zip(KEYBOARD_PLAYER_CONFIGS, START_POSITIONS):
            personapa = Personapa()
            personapa.position = pygame.Vector2(start_pos)
            personapa.collide_box.topleft = start_pos

            controller = PlayerController(config)
            controller.possessed_entity = personapa

            self.personapas.append(personapa)
            self.controllers.append(controller)

        # Jugador 3: mando, leído directo con pygame (sondeo, sin eventos de Gale)
        personapa_3 = Personapa()
        personapa_3.position = pygame.Vector2(START_POSITIONS[2])
        personapa_3.collide_box.topleft = START_POSITIONS[2]
        self.personapas.append(personapa_3)

        self.gamepad_controller = None
        try:
            self.gamepad_controller = GamepadDirectController(joystick_index=0, invert_y=True)
            self.gamepad_controller.possessed_entity = personapa_3
        except pygame.error:
            pass  # no hay mando conectado; el jugador 3 simplemente no se mueve

        # Jugador 4: todavía sin dispositivo asignado (falta un segundo mando).
        # Se crea igual para que aparezca en pantalla, pero se queda quieto
        # hasta que se le conecte un control (ver TODO más abajo).
        personapa_4 = Personapa()
        personapa_4.position = pygame.Vector2(START_POSITIONS[3])
        personapa_4.collide_box.topleft = START_POSITIONS[3]
        self.personapas.append(personapa_4)

        # TODO: cuando haya un segundo mando físico conectado, algo como:
        # self.gamepad_controller_2 = GamepadDirectController(joystick_index=1)
        # self.gamepad_controller_2.possessed_entity = personapa_4
        self.gamepad_controller_2 = None

        random.choice(self.personapas).is_hot_potato = True

        self.mapa = Map(x=0, y=0, columns=14, rows=10)
        self._construir_arena_de_prueba()

        self.countdown_time_left = COUNTDOWN_DURATION
        self.round_time_left = ROUND_DURATION
        self.sink_timer = SINK_START_DELAY

        self.death_log: list[dict] = []

        pygame.font.init()
        self._font = pygame.font.SysFont(None, 72)

    def _construir_arena_de_prueba(self) -> None:
        for col in range(self.mapa.columns):
            self.mapa.set_tile_by_index(col, 0, TileType.WALL)
            self.mapa.set_tile_by_index(col, self.mapa.rows - 1, TileType.WALL)
        for row in range(self.mapa.rows):
            self.mapa.set_tile_by_index(0, row, TileType.WALL)
            self.mapa.set_tile_by_index(self.mapa.columns - 1, row, TileType.WALL)
        self.mapa.set_tile_by_index(7, 5, TileType.HOLE)

    @property
    def in_countdown(self) -> bool:
        return self.countdown_time_left > 0

    def on_input(self, input_id: str, input_data) -> None:
        if self.in_countdown:
            return
        for controller in self.controllers:
            controller.on_input(input_id, input_data)
        # el mando NO pasa por aquí: se sondea directo en update()

    def update(self, dt: float) -> None:
        if self.in_countdown:
            self.countdown_time_left -= dt
            return

        if self.gamepad_controller is not None:
            self.gamepad_controller.poll()
        if self.gamepad_controller_2 is not None:
            self.gamepad_controller_2.poll()

        self.round_time_left -= dt

        for personapa in self.personapas:
            if personapa.is_alive:
                personapa.move(dt)

        self._check_tile_effects(dt)
        self._check_player_collisions()
        self._check_object_collisions()
        self._update_tile_sinking(dt)

        if self.round_time_left <= 0:
            self._explode_hot_potato()
            self._end_round()
        elif self._count_alive() <= 1:
            self._end_round()

    def _check_tile_effects(self, dt: float) -> None:
        for personapa in self.personapas:
            if not personapa.is_alive:
                continue
            col, row = self.mapa.pos_to_index(*personapa.collide_box.center)
            if col == -1:
                continue
            self.mapa.registrar_pisado(col, row, dt)
            was_alive = personapa.is_alive
            self.mapa.resolve_tile_collision(personapa, col, row)
            if was_alive and not personapa.is_alive:
                self.death_log.append({"personapa": personapa, "cause": "fell"})

    def _check_player_collisions(self) -> None:
        alive = [p for p in self.personapas if p.is_alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                if not a.collides_with(b):
                    continue
                if a.is_hot_potato:
                    a.is_hot_potato = False
                    b.is_hot_potato = True
                elif b.is_hot_potato:
                    b.is_hot_potato = False
                    a.is_hot_potato = True

    def _check_object_collisions(self) -> None:
        for personapa in self.personapas:
            if not personapa.is_alive:
                continue
            for obj in self.mapa.objects.values():
                personapa.handle_collision(obj)

    def _update_tile_sinking(self, dt: float) -> None:
        self.sink_timer -= dt
        if self.sink_timer <= 0:
            self.sink_timer = SINK_INTERVAL
            self.mapa.hundir_casillas_random()

    def _explode_hot_potato(self) -> None:
        for personapa in self.personapas:
            if personapa.is_hot_potato and personapa.is_alive:
                personapa.is_alive = False
                self.death_log.append({"personapa": personapa, "cause": "explosion"})

    def _count_alive(self) -> int:
        return sum(1 for p in self.personapas if p.is_alive)

    def _end_round(self) -> None:
        self.state_machine.change("score", death_log=self.death_log, personapas=self.personapas)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill("black")
        self.mapa.render(surface)

        for personapa in self.personapas:
            if not personapa.is_alive:
                continue
            personapa.render(surface)
            if personapa.is_hot_potato:
                pygame.draw.circle(
                    surface, "yellow", personapa.collide_box.center,
                    personapa.size // 2 + 6, width=3,
                )

        if self.in_countdown:
            numero = str(int(self.countdown_time_left) + 1)
            texto = self._font.render(numero, True, "white")
            rect = texto.get_rect(center=surface.get_rect().center)
            surface.blit(texto, rect)