"""ScoreState: estado de puntuación después de una ronda."""
import math

import pygame
from gale.state import BaseState
from gale.timer import Timer

from src.objects.podio import Podio
from src.objects.personapa_sprite_renderer import PersonapaSpriteRenderer
from src.objects.transitions import FadeInOut

import settings

VIRTUAL_W = getattr(settings, "VIRTUAL_WIDTH", None) or settings.WINDOW_WIDTH
VIRTUAL_H = getattr(settings, "VIRTUAL_HEIGHT", None) or settings.WINDOW_HEIGHT

# Botones al final de la pantalla (mismo estilo que MenuState/WinState)
OUTLINE_COLOR = (20, 20, 30)
BUTTON_FILL_IDLE = (255, 255, 255)
BUTTON_FILL_SELECTED = (255, 221, 0)
BUTTON_TEXT_IDLE = (44, 108, 191)
BUTTON_TEXT_SELECTED = (20, 20, 30)
BUTTON_W, BUTTON_H, BUTTON_GAP = 250, 46, 20
BUTTON_CENTER_Y = VIRTUAL_H - 38
INPUT_UNLOCK_DELAY = 1.8  # segundos antes de aceptar input (evita saltarse la pantalla sin querer)

class ScoreState(BaseState):
    def enter(self, **kwargs) -> None:
        self.play_state = kwargs["play_state"]
        self.death_log = kwargs["death_log"]
        self.personapas = kwargs["personapas"]

        self.play_state.rounds += 1

        self.renderer = PersonapaSpriteRenderer()
        self.anim_time = 0.0

        # 1. Configurar podios
        self.podios = []
        screen_w, screen_h = VIRTUAL_W, VIRTUAL_H
        ancho_podio = 80
        espacio = 60
        total_w = (ancho_podio * len(self.personapas)) + (espacio * (len(self.personapas) - 1))
        start_x = (screen_w - total_w) // 2

        colores = [(245, 60, 60), (100, 255, 100), (60, 150, 255), (255, 175, 55)]
        self.colores = colores

        for i in range(len(self.personapas)):
            puntos = self.play_state.scores[i]
            #la altura es inicialmente minima, pero La barra crece en el tween según los puntos
            podio = Podio({
                "x": start_x + (ancho_podio + espacio) * i,
                "y": screen_h - 130, # Espacio extra abajo para los números
                "width": ancho_podio,
                "height": 5,
                "color": colores[i % len(colores)]
            })
            self.podios.append(podio)

        
        # 2. empezar tween de los podios
        self.tween_podio_heights(True)
        
        # 3. Actualizar puntajes
        for i, survived in enumerate(self.death_log):

            if survived:
                self.play_state.scores[i] += 1

        # 4. Fuentes estilo UI
        try:
            self.font = pygame.font.Font("assets/fonts/Hansief.otf", 40)
            self.sub_font = pygame.font.Font("assets/fonts/Hansief.otf", 28)
        except:
            self.font = pygame.font.SysFont(None, 40)
            self.sub_font = pygame.font.SysFont(None, 28)

        # Fondo de franjas diagonales, igual estilo que MenuState. Se genera
        # en el primer render() usando el tamaño REAL de la superficie que
        # se recibe ahí (no pygame.display.get_surface(), que puede diferir
        # de la superficie virtual interna del framework y dejar franjas
        # más chicas que la pantalla real -> franjas negras en los bordes).
        self.stripes_surface = None

        self.transition = None
        self.is_transitioning = False

        # La pantalla se queda hasta que un jugador elija un botón.
        # Opción 0 (izquierda): volver al menú principal
        # Opción 1 (derecha): siguiente ronda (o ver ganador si ya terminaron las rondas)
        self.selected_index = 1  # por defecto queda seleccionado "siguiente ronda"
        self.pending_action = None
        self.options = [
            "MENÚ PRINCIPAL",
            "VER GANADOR" if self.play_state.are_rounds_over() else "SIGUIENTE RONDA",
        ]
        self.button_labels = {}
        for i, text in enumerate(self.options):
            self.button_labels[(i, False)] = self.sub_font.render(text, True, BUTTON_TEXT_IDLE)
            self.button_labels[(i, True)] = self.sub_font.render(text, True, BUTTON_TEXT_SELECTED)

        try:
            self.hover_sound = pygame.mixer.Sound(settings.SOUNDS["hover"])
            self.hover_sound.set_volume(0.1)
            self.click_sound = pygame.mixer.Sound(settings.SOUNDS["click"])
            self.click_sound.set_volume(0.1)
        except Exception:
            self.hover_sound = self.click_sound = None

    def tween_podio_heights(self, repeat: bool):
        altura = 40
        to_tween = []

        for i in range(len(self.personapas)):
            puntos = self.play_state.scores[i]
            pair = (self.podios[i],{"height":(puntos + 0.5)*altura})
            to_tween.append(pair)

        o_f = lambda: self.tween_podio_heights(False) if repeat else None

        Timer.tween(
            1,
            to_tween,
            ease_function_name="out_cubic",
            on_finish= o_f,
        )

    @property
    def inputs_enabled(self) -> bool:
        return (not self.is_transitioning) and self.anim_time >= INPUT_UNLOCK_DELAY

    def on_input(self, input_id, input_data) -> None:
        if not getattr(input_data, "pressed", False) or not self.inputs_enabled:
            return

        # Cualquier jugador puede navegar y confirmar (igual que en WinState)
        if input_id.endswith(("_up", "_left")):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            if self.hover_sound:
                self.hover_sound.play()
        elif input_id.endswith(("_down", "_right")):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            if self.hover_sound:
                self.hover_sound.play()
        elif input_id.endswith("_main"):
            if self.click_sound:
                self.click_sound.play()
            self.pending_action = "menu" if self.selected_index == 0 else "next"
            self._start_transition()

    def _start_transition(self):
        self.is_transitioning = True
        self.transition = FadeInOut(duration=1.0, color=(20, 22, 32), fade_out=True, on_finish=self._on_transition_finish)

    def _generate_diagonal_stripes(self, width: int, height: int) -> pygame.Surface:
        """Mismo estilo de franjas diagonales azules que MenuState
        (src/states/menu_state.py::_generate_diagonal_stripes), pero
        duplicado aquí para no depender de instanciar MenuState."""
        stripe_color_a = (58, 134, 222)
        stripe_color_b = (44, 108, 191)

        surface = pygame.Surface((width, height))
        band_width = 46

        step = band_width
        start = -height
        end = width + height

        surface.fill(stripe_color_a)
        toggle = False
        for x in range(start, end, step):
            color = stripe_color_b if toggle else stripe_color_a
            pygame.draw.line(
                surface, color,
                (x, 0), (x - height, height),
                band_width,
            )
            toggle = not toggle

        return surface

    def _get_leader(self):
        """Devuelve (texto, color) del jugador que va ganando.
        Si hay empate en el primer lugar, devuelve 'Empate' en blanco."""
        scores = self.play_state.scores[:len(self.personapas)]
        best = max(scores)
        leaders = [i for i, p in enumerate(scores) if p == best]
        if len(leaders) == 1:
            i = leaders[0]
            return f"Jugador {i + 1}", self.colores[i % len(self.colores)]
        return "Empate", (245, 245, 245)

    def _render_buttons(self, surface: pygame.Surface) -> None:
        total_w = BUTTON_W * len(self.options) + BUTTON_GAP * (len(self.options) - 1)
        start_x = (VIRTUAL_W - total_w) // 2

        for i in range(len(self.options)):
            is_selected = i == self.selected_index
            bounce = math.sin(self.anim_time * 6) * 3 if is_selected else 0

            rect = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
            rect.center = (start_x + BUTTON_W // 2 + i * (BUTTON_W + BUTTON_GAP),
                           BUTTON_CENTER_Y + bounce)

            shadow = rect.copy()
            shadow.y += 5
            pygame.draw.rect(surface, (10, 10, 15), shadow, border_radius=16)

            fill = BUTTON_FILL_SELECTED if is_selected else BUTTON_FILL_IDLE
            pygame.draw.rect(surface, fill, rect, border_radius=16)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect, width=4, border_radius=16)

            label = self.button_labels[(i, is_selected)]
            surface.blit(label, label.get_rect(center=rect.center))

    def _render_header(self, surface: pygame.Surface) -> None:
        """Textos de arriba, mismo estilo que 'Selecciona tu Sombrero'
        (Hansief, blanco, centrados) en la parte superior."""
        cx = VIRTUAL_W // 2

        title = self.font.render("Puntuaciones", True, "white")
        surface.blit(title, title.get_rect(center=(cx, 40)))

        ronda = f"Ronda {self.play_state.rounds} de {self.play_state.max_rounds}"
        ronda_surf = self.sub_font.render(ronda, True, "white")
        surface.blit(ronda_surf, ronda_surf.get_rect(center=(cx, 80)))

        nombre, color = self._get_leader()
        prefijo = self.sub_font.render("Va ganando: ", True, "white")
        nombre_surf = self.sub_font.render(nombre, True, color)
        total_w = prefijo.get_width() + nombre_surf.get_width()
        x = cx - total_w // 2
        y = 115
        surface.blit(prefijo, prefijo.get_rect(midleft=(x, y)))
        surface.blit(nombre_surf, nombre_surf.get_rect(midleft=(x + prefijo.get_width(), y)))

    def _on_transition_finish(self):
        if self.pending_action == "menu":
            self.play_state.return_to_menu()
            return

        winner_index = self.play_state.check_winner()
        if winner_index != -1:
            # OJO: self.state_machine NO es la maquina del juego, es la
            # substate_machine de PlayState (es quien instancio a este
            # subestado). WinState vive en la maquina de ARRIBA, la de
            # src/game.py, que es justamente play_state.state_machine.
            self.play_state.state_machine.change(
                "win",
                play_state=self.play_state,
                winner_index=winner_index,
                personapas=self.personapas,
            )
        else:
            # Siguiente ronda
            self.play_state.substate_machine.change("parkour", play_state=self.play_state, personapas=self.personapas)

    def update(self, dt: float) -> None:
        self.anim_time += dt

    def render(self, surface: pygame.Surface) -> None:
        if self.stripes_surface is None or self.stripes_surface.get_size() != surface.get_size():
            self.stripes_surface = self._generate_diagonal_stripes(*surface.get_size())

        surface.blit(self.stripes_surface, (0, 0))  # Fondo de franjas, estilo del menú

        for i, podio in enumerate(self.podios):
            # Dibujar el podio (barra)
            podio.render(surface)

            # Dibujar el texto de los puntos JUSTO DEBAJO del podio
            puntos_str = f"{self.play_state.scores[i]} pts"
            text_surf = self.font.render(puntos_str, True, (245, 245, 245))
            text_rect = text_surf.get_rect(center=(podio.x + podio.width // 2, podio.y + 30))
            surface.blit(text_surf, text_rect)

            # Dibujar la Personapa (y su sombrero) ARRIBA de la barra
            personapa = self.personapas[i]
            
            # Truco: Temporalmente movemos la posición del personapa a la cima del podio para renderizar
            pos_original = personapa.position.copy()
            # Apoyamos la parte baja de la personapa en la parte superior del podio (podio.y - podio.height)
            personapa.position = pygame.Vector2(
                podio.x + (podio.width // 2) - (personapa.size // 2),
                podio.y - podio.height - personapa.size + 15
            )
            # Forzamos que miren hacia el frente 
            personapa.move_intent = pygame.Vector2(0, 0)
            personapa.facing_direction = pygame.Vector2(0, 1)

            # Usamos el renderer para que dibuje el sprite animado y el sombrero encima
            self.renderer.render(surface, personapa, self.anim_time, visual_scale=1.5)

            # Restauramos la posición original
            personapa.position = pos_original

        self._render_header(surface)

        if self.anim_time >= INPUT_UNLOCK_DELAY:
            self._render_buttons(surface)

        # Si está transicionando, pintar encima el Fade
        if self.is_transitioning and self.transition:
            self.transition.render(surface)