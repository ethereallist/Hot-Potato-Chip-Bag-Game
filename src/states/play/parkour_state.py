"""ParkourState: los jugadores se mueven por el mapa y se lanzan/empujan
para pasarse la papa caliente antes de que explote."""

import random

import pygame

from gale.state import BaseState

from src.objects.personapa import Personapa
from src.objects.player_controller import PlayerController
from src.states.map.map import Mapa, TipoCasilla


# Un dict de configuración por jugador. Los nombres de acción (p1_left,
# p2_left, etc.) deben coincidir con lo que registre settings.py.
PLAYER_CONFIGS = [
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
    {
        "device": "gamepad", "gamepad_id": 0,
        "left": "p3_left", "right": "p3_right", "up": "p3_up", "down": "p3_down",
        "main_action": "p3_main", "secondary_action": "p3_secondary",
    },
    {
        "device": "gamepad", "gamepad_id": 1,
        "left": "p4_left", "right": "p4_right", "up": "p4_up", "down": "p4_down",
        "main_action": "p4_main", "secondary_action": "p4_secondary",
    },
]

START_POSITIONS = [(100, 100), (600, 100), (100, 400), (600, 400)]

COUNTDOWN_DURATION = 3.0   # segundos sin procesar input, antes de empezar
ROUND_DURATION = 20.0      # el reloj de la papa caliente/bomba
SINK_START_DELAY = 6.0     # a partir de cuándo empiezan a hundirse casillas
SINK_INTERVAL = 2.0        # cada cuánto se hunde una casilla nueva


class ParkourState(BaseState):
    def enter(self, **kwargs) -> None:
        self.personapas: list[Personapa] = []
        self.controllers: list[PlayerController] = []

        for config, start_pos in zip(PLAYER_CONFIGS, START_POSITIONS):
            personapa = Personapa()
            personapa.position = pygame.Vector2(start_pos)
            personapa.collide_box.topleft = start_pos

            controller = PlayerController(config)
            controller.possessed_entity = personapa  # el vínculo pedido

            self.personapas.append(personapa)
            self.controllers.append(controller)

        # se decide al azar quién es la papa caliente
        random.choice(self.personapas).is_hot_potato = True

        # TODO: este mapa debería venir de ConstructionState; mientras esa
        # fase no exista, se genera una arena de prueba con borde de pared
        # y un hueco, solo para poder probar ParkourState de forma aislada
        self.mapa = Mapa(ancho=14, alto=10, tile_size=50)
        self._construir_arena_de_prueba()

        self.countdown_time_left = COUNTDOWN_DURATION
        self.round_time_left = ROUND_DURATION
        self.sink_timer = SINK_START_DELAY

        self.death_log: list[dict] = []

        pygame.font.init()
        self._font = pygame.font.SysFont(None, 72)

    def _construir_arena_de_prueba(self) -> None:
        for x in range(self.mapa.ancho):
            self.mapa.set_casilla(x, 0, TipoCasilla.PARED)
            self.mapa.set_casilla(x, self.mapa.alto - 1, TipoCasilla.PARED)
        for y in range(self.mapa.alto):
            self.mapa.set_casilla(0, y, TipoCasilla.PARED)
            self.mapa.set_casilla(self.mapa.ancho - 1, y, TipoCasilla.PARED)
        self.mapa.set_casilla(7, 5, TipoCasilla.HUECO)

    @property
    def in_countdown(self) -> bool:
        return self.countdown_time_left > 0

    def on_input(self, input_id: str, input_data) -> None:
        if self.in_countdown:
            return  # durante el countdown no se procesa el input del jugador

        for controller in self.controllers:
            controller.on_input(input_id, input_data)

    def update(self, dt: float) -> None:
        if self.in_countdown:
            self.countdown_time_left -= dt
            return

        # se empieza y observa el reloj de la bomba/papa caliente
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
        # se observa sobre qué casillas están posicionados los jugadores,
        # aplicando efectos donde sea relevante, y se cuenta el tiempo de
        # pisado de las casillas
        for personapa in self.personapas:
            if not personapa.is_alive:
                continue

            gx, gy = self.mapa.casilla_en(personapa.collide_box.center)
            self.mapa.registrar_pisado(gx, gy, dt)

            was_alive = personapa.is_alive
            self.mapa.colisionar(personapa, gx, gy)
            if was_alive and not personapa.is_alive:
                self.death_log.append({"personapa": personapa, "cause": "fell"})

    def _check_player_collisions(self) -> None:
        # se observa colisión entre jugadores para pasarse la papa
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
        # se observa colisión de jugadores con objetos, llamando al
        # método de colisión del objeto cuando sucede
        for personapa in self.personapas:
            if not personapa.is_alive:
                continue
            for obj in self.mapa.objetos:
                personapa.handle_collision(obj)

    def _update_tile_sinking(self, dt: float) -> None:
        # tras cierto tiempo se empieza a hundir casillas al azar,
        # priorizando las que más tiempo de pisado tienen
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
        # si se acabó el tiempo o queda solo un jugador vivo, se pasa al
        # estado score junto con la información de quién y cómo murió
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
