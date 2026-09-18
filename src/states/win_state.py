"""WinState: pantalla final que muestra al jugador ganador con su
puntuación, el sombrero con el que ganó, y dos botones para volver a
jugar o regresar al menú.

OJO con la máquina de estados: este estado vive en la máquina de ARRIBA
(la de src/game.py: "menu" / "play" / "win"), NO dentro de los subestados
de PlayState. Por eso aquí `self.state_machine` sí conoce "menu" y "play",
y los botones pueden cambiar de estado sin reventar.
"""

import math

import pygame

from gale.state import BaseState

import settings
from src.objects.confetti import ConfettiRain
from src.objects.personapa_sprite_renderer import PersonapaSpriteRenderer
from src.objects.transitions import FadeInOut


# Misma paleta que MenuState, para que todo se vea de la misma familia.
# BG_COLOR ya no es el fondo de la pantalla (ahora son las franjas), pero
# sigue siendo el color de los fundidos, igual que en ScoreState.
BG_COLOR = (20, 22, 32)
STRIPE_COLOR_A = (58, 134, 222)
STRIPE_COLOR_B = (44, 108, 191)
STRIPE_BAND_WIDTH = 46
TITLE_COLOR = (255, 221, 0)
OUTLINE_COLOR = (20, 20, 30)
BUTTON_FILL_IDLE = (255, 255, 255)
BUTTON_FILL_SELECTED = (255, 221, 0)
BUTTON_TEXT_IDLE = (44, 108, 191)
BUTTON_TEXT_SELECTED = (20, 20, 30)

OPTIONS = ["VOLVER A JUGAR", "IR AL MENÚ"]

# Frases que se turnan debajo del puntaje (en orden, en bucle).
WIN_PHRASES = [
    "¡El papa de los helaos!",
    "¡Te los papeaste!",
    "¿Papa? ¿Papá?",
    "¡Papote!",
    "Papa-pa.. ¿Pa esto juegan?",
]
PHRASE_HOLD = 2.4      # segundos que se queda una frase a plena opacidad
PHRASE_FADE = 0.4      # segundos de aparición y de desvanecimiento
PHRASE_SLIDE = 8       # px que sube la frase mientras aparece

# Confeti: papelitos por segundo, y cuántos ya vienen "en camino" al entrar.
CONFETTI_RATE = 40.0
CONFETTI_PREFILL = 70
CONFETTI_PREFILL_DEPTH = 260

# Qué tan rápido se "enciende"/"apaga" el resaltado de un botón
# (mayor = más rápido). Ver _update_button_highlights.
BUTTON_HIGHLIGHT_SPEED = 14.0
LABEL_COLOR_STEPS = 16  # pasos de color cacheados para las etiquetas

FADE_IN_DURATION = 0.8
FADE_OUT_DURATION = 0.7

# Los botones (caja clara con texto oscuro) se desvanecen con su propia
# curva, más "adelantada" que la del resto de la pantalla. Con el fundido
# lineal normal, el texto oscuro se confundía con el fondo antes que la
# caja clara, y se veía un rectángulo vacío flotando al final. Así la
# caja ya se fue (o todavía no llega) cuando el texto sería ilegible.
BUTTON_EXIT_SPAN = 0.6     # los botones terminan de irse al 60% del fundido de salida
BUTTON_ENTER_DELAY = 0.3   # y empiezan a aparecer al 30% del fundido de entrada
BUTTON_PAD = 24            # margen del lienzo temporal (sombra + rebote)

# No se aceptan inputs hasta que termine el fundido de entrada, para que
# nadie se salte la pantalla de ganador por venir machacando el botón de
# dash desde la ronda anterior.
INPUT_UNLOCK_DELAY = FADE_IN_DURATION + 0.15


class WinState(BaseState):
    def enter(self, **kwargs) -> None:
        self.play_state = kwargs["play_state"]
        self.winner_index = kwargs["winner_index"]
        self.personapas = kwargs["personapas"]

        self.winner_personapa = self.personapas[self.winner_index]
        self.winner_score = self.play_state.scores[self.winner_index]

        self.renderer = PersonapaSpriteRenderer()
        self.anim_time = 0.0

        # Fondo de franjas diagonales, igual que MenuState/ScoreState. Se
        # genera en el primer render() con el tamaño REAL de la superficie
        # que llega ahí (mismo criterio que ScoreState).
        self.stripes_surface = None

        self.selected_index = 0
        self.leaving = False          # ya se eligió una opción, ignorar inputs
        self.pending_action = None    # "play" | "menu"

        # Tamaños de fuente pensados para una ventana de 700x500 (ver
        # settings.WINDOW_WIDTH/HEIGHT). El título original a 96pt medía
        # 828px de ancho -- más ancho que toda la pantalla -- por eso no
        # se veía: se salía por ambos lados. Con 44pt entra completo.
        self.font_title = self._load_font(44)
        self.font_score = self._load_font(26)
        self.font_phrase = self._load_font(24)
        self.font_button = self._load_font(26)

        # Resaltado de cada botón, de 0.0 (reposo) a 1.0 (seleccionado).
        # Se mueve suavemente hacia su objetivo en update(). Antes el
        # botón seleccionado pasaba de blanco a amarillo (y empezaba a
        # rebotar) de golpe en cuanto se desbloqueaban los inputs, y
        # volvía a blanco de golpe al confirmar: ese rectángulo amarillo
        # que aparecía/desaparecía "de un tirón" era el salto que se veía
        # al entrar y al salir de esta pantalla. Ahora el seleccionado
        # nace ya amarillo (así entra con el fundido, como todo lo demás)
        # y sigue amarillo mientras se hace el fundido de salida.
        self.button_highlight = [
            1.0 if i == self.selected_index else 0.0 for i in range(len(OPTIONS))
        ]
        self._label_cache = {}

        # Frases rotativas: se prerenderizan (con sombra) una sola vez.
        self._phrase_surfaces = [self._build_phrase_surface(p) for p in WIN_PHRASES]
        self.phrase_index = 0
        self.phrase_time = 0.0

        # Confeti cayendo desde arriba
        self.confetti = ConfettiRain(
            settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, rate=CONFETTI_RATE
        )
        self.confetti.prefill(CONFETTI_PREFILL, CONFETTI_PREFILL_DEPTH)

        # Transición de entrada: aparece desde negro
        self.transition = FadeInOut(
            duration=FADE_IN_DURATION, color=BG_COLOR, fade_out=False
        )

    @staticmethod
    def _load_font(size: int) -> pygame.font.Font:
        try:
            return pygame.font.Font("assets/fonts/Hansief.otf", size)
        except (FileNotFoundError, pygame.error):
            return pygame.font.SysFont(None, size)

    def _build_phrase_surface(self, text: str) -> pygame.Surface:
        """Frase + sombra en UNA sola superficie con alpha, para poder
        desvanecerla entera con un único set_alpha()."""
        text_surf = self.font_phrase.render(text, True, TITLE_COLOR)
        shadow_surf = self.font_phrase.render(text, True, (10, 10, 15))
        surf = pygame.Surface(
            (text_surf.get_width() + 3, text_surf.get_height() + 3), pygame.SRCALPHA
        )
        surf.blit(shadow_surf, (2, 2))
        surf.blit(text_surf, (0, 0))
        return surf

    @staticmethod
    def _lerp_color(a: tuple, b: tuple, t: float) -> tuple:
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def _get_label(self, option: str, highlight: float) -> pygame.Surface:
        """Etiqueta del botón con el color intermedio entre reposo y
        seleccionado. Se cachea por pasos para no renderizar texto nuevo
        en cada frame."""
        step = round(highlight * LABEL_COLOR_STEPS)
        key = (option, step)
        if key not in self._label_cache:
            color = self._lerp_color(
                BUTTON_TEXT_IDLE, BUTTON_TEXT_SELECTED, step / LABEL_COLOR_STEPS
            )
            self._label_cache[key] = self.font_button.render(option, True, color)
        return self._label_cache[key]

    # --- Entrada ---

    @property
    def inputs_enabled(self) -> bool:
        return not self.leaving and self.anim_time >= INPUT_UNLOCK_DELAY

    def on_input(self, input_id, input_data) -> None:
        if not getattr(input_data, "pressed", False):
            return
        if not self.inputs_enabled:
            return

        # Cualquier jugador puede navegar y confirmar aquí (se "pasa el
        # control"), igual que en la selección de sombreros del menú.
        if input_id.endswith(("_up", "_left")):
            self.selected_index = (self.selected_index - 1) % len(OPTIONS)
        elif input_id.endswith(("_down", "_right")):
            self.selected_index = (self.selected_index + 1) % len(OPTIONS)
        elif input_id.endswith("_main"):
            self._confirm_selection()

    def _confirm_selection(self) -> None:
        self.leaving = True
        self.pending_action = "play" if self.selected_index == 0 else "menu"
        self.transition = FadeInOut(
            duration=FADE_OUT_DURATION,
            color=BG_COLOR,
            fade_out=True,
            on_finish=self._go_to_pending_state,
        )

    def _go_to_pending_state(self) -> None:
        if self.pending_action == "play":
            # Revancha: PlayState.enter reinicia rondas y puntajes, y
            # ParkourState revive y reubica a todas las personapas, así
            # que se reutilizan tal cual (conservan su sombrero).
            self.state_machine.change(
                "play",
                player_count=self.play_state.player_count,
                personapas=self.personapas,
            )
        else:
            self.state_machine.change("menu")

    # --- Loop ---

    def update(self, dt: float) -> None:
        self.anim_time += dt
        self._update_button_highlights(dt)
        self._update_phrase(dt)
        self.confetti.emit(dt)
        self.confetti.update(dt)

    def _update_button_highlights(self, dt: float) -> None:
        # Suavizado exponencial: cada frame se acerca una fracción de lo
        # que falta, sin importar los FPS (por eso depende de dt).
        blend = min(1.0, dt * BUTTON_HIGHLIGHT_SPEED)
        for i in range(len(self.button_highlight)):
            target = 1.0 if i == self.selected_index else 0.0
            self.button_highlight[i] += (target - self.button_highlight[i]) * blend

    def _update_phrase(self, dt: float) -> None:
        self.phrase_time += dt
        cycle = PHRASE_HOLD + 2 * PHRASE_FADE
        while self.phrase_time >= cycle:
            self.phrase_time -= cycle
            self.phrase_index = (self.phrase_index + 1) % len(WIN_PHRASES)

    @staticmethod
    def _generate_diagonal_stripes(width: int, height: int) -> pygame.Surface:
        """Mismas franjas que MenuState y ScoreState (duplicado aquí para
        no depender de instanciar ninguno de los dos)."""
        surface = pygame.Surface((width, height))
        surface.fill(STRIPE_COLOR_A)

        toggle = False
        for x in range(-height, width + height, STRIPE_BAND_WIDTH):
            color = STRIPE_COLOR_B if toggle else STRIPE_COLOR_A
            pygame.draw.line(
                surface, color,
                (x, 0), (x - height, height),
                STRIPE_BAND_WIDTH,
            )
            toggle = not toggle

        return surface

    def render(self, surface: pygame.Surface) -> None:
        screen_w, screen_h = surface.get_size()

        if self.stripes_surface is None or self.stripes_surface.get_size() != surface.get_size():
            self.stripes_surface = self._generate_diagonal_stripes(screen_w, screen_h)
        surface.blit(self.stripes_surface, (0, 0))

        self._render_title(surface, screen_w)
        self._render_winner(surface, screen_w, screen_h)
        self._render_texts(surface, screen_w)
        # El confeti va delante del título/ganador/textos, pero DETRÁS de
        # los botones para no tapar lo que se puede presionar.
        self.confetti.render(surface)
        self._render_buttons(surface, screen_w, screen_h)

        # Fundido (de entrada o de salida), encima de todo
        if not self.transition.finished:
            self.transition.render(surface)

    def _render_title(self, surface: pygame.Surface, screen_w: int) -> None:
        title_text = "¡TENEMOS GANADOR!"
        title_surf = self.font_title.render(title_text, True, TITLE_COLOR)
        title_rect = title_surf.get_rect(center=(screen_w // 2, 58))

        shadow_surf = self.font_title.render(title_text, True, (10, 10, 15))
        surface.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title_surf, title_rect)

    def _render_winner(self, surface: pygame.Surface, screen_w: int, screen_h: int) -> None:
        # La personapa se dibuja a partir de su position, así que la
        # movemos al centro solo para este frame y la devolvemos a donde
        # estaba, para no ensuciar su estado real.
        pos_original = self.winner_personapa.position.copy()

        bob = math.sin(self.anim_time * 3) * 4  # flotadita de campeón

        self.winner_personapa.move_intent = pygame.Vector2(0, 0)
        self.winner_personapa.facing_direction = pygame.Vector2(0, 1)
        self.winner_personapa.position = pygame.Vector2(
            (screen_w // 2) - (self.winner_personapa.size // 2),
            170 - (self.winner_personapa.size // 2) + bob,
        )

        self.renderer.render(surface, self.winner_personapa, self.anim_time, visual_scale=2.2)

        self.winner_personapa.position = pos_original

    def _render_texts(self, surface: pygame.Surface, screen_w: int) -> None:
        puntos = "punto" if self.winner_score == 1 else "puntos"
        score_text = f"El Jugador {self.winner_index + 1} arrasó con {self.winner_score} {puntos}"
        score_surf = self.font_score.render(score_text, True, (245, 245, 245))
        surface.blit(score_surf, score_surf.get_rect(center=(screen_w // 2, 268)))

        self._render_phrase(surface, screen_w)

    def _render_phrase(self, surface: pygame.Surface, screen_w: int) -> None:
        # Cada frase aparece (sube un poquito mientras se vuelve opaca),
        # se sostiene, y se desvanece antes de dar paso a la siguiente.
        cycle = PHRASE_HOLD + 2 * PHRASE_FADE
        fade = min(1.0, self.phrase_time / PHRASE_FADE, (cycle - self.phrase_time) / PHRASE_FADE)
        fade = max(0.0, fade)
        if fade <= 0.0:
            return

        phrase = self._phrase_surfaces[self.phrase_index]
        phrase.set_alpha(int(fade * 255))
        rect = phrase.get_rect(center=(screen_w // 2, 302 + int((1.0 - fade) * PHRASE_SLIDE)))
        surface.blit(phrase, rect)

    def _button_opacity(self) -> float:
        """Opacidad propia del grupo de botones (0..1), independiente de
        la del fundido general que se pinta encima de todo."""
        rate = self.transition.rate
        if self.leaving:
            return max(0.0, 1.0 - rate / BUTTON_EXIT_SPAN)
        if not self.transition.finished:
            return min(1.0, max(0.0, (rate - BUTTON_ENTER_DELAY) / (1.0 - BUTTON_ENTER_DELAY)))
        return 1.0

    def _render_buttons(self, surface: pygame.Surface, screen_w: int, screen_h: int) -> None:
        button_width, button_height = 260, 54
        spacing = 14
        first_y = screen_h - 130

        opacity = self._button_opacity()
        if opacity <= 0.0:
            return

        if opacity >= 1.0:
            # Caso normal: directo a la pantalla, sin lienzo intermedio.
            self._draw_buttons(surface, screen_w // 2, first_y, button_width, button_height, spacing)
            return

        # Durante el fundido: los botones se dibujan juntos (caja + texto)
        # en un lienzo con alpha y se pegan con la opacidad del grupo.
        strip_w = button_width + 2 * BUTTON_PAD
        strip_h = 2 * button_height + spacing + 2 * BUTTON_PAD
        strip = pygame.Surface((strip_w, strip_h), pygame.SRCALPHA)
        self._draw_buttons(
            strip, strip_w // 2, BUTTON_PAD + button_height // 2,
            button_width, button_height, spacing,
        )
        strip.set_alpha(int(opacity * 255))
        surface.blit(strip, (screen_w // 2 - strip_w // 2, first_y - button_height // 2 - BUTTON_PAD))

    def _draw_buttons(
        self, target: pygame.Surface, center_x: int, first_center_y: int,
        button_width: int, button_height: int, spacing: int,
    ) -> None:
        for i, option in enumerate(OPTIONS):
            highlight = self.button_highlight[i]
            bounce = math.sin(self.anim_time * 6) * 3 * highlight

            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (
                center_x,
                first_center_y + i * (button_height + spacing) + bounce,
            )

            shadow_rect = rect.copy()
            shadow_rect.y += 5
            pygame.draw.rect(target, (10, 10, 15), shadow_rect, border_radius=16)

            fill = self._lerp_color(BUTTON_FILL_IDLE, BUTTON_FILL_SELECTED, highlight)
            pygame.draw.rect(target, fill, rect, border_radius=16)
            pygame.draw.rect(target, OUTLINE_COLOR, rect, width=4, border_radius=16)

            label = self._get_label(option, highlight)
            target.blit(label, label.get_rect(center=rect.center))