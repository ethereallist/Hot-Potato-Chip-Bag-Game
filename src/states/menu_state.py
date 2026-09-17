"""MenuState: menú principal con estilo tipo Fall Guys — franjas
diagonales de colores saturados, texto grueso con contorno, y botones
redondeados con borde marcado."""

import math
import random

import pygame

from gale.state import BaseState

from src.objects.personapa import Personapa

import settings


OPTIONS = ["JUGAR", "SALIR"]

# Paleta tipo Fall Guys: azul vibrante de fondo, franjas alternadas,
# amarillo para resaltar lo seleccionado
STRIPE_COLOR_A = (58, 134, 222)
STRIPE_COLOR_B = (44, 108, 191)
OUTLINE_COLOR = (20, 20, 30)
TITLE_COLOR = (255, 221, 0)
BUTTON_FILL_IDLE = (255, 255, 255)
BUTTON_FILL_SELECTED = (255, 221, 0)
BUTTON_TEXT_IDLE = (44, 108, 191)
BUTTON_TEXT_SELECTED = (20, 20, 30)

TITLE_FONT_PATH = "assets/fonts/Bloom-Regular.otf"
BUTTON_FONT_PATH = "assets/fonts/Hansief.otf"

MENU_PERSONAPA_COUNT = 4
MENU_PERSONAPA_MARGIN = 30       # no se acercan a menos de esto del borde
MENU_PERSONAPA_SPEED = 90        # más lento que en el juego real, para que se vea "de fondo"
DIRECTION_CHANGE_RANGE = (1.5, 3.5)  # segundos entre cambios de rumbo al azar


class MenuState(BaseState):
    def enter(self, **kwargs) -> None:
        self.width = getattr(settings, "WINDOW_WIDTH", 800)
        self.height = getattr(settings, "WINDOW_HEIGHT", 600)

        self.stripes_surface = self._generate_diagonal_stripes()

        pygame.font.init()
        self._title_font = self._load_font(TITLE_FONT_PATH, 46)
        self._button_font = self._load_font(BUTTON_FONT_PATH, 36)

        self.selected_index = 0
        self._time = 0.0

        self._init_menu_personapas()

    def _init_menu_personapas(self) -> None:
        """4 Personapas de adorno en el fondo del menú: IA simple que
        camina en una dirección, cambia de rumbo cada rato, rebota en
        el margen del borde, y se empuja con las demás si chocan."""
        self.menu_personapas: list[Personapa] = []
        self._menu_personapa_timers: list[float] = []

        margin = MENU_PERSONAPA_MARGIN
        for _ in range(MENU_PERSONAPA_COUNT):
            p = Personapa()
            p.max_speed = MENU_PERSONAPA_SPEED
            p.position = pygame.Vector2(
                random.uniform(margin, self.width - margin - p.size),
                random.uniform(margin, self.height - margin - p.size),
            )
            p.move_intent = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))

            self.menu_personapas.append(p)
            self._menu_personapa_timers.append(random.uniform(*DIRECTION_CHANGE_RANGE))

    def _update_menu_personapas(self, dt: float) -> None:
        margin = MENU_PERSONAPA_MARGIN

        for i, p in enumerate(self.menu_personapas):
            # cambia de rumbo al azar cada cierto tiempo, para que no
            # caminen en línea recta todo el rato
            self._menu_personapa_timers[i] -= dt
            if self._menu_personapa_timers[i] <= 0:
                self._menu_personapa_timers[i] = random.uniform(*DIRECTION_CHANGE_RANGE)
                p.move_intent = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))

            p.move(dt)

            # rebote al llegar al margen del borde de la ventana
            min_x, max_x = margin, self.width - margin - p.size
            min_y, max_y = margin, self.height - margin - p.size

            if p.position.x < min_x:
                p.position.x = min_x
                p.move_intent.x = abs(p.move_intent.x)
            elif p.position.x > max_x:
                p.position.x = max_x
                p.move_intent.x = -abs(p.move_intent.x)

            if p.position.y < min_y:
                p.position.y = min_y
                p.move_intent.y = abs(p.move_intent.y)
            elif p.position.y > max_y:
                p.position.y = max_y
                p.move_intent.y = -abs(p.move_intent.y)

        # colisión entre ellas mismas, reutilizando lo que ya existe en Personapa
        for i, a in enumerate(self.menu_personapas):
            for b in self.menu_personapas[i + 1:]:
                a.handle_collision(b)
                b.handle_collision(a)

    def _load_font(self, font_path: str, size: int) -> pygame.font.Font:
        if font_path:
            try:
                return pygame.font.Font(font_path, size)
            except FileNotFoundError:
                pass
        fallback_path = pygame.font.match_font(
            "phosphate,arialrounded,arialblack,verdana-bold"
        )
        return pygame.font.Font(fallback_path, size)

    def _generate_diagonal_stripes(self) -> pygame.Surface:
        """Franjas diagonales de dos colores, cubriendo TODO el fondo
        (patrón sólido, estilo Fall Guys) — no líneas finas sobre foto."""
        surface = pygame.Surface((self.width, self.height))
        band_width = 46

        step = band_width
        start = -self.height
        end = self.width + self.height

        surface.fill(STRIPE_COLOR_A)
        toggle = False
        for x in range(start, end, step):
            color = STRIPE_COLOR_B if toggle else STRIPE_COLOR_A
            pygame.draw.line(
                surface, color,
                (x, 0), (x - self.height, self.height),
                band_width,
            )
            toggle = not toggle

        return surface

    def _render_outlined_text(self, font, text, color, outline_width=3, letter_spacing=0) -> pygame.Surface:
        if letter_spacing == 0:
            # camino simple, sin separación extra (como antes)
            base = font.render(text, True, color)
            padding = outline_width * 2
            combined = pygame.Surface(
                (base.get_width() + padding * 2, base.get_height() + padding * 2),
                pygame.SRCALPHA,
            )
            outline = font.render(text, True, OUTLINE_COLOR)
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    combined.blit(outline, (padding + dx, padding + dy))
            combined.blit(base, (padding, padding))
            return combined

        # con letter_spacing: se renderiza carácter por carácter y se
        # van pegando uno junto al otro con el espacio extra en medio
        char_surfaces = []
        total_width = 0
        max_height = 0
        for ch in text:
            char_base = font.render(ch, True, color)
            char_outline = font.render(ch, True, OUTLINE_COLOR)
            char_surfaces.append((char_base, char_outline))
            total_width += char_base.get_width() + letter_spacing
            max_height = max(max_height, char_base.get_height())
        total_width -= letter_spacing  # no agregar espacio después de la última letra

        padding = outline_width * 2
        combined = pygame.Surface(
            (total_width + padding * 2, max_height + padding * 2),
            pygame.SRCALPHA,
        )

        x = padding
        for char_base, char_outline in char_surfaces:
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx == 0 and dy == 0:
                        continue
                    combined.blit(char_outline, (x + dx, padding + dy))
            combined.blit(char_base, (x, padding))
            x += char_base.get_width() + letter_spacing

        return combined

    def update(self, dt: float) -> None:
        self._time += dt
        self._update_menu_personapas(dt)

    def on_input(self, input_id, input_data) -> None:
        if not getattr(input_data, "pressed", False):
            return

        if input_id == "p1_up":
            self.selected_index = (self.selected_index - 1) % len(OPTIONS)
        elif input_id == "p1_down":
            self.selected_index = (self.selected_index + 1) % len(OPTIONS)
        elif input_id == "p1_main":
            self._confirm_selection()

    def _confirm_selection(self) -> None:
        selected = OPTIONS[self.selected_index]
        if selected == "JUGAR":
            self.state_machine.change("play")
        elif selected == "SALIR":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.stripes_surface, (0, 0))

        for p in self.menu_personapas:
            p.render(surface)

        title = self._render_outlined_text(self._title_font, "HOT POTATO CHIP BAG", TITLE_COLOR)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3 - 20))
        surface.blit(title, title_rect)

        button_width, button_height = 260, 70
        spacing = 24
        start_y = self.height // 3 + 90

        for i, option in enumerate(OPTIONS):
            is_selected = i == self.selected_index

            # rebotecito sutil en el botón seleccionado, para que se
            # sienta vivo/energético (como los menús de Fall Guys)
            bounce = math.sin(self._time * 6) * 4 if is_selected else 0

            fill = BUTTON_FILL_SELECTED if is_selected else BUTTON_FILL_IDLE
            text_color = BUTTON_TEXT_SELECTED if is_selected else BUTTON_TEXT_IDLE

            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (self.width // 2, start_y + i * (button_height + spacing) + bounce)

            # sombra del botón
            shadow_rect = rect.copy()
            shadow_rect.y += 6
            pygame.draw.rect(surface, (20, 20, 30, 120), shadow_rect, border_radius=18)

            pygame.draw.rect(surface, fill, rect, border_radius=18)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect, width=4, border_radius=18)

            label = self._render_outlined_text(
                self._button_font, option, text_color, outline_width=2, letter_spacing=4
            )
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)