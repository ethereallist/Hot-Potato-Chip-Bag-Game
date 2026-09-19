"""ParkourState: los jugadores se mueven por el mapa y se lanzan/empujan
para pasarse la papa caliente antes de que explote."""

import math
import random

import pygame

from gale.state import BaseState
from gale.timer import Timer
import settings

from src.objects.personapa import Personapa
from src.objects.player_controller import PlayerController
from src.objects.gamepad_direct import GamepadDirectController
from src.objects.personapa_sprite_renderer import PersonapaSpriteRenderer
from src.states.map.map import Map, TileType
from src.utilities.player_input_manager import PlayerTracker

_POTATO_PASS_DOWNTIME = 0.4

# Jugadores 1 y 2: teclado, vía Gale (funciona bien por eventos)
KEYBOARD_PLAYER_CONFIGS = []
for i in range(4):
    KEYBOARD_PLAYER_CONFIGS.append(PlayerTracker.get_player_keyboard_inputs(i+1))

START_POSITIONS = [
    (settings.TILE_SIZE * 2, settings.TILE_SIZE * 2),
    (settings.TILE_SIZE * 11, settings.TILE_SIZE * 2),
    (settings.TILE_SIZE * 2, settings.TILE_SIZE * 7),
    (settings.TILE_SIZE * 11, settings.TILE_SIZE * 7)
]

COUNTDOWN_DURATION = 3.0
ROUND_DURATION = 20.0
SINK_START_DELAY = 6.0
SINK_INTERVAL = 2.0
PERSONAPA_VISUAL_SCALE = 1.5  # tamaño del sprite al dibujarlo

EXPLOSION_SHAKE_DURATION = 0.5    # segundos que tiembla la pantalla
EXPLOSION_SHAKE_MAGNITUDE = 26    # qué tan fuerte tiembla, en píxeles
EXPLOSION_BLACKOUT_DELAY = 0.6      # espera esto antes de que el negro empiece a crecer, para que se vea la cascada completa
EXPLOSION_BLACKOUT_DURATION = 1.1  # segundos que tarda el negro en cubrir todo, UNA VEZ que empieza

# partículas que van de grandes a chicas: empiezan pocas y GRANDES, y
# cada una se "parte" en varias más chicas, y esas otra vez en más
# chicas todavía (4 generaciones: 0 grande -> 1 -> 2 -> 3 diminuta)
EXPLOSION_BIG_PARTICLE_COUNT = 8
EXPLOSION_CHILDREN_PER_SPLIT = 4
EXPLOSION_MAX_GENERATION = 3
EXPLOSION_SPLIT_DELAY = 0.15
EXPLOSION_GEN_RADIUS = [24, 14, 8, 4]
EXPLOSION_GEN_SPEED = [90, 150, 210, 280]
EXPLOSION_GEN_LIFE = [0.9, 0.65, 0.45, 0.3]
EXPLOSION_GEN_COLORS = [
    (200, 40, 0),     # generación 0 (grande): rojo oscuro
    (255, 120, 0),    # generación 1: naranja
    (255, 180, 20),   # generación 2: ámbar
    (255, 240, 120),  # generación 3 (diminuta): chispas casi blancas
]


class ExplosionParticle:
    """Partícula de la explosión que sabe "partirse" en varias más
    chicas después de EXPLOSION_SPLIT_DELAY segundos, hasta llegar a
    EXPLOSION_MAX_GENERATION (ahí ya no se parte más, solo se apaga)."""

    def __init__(self, x: float, y: float, vx: float, vy: float, generation: int) -> None:
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.generation = generation
        self.radius = EXPLOSION_GEN_RADIUS[generation]
        self.color = EXPLOSION_GEN_COLORS[generation]
        self.life = EXPLOSION_GEN_LIFE[generation]
        self.max_life = self.life
        self.split_timer = EXPLOSION_SPLIT_DELAY if generation < EXPLOSION_MAX_GENERATION else None

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.985
        self.vy *= 0.985
        self.life -= dt
        if self.split_timer is not None:
            self.split_timer -= dt

    @property
    def should_split(self) -> bool:
        return self.split_timer is not None and self.split_timer <= 0

    @property
    def is_alive(self) -> bool:
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        t = max(0.0, self.life / self.max_life)
        radius = max(1, int(self.radius * (0.6 + 0.4 * t)))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)


class ParkourState(BaseState):
    def enter(self, **kwargs) -> None:
        # Cargar la música de fondo para el Parkour
        pygame.mixer.music.load(settings.SOUNDS["parkour"])
        pygame.mixer.music.set_volume(0.02)  # Volumen a la mitad
        pygame.mixer.music.play(-1)

        self.play_state = kwargs["play_state"]

        # Personapas que ya venían caminando en el menú (si las hay) —
        # se REUTILIZAN tal cual, con su posición actual, en vez de
        # crear unas nuevas en START_POSITIONS.
        incoming = kwargs.get("personapas")

        self.personapas: list[Personapa] = []
        self.controllers: list[PlayerController] = []  # solo teclado, vía Gale

        for i, config in enumerate(KEYBOARD_PLAYER_CONFIGS):
            if incoming and i < len(incoming):
                personapa = incoming[i]
                personapa.move_intent = pygame.Vector2(0, 0)  # limpia el rumbo que traía del menú
            else:
                personapa = Personapa()
                personapa.position = pygame.Vector2(START_POSITIONS[i])

            controller = PlayerController(config)
            controller.possessed_entity = personapa

            self.personapas.append(personapa)
            self.controllers.append(controller)

        self._sprite_renderer = PersonapaSpriteRenderer()
        self._personapa_anim_time = [random.uniform(0, 1) for _ in self.personapas]

        # --- Efecto de explosión (partículas + temblor + apagón) ---
        self.round_ending = False
        self.round_end_timer = 0.0
        self.explosion_particles = None
        self.blackout_center = None
        self.blackout_progress = 0.0  # 0..1
        self.screen_shake_timer = 0.0
        self._round_ended = False

        random.choice(self.personapas).is_hot_potato = True

        self.mapa = Map(x=0, y=0, columns=14, rows=10)
        self._construir_arena_de_prueba()

        if "mapa" in kwargs:
            self.mapa = kwargs["mapa"]
            
        # NUEVO: Recalcular las listas de hundimiento basado en lo que
        # construyeron los jugadores, para que hunda solo el suelo (FLOOR).
        if hasattr(self, 'mapa'):
            self.mapa.reset_sinking()
        
        self.assign_hot_potato_randomly()
        self.pass_allowed = True
        self.countdown_time_left = COUNTDOWN_DURATION
        self.round_time_left = ROUND_DURATION
        self.sink_timer = SINK_START_DELAY

        self.death_log: list[bool] = [True for _ in range(self.play_state.player_count)]

        pygame.font.init()
        self._font = pygame.font.SysFont(None, 72)

        try:
            self._font = pygame.font.Font("assets/fonts/Hansief.otf", 72)
            self._hud_font = pygame.font.Font("assets/fonts/Hansief.otf", 28)
            self._hud_font_small = pygame.font.Font("assets/fonts/Hansief.otf", 12)
        except (FileNotFoundError, pygame.error):
            self._font = pygame.font.SysFont(None, 72)
            self._hud_font = pygame.font.SysFont(None, 28)
            self._hud_font_small = pygame.font.SysFont(None, 12)

        if "personapas" in kwargs:
            self.personapas = kwargs["personapas"]
            
            # 1. Revivir a todos para la nueva ronda y quitarles la papa
            # por si acaso alguien la tenía de la ronda anterior.
            for i, p in enumerate(self.personapas):
                p.is_alive = True
                p.alpha = 255            
                
                # Reubicarlos en su posición de inicio para la nueva ronda
                # (en vez de (0,0), que podría caer dentro de una pared)
                if i < len(START_POSITIONS):
                    p.position = pygame.Vector2(START_POSITIONS[i])
                
                # Le quitamos la papa a todos primero
                p.is_hot_potato = False

            # 2. Asignar la papa a un jugador AL AZAR
            jugador_elegido = random.choice(self.personapas)
            jugador_elegido.is_hot_potato = True

    def assign_hot_potato_randomly(self) -> None:
        """Le quita la papa a todos y se la asigna a alguien al azar
        entre los que siguen VIVOS (para no dársela a quien ya cayó en
        un hoyo o ya explotó). Se usa tanto al iniciar la ronda como
        cuando, a mitad de partida, el que tenía la papa muere y hay
        que pasarla a otro."""
        for p in self.personapas:
            p.is_hot_potato = False

        alive = [p for p in self.personapas if p.is_alive]
        if alive:
            random.choice(alive).is_hot_potato = True

    def _render_hud(self, surface: pygame.Surface) -> None:
        # --- Configuración de dimensiones y posición ---
        card_w, card_h = 280, 56
        card_x = (surface.get_width() - card_w) // 2
        card_y = 12
        border_radius = 14

        # Tiempo restante e intensidad
        time_left = max(0.0, self.round_time_left)
        progress = min(1.0, max(0.0, time_left / ROUND_DURATION))
        is_critical = time_left <= 5.0

        # --- 1. Sombra del contenedor (Efecto de profundidad) ---
        shadow_rect = pygame.Rect(card_x, card_y + 3, card_w, card_h)
        pygame.draw.rect(surface, (10, 10, 15), shadow_rect, border_radius=border_radius)

        # --- 2. Fondo principal flotante (Transparencia con superficie dedicada) ---
        hud_surface = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        bg_color = (20, 22, 32, 230)  # Azul oscuro / Grafito translúcido
        pygame.draw.rect(hud_surface, bg_color, (0, 0, card_w, card_h), border_radius=border_radius)

        # Borde exterior según el estado de la ronda
        border_color = (235, 75, 75) if (is_critical and int(time_left * 6) % 2 == 0) else (60, 64, 80)
        pygame.draw.rect(hud_surface, border_color, (0, 0, card_w, card_h), width=2, border_radius=border_radius)

        # --- 3. Barra de tiempo gráfica inferior ---
        bar_margin_x = 16
        bar_w = card_w - (bar_margin_x * 2)
        bar_h = 6
        bar_x = bar_margin_x
        bar_y = card_h - 12

        # Fondo de la barra
        pygame.draw.rect(hud_surface, (40, 44, 58), (bar_x, bar_y, bar_w, bar_h), border_radius=3)

        # Relleno de la barra (Cambia de dorado/naranja a rojo vivo cuando queda poco tiempo)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            bar_color = (245, 60, 60) if is_critical else (255, 175, 55)
            pygame.draw.rect(hud_surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        # --- 4. Renderizado del Texto con "Hansief.otf" ---
        segundos = int(time_left)
        milisegundos = int((time_left - segundos) * 100)
        texto_str = f"{segundos:02d}:{milisegundos:02d}"

        # Color del texto según urgencia
        if is_critical and int(time_left * 8) % 2 == 0:
            text_color = (255, 80, 80)
        else:
            text_color = (245, 245, 245)

        # Texto de etiqueta pequeñita ("PAPA HOT")
        ronda_actual = self.play_state.rounds + 1
        texto_label = f"¡PASA LA PAPA!  -  Ronda {ronda_actual}"
        label_surf = self._hud_font_small.render(texto_label, True, (160, 165, 180))
        hud_surface.blit(label_surf, (bar_x, 8))

        # Texto principal del reloj
        time_surf = self._hud_font.render(texto_str, True, text_color)
        time_rect = time_surf.get_rect(midright=(card_w - bar_margin_x, 20))

        # Sombra del texto
        shadow_time_surf = self._hud_font.render(texto_str, True, (15, 15, 20))
        hud_surface.blit(shadow_time_surf, (time_rect.x + 1, time_rect.y + 1))
        hud_surface.blit(time_surf, time_rect)

        # Blit final en la pantalla principal
        surface.blit(hud_surface, (card_x, card_y))

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
        if self.round_ending:
            self._update_explosion_effect(dt)
            return

        if self.in_countdown:
            self.countdown_time_left -= dt
            return

        self.round_time_left -= dt

        for i, personapa in enumerate(self.personapas):
            self._personapa_anim_time[i] += dt
            if personapa.is_alive:
                personapa.move(dt)

        self._check_tile_effects(dt)
        self._check_player_collisions()
        self._check_object_collisions()
        self._update_tile_sinking(dt)

        if self.round_time_left <= 0:
            self._explode_hot_potato()  # dispara la secuencia; _end_round() se llama sola al terminar
        elif self._count_alive() <= 1:
            self._end_round()

    def _check_tile_effects(self, dt: float) -> None:
        for i in range(len(self.personapas)):
            personapa = self.personapas[i]
            if not personapa.is_alive:
                continue
            
            tile = self.mapa.get_tile_by_pos(*personapa.get_rect().center)
            if (
                tile == TileType.HOLE
                or tile == None
            ):
                if not personapa.is_dashing:
                    personapa.is_alive = False
                    self.death_log[i] = False
                    if personapa.is_hot_potato:
                        self.assign_hot_potato_randomly()
                    continue
           
            self.mapa.register_sink(*personapa.get_rect().center)
            
            x, y = personapa.position
            leftoverlap, rightoverlap, upoverlap, downoverlap = 0, 0, 0, 0
            
            indexes = self.mapa.pos_to_index(x, y) #top-left
            if self.mapa.get_tile_by_index(*indexes) == TileType.WALL:
                clip = personapa.get_rect().clip(
                    self.mapa.get_rect_by_index(*indexes)
                )
                leftoverlap = max(leftoverlap, clip.width)
                upoverlap = max(upoverlap, clip.height)
                
            indexes = self.mapa.pos_to_index(x + personapa.size, y) #top-right
            if self.mapa.get_tile_by_index(*indexes) == TileType.WALL:
                clip = personapa.get_rect().clip(
                    self.mapa.get_rect_by_index(*indexes)
                )
                rightoverlap = max(rightoverlap, clip.width)
                upoverlap = max(upoverlap, clip.height)
                
            indexes = self.mapa.pos_to_index(x, y + personapa.size) #bottom-left
            if self.mapa.get_tile_by_index(*indexes) == TileType.WALL:
                clip = personapa.get_rect().clip(
                    self.mapa.get_rect_by_index(*indexes)
                )
                leftoverlap = max(leftoverlap, clip.width)
                downoverlap = max(downoverlap, clip.height)
                
            indexes = self.mapa.pos_to_index(x + personapa.size, y + personapa.size) #bottom-right
            if self.mapa.get_tile_by_index(*indexes) == TileType.WALL:
                clip = personapa.get_rect().clip(
                    self.mapa.get_rect_by_index(*indexes)
                )
                rightoverlap = max(rightoverlap, clip.width)
                downoverlap = max(downoverlap, clip.height)
               
            h_overlap = leftoverlap + rightoverlap
            v_overlap = upoverlap + downoverlap
            
            if h_overlap == 0:
                continue
            
            full_side_overlap = False
            
            if h_overlap == personapa.size:
                if upoverlap * downoverlap == 0:
                    personapa.position.y += upoverlap if upoverlap > 0 else -downoverlap
                else:
                    personapa.position.y += upoverlap if upoverlap < downoverlap else -downoverlap
                full_side_overlap = True
            
            if v_overlap == personapa.size:
                if leftoverlap * rightoverlap == 0:
                    personapa.position.x += leftoverlap if leftoverlap > 0 else -rightoverlap
                else:
                    personapa.position.x += leftoverlap if leftoverlap < rightoverlap else -rightoverlap
                full_side_overlap = True
            
            if full_side_overlap:
                continue
            
            if h_overlap < v_overlap:
                personapa.position.x +=  leftoverlap if leftoverlap > 0 else -rightoverlap
            else:
                personapa.position.y +=  upoverlap if upoverlap > 0 else -downoverlap
                
    def reallow_passing(self):
        self.pass_allowed = True
        
    def _check_player_collisions(self) -> None:
        if not self.pass_allowed:
            return
            
        alive = [p for p in self.personapas if p.is_alive]
        for i, a in enumerate(alive):
            for b in alive[i + 1:]:
                if not a.collides_with(b):
                    continue
                if a.is_hot_potato or b.is_hot_potato:
                    a.is_hot_potato = not a.is_hot_potato
                    b.is_hot_potato = not b.is_hot_potato
                    self.pass_allowed = False
                    Timer.after(_POTATO_PASS_DOWNTIME,self.reallow_passing)

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
            self.mapa.sink_random_tile()

    def _explode_hot_potato(self) -> None:
        for i in range(len(self.personapas)):
            personapa = self.personapas[i]
            if personapa.is_hot_potato and personapa.is_alive:
                personapa.is_alive = False
                self.death_log[i] = False
                self._start_explosion_effect(personapa.get_rect().center)

    def _start_explosion_effect(self, position: tuple) -> None:
        self.round_ending = True
        self.round_end_timer = 0.0
        self.blackout_center = position
        self.blackout_progress = 0.0
        self.screen_shake_timer = EXPLOSION_SHAKE_DURATION
        self._round_ended = False

        self.explosion_particles: list[ExplosionParticle] = []
        cx, cy = position
        for _ in range(EXPLOSION_BIG_PARTICLE_COUNT):
            self._spawn_explosion_particle(cx, cy, generation=0)

    def _spawn_explosion_particle(self, x: float, y: float, generation: int, base_vx: float = 0.0, base_vy: float = 0.0) -> None:
        speed = EXPLOSION_GEN_SPEED[generation]
        direction = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
        vx = base_vx * 0.3 + direction.x * speed
        vy = base_vy * 0.3 + direction.y * speed
        self.explosion_particles.append(ExplosionParticle(x, y, vx, vy, generation))

    def _update_explosion_effect(self, dt: float) -> None:
        self.round_end_timer += dt

        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt

        surviving = []
        new_children = []
        for p in self.explosion_particles:
            p.update(dt)
            if p.should_split:
                for _ in range(EXPLOSION_CHILDREN_PER_SPLIT):
                    new_children.append((p.x, p.y, p.generation + 1, p.vx, p.vy))
                continue  # la partícula grande desaparece, la reemplazan sus hijas
            if p.is_alive:
                surviving.append(p)
        self.explosion_particles = surviving
        for x, y, gen, vx, vy in new_children:
            self._spawn_explosion_particle(x, y, gen, vx, vy)

        # el "apagón" negro espera un poco (para que se vea la cascada
        # completa de partículas) y luego crece acelerando hasta cubrir
        # toda la pantalla, y ahí se pasa a la puntuación
        t = max(0.0, self.round_end_timer - EXPLOSION_BLACKOUT_DELAY) / EXPLOSION_BLACKOUT_DURATION
        t = min(1.0, t)
        self.blackout_progress = t * t

        if t >= 1.0 and not self._round_ended:
            self._round_ended = True
            self._end_round()

    def _count_alive(self) -> int:
        return sum(1 for p in self.personapas if p.is_alive)

    def _end_round(self) -> None:
        # Recorremos todas las personapas para desactivar la papa caliente
        for p in self.personapas:
            p.is_hot_potato = False

        self.state_machine.change(
            "score",
            death_log=self.death_log,
            play_state=self.play_state,
            personapas=self.personapas  # ¡Importante para poder dibujarlas en los podios!
        )

    def render(self, surface: pygame.Surface) -> None:
        if self.round_ending:
            self._render_explosion_effect(surface)
            return

        surface.fill("black")
        self.mapa.render(surface)

        for i, personapa in enumerate(self.personapas):
            if not personapa.is_alive:
                continue
            self._sprite_renderer.render(
                surface, personapa, self._personapa_anim_time[i], visual_scale=PERSONAPA_VISUAL_SCALE
            )
            #if personapa.is_hot_potato:
                #pygame.draw.circle(
                    #surface, "yellow", personapa.get_rect().center,
                    #personapa.size // 2 + 6, width=3,
                #)

        # Dibujar la barra superior e interfaz
        self._render_hud(surface)

        # El conteo regresivo inicial se dibuja al final de todo
        if self.in_countdown:
            numero = str(int(self.countdown_time_left) + 1)
            texto = self._font.render(numero, True, "white")
            rect = texto.get_rect(center=surface.get_rect().center)
            surface.blit(texto, rect)

    def _render_explosion_effect(self, surface: pygame.Surface) -> None:
        # dibuja el mundo normal (mapa + personapas vivas) en una
        # superficie aparte, para poder aplicarle el temblor de pantalla
        # sin tocar el resto del código de dibujo
        temp = pygame.Surface(surface.get_size())
        temp.fill("black")
        self.mapa.render(temp)

        for i, personapa in enumerate(self.personapas):
            if personapa.is_alive:
                self._sprite_renderer.render(
                    temp, personapa, self._personapa_anim_time[i], visual_scale=PERSONAPA_VISUAL_SCALE
                )

        if self.explosion_particles:
            for p in self.explosion_particles:
                p.render(temp)

        shake_x, shake_y = 0, 0
        if self.screen_shake_timer > 0:
            shake_x = random.uniform(-EXPLOSION_SHAKE_MAGNITUDE, EXPLOSION_SHAKE_MAGNITUDE)
            shake_y = random.uniform(-EXPLOSION_SHAKE_MAGNITUDE, EXPLOSION_SHAKE_MAGNITUDE)

        surface.fill("black")
        surface.blit(temp, (shake_x, shake_y))

        # el círculo negro va creciendo hasta tapar toda la pantalla
        if self.blackout_center is not None and self.blackout_progress > 0:
            max_radius = math.hypot(surface.get_width(), surface.get_height())
            radius = int(self.blackout_progress * max_radius)
            pygame.draw.circle(surface, "black", self.blackout_center, radius)