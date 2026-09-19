"""MenuState: menú principal con estilo tipo Fall Guys — franjas
diagonales de colores saturados, texto grueso con contorno, botones
redondeados con borde marcado, Personapas de fondo con IA simple, y un
tween al confirmar "Jugar" que reordena los botones."""

import math
import random

import numpy as np
import pygame

from gale.state import BaseState

from src.objects.personapa import Personapa
from src.objects.sprite_animation import SpriteAnimation
from src.objects.hat_sprites import HatSprites

import settings


OPTIONS = ["JUGAR", "SALIR"]

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
MENU_PERSONAPA_MARGIN = 30
MENU_PERSONAPA_SPEED = 90
DIRECTION_CHANGE_RANGE = (1.5, 3.5)
FREEZE_DURATION = 3.0       # segundos quietos tras chocar
WIGGLE_DURATION = 0.5       # segundos de meneo antes de retomar camino
WIGGLE_AMPLITUDE = 4        # qué tanto se menea, en píxeles
WIGGLE_FREQUENCY = 30       # qué tan rápido menea
MENU_PERSONAPA_VISUAL_SCALE = 2.0  # solo el dibujo; el tamaño de colisión no cambia

BUTTON_TWEEN_DURATION = 0.35  # segundos que tarda la animación
BUTTON_EDGE_MARGIN = 30        # separación de los botones respecto al borde, ya confirmado


class MenuState(BaseState):
    def enter(self, **kwargs) -> None:
        # Cargar música del lobby (settings) con volumen bajo para que no sature
        pygame.mixer.music.load(settings.SOUNDS["lobby"])
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.04)

        # Cargar efectos de sonido de hover y click
        self.hover_sound = pygame.mixer.Sound(settings.SOUNDS["hover"])
        self.hover_sound.set_volume(0.1)
        
        self.click_sound = pygame.mixer.Sound(settings.SOUNDS["click"])
        self.click_sound.set_volume(0.1)

        self.width = getattr(settings, "WINDOW_WIDTH", 800)
        self.height = getattr(settings, "WINDOW_HEIGHT", 600)

        self.stripes_surface = self._generate_diagonal_stripes()

        pygame.font.init()
        self._title_font = self._load_font(TITLE_FONT_PATH, 46)
        self._button_font = self._load_font(BUTTON_FONT_PATH, 36)
        self._hat_title_font = self._load_font(BUTTON_FONT_PATH, 40)
        self._hat_player_font = self._load_font(BUTTON_FONT_PATH, 28)
        self._hat_hint_font = self._load_font(BUTTON_FONT_PATH, 18)

        self.selected_index = 0
        self._time = 0.0

        self._title_surface = self._render_text_with_soft_shadow(
            self._title_font, "HOT POTATO CHIP BAG", TITLE_COLOR
        )
        self._button_label_surfaces = {}
        for option in OPTIONS:
            self._button_label_surfaces[(option, False)] = self._button_font.render(
                option, True, BUTTON_TEXT_IDLE
            )
            self._button_label_surfaces[(option, True)] = self._button_font.render(
                option, True, BUTTON_TEXT_SELECTED
            )

        # "main" -> "confirming" -> "confirm" -> "returning" -> "main"
        self.button_state = "main"
        self.button_tween_t = 0.0  # 0 = layout normal, 1 = layout confirmado

        self.selecting_hats = False
        self.hat_sprites = None
        self.hat_current_player = 0
        self.hat_available_indices: list[int] = []
        self.hat_cursor = 0

        self._init_menu_personapas()

        self._walk_right_animation = SpriteAnimation(
            "assets/sprites/personapa_walk_right.png",
            frame_width=32, frame_height=32, frame_count=6, fps=8,
        )
        self._idle_animation = SpriteAnimation(
            "assets/sprites/personapa_idle.png",
            frame_width=32, frame_height=32, frame_count=7, columns=3, fps=6,
        )
        self._walk_up_animation = SpriteAnimation(
            "assets/sprites/personapa_walk_up.png",
            frame_width=32, frame_height=32, frame_count=4, fps=8,
        )

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

    # --- Personapas de fondo, con IA + freeze/wiggle al chocar ---

    def _init_menu_personapas(self) -> None:
        self.menu_personapas: list[Personapa] = []
        self._menu_personapa_state: list[str] = []        # "moving" | "frozen" | "wiggling"
        self._menu_personapa_state_timer: list[float] = []
        self._menu_personapa_dir_timer: list[float] = []
        self._menu_personapa_anim_time: list[float] = []

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
            self._menu_personapa_state.append("moving")
            self._menu_personapa_state_timer.append(0.0)
            self._menu_personapa_dir_timer.append(random.uniform(*DIRECTION_CHANGE_RANGE))
            self._menu_personapa_anim_time.append(random.uniform(0, 1))

    def _update_menu_personapas(self, dt: float) -> None:
        margin = MENU_PERSONAPA_MARGIN

        for i, p in enumerate(self.menu_personapas):
            state = self._menu_personapa_state[i]

            self._menu_personapa_anim_time[i] += dt

            if state == "moving":
                self._menu_personapa_dir_timer[i] -= dt
                if self._menu_personapa_dir_timer[i] <= 0:
                    self._menu_personapa_dir_timer[i] = random.uniform(*DIRECTION_CHANGE_RANGE)
                    p.move_intent = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))

                p.move(dt)

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

            elif state == "frozen":
                p.move_intent = pygame.Vector2(0, 0)
                p.move(dt)
                self._menu_personapa_state_timer[i] -= dt
                if self._menu_personapa_state_timer[i] <= 0:
                    self._menu_personapa_state[i] = "wiggling"
                    self._menu_personapa_state_timer[i] = WIGGLE_DURATION

            elif state == "wiggling":
                p.move_intent = pygame.Vector2(0, 0)
                p.move(dt)
                self._menu_personapa_state_timer[i] -= dt
                if self._menu_personapa_state_timer[i] <= 0:
                    self._menu_personapa_state[i] = "moving"
                    self._menu_personapa_dir_timer[i] = random.uniform(*DIRECTION_CHANGE_RANGE)
                    p.move_intent = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))

        for i, a in enumerate(self.menu_personapas):
            for j in range(i + 1, len(self.menu_personapas)):
                b = self.menu_personapas[j]
                if not a.collides_with(b):
                    continue

                a.handle_collision(b)
                b.handle_collision(a)

                if self._menu_personapa_state[i] == "moving":
                    self._menu_personapa_state[i] = "frozen"
                    self._menu_personapa_state_timer[i] = FREEZE_DURATION
                if self._menu_personapa_state[j] == "moving":
                    self._menu_personapa_state[j] = "frozen"
                    self._menu_personapa_state_timer[j] = FREEZE_DURATION

    def _render_menu_personapas(self, surface: pygame.Surface, alpha: int = 255) -> None:
        for i, p in enumerate(self.menu_personapas):
            state = self._menu_personapa_state[i]

            offset_x = 0
            if state == "wiggling":
                t = self._menu_personapa_state_timer[i]
                offset_x = math.sin(t * WIGGLE_FREQUENCY) * WIGGLE_AMPLITUDE

            center = (p.get_rect().centerx + offset_x, p.get_rect().centery)

            if state == "moving" and abs(p.move_intent.x) > abs(p.move_intent.y) and abs(p.move_intent.x) > 0.1:
                va_a_la_izquierda = p.move_intent.x < 0
                frame = self._walk_right_animation.get_frame(
                    self._menu_personapa_anim_time[i], flipped=va_a_la_izquierda
                )
            elif state == "moving" and p.move_intent.y < -0.1 and abs(p.move_intent.y) >= abs(p.move_intent.x):
                frame = self._walk_up_animation.get_frame(self._menu_personapa_anim_time[i])
            else:
                va_a_la_izquierda = p.facing_direction.x < 0
                frame = self._idle_animation.get_frame(
                    self._menu_personapa_anim_time[i], flipped=va_a_la_izquierda
                )

            render_size = int(p.size * MENU_PERSONAPA_VISUAL_SCALE)
            frame = pygame.transform.scale(frame, (render_size, render_size))
            frame.set_alpha(alpha)
            rect = frame.get_rect(center=center)
            surface.blit(frame, rect)

            if p.hat_index >= 0 and p.hat_sprites is not None:
                self._render_hat_on_personapa(surface, p, rect)

    def _get_hat_direction_index(self, move_intent: pygame.Vector2) -> tuple:
        if move_intent.length_squared() < 0.01:
            return 0, False

        norm = move_intent.normalize()
        x, y = norm.x, norm.y

        if abs(x) > abs(y):
            if x > 0:
                return 1, True
            else:
                return 1, False
        elif y < -0.1:
            return 2, False
        elif y > 0.1:
            if x < -0.3:
                return 4, False
            elif x > 0.3:
                return 5, False
            else:
                return 0, False
        else:
            return 0, False

    def _render_hat_on_personapa(self, surface: pygame.Surface, personapa: Personapa, character_rect: pygame.Rect) -> None:
        frame_idx, flipped = self._get_hat_direction_index(personapa.move_intent)
        hat_frame = personapa.hat_sprites.get_hat_frame(personapa.hat_index, frame_idx, flipped=flipped)

        if hat_frame is None:
            return

        hat_size = int(48 * MENU_PERSONAPA_VISUAL_SCALE) + 16
        hat_frame = pygame.transform.scale(hat_frame, (hat_size, hat_size))

        overlap = hat_size // 4 + 46
        hat_rect = hat_frame.get_rect()
        hat_rect.centerx = character_rect.centerx
        hat_rect.bottom = character_rect.top + overlap

        surface.blit(hat_frame, hat_rect)

    def _generate_diagonal_stripes(self) -> pygame.Surface:
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

    def _build_text_surface(self, font, text, color, letter_spacing=0) -> pygame.Surface:
        if letter_spacing == 0:
            return font.render(text, True, color)

        char_surfaces = [font.render(ch, True, color) for ch in text]
        total_width = sum(c.get_width() for c in char_surfaces) + letter_spacing * (len(text) - 1)
        max_height = max(c.get_height() for c in char_surfaces)
        combined = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        x = 0
        for c in char_surfaces:
            combined.blit(c, (x, 0))
            x += c.get_width() + letter_spacing
        return combined

    @staticmethod
    def _blur_alpha(alpha: np.ndarray, radius: int) -> np.ndarray:
        kernel_size = radius * 2 + 1
        kernel = np.ones(kernel_size) / kernel_size
        blurred = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=0, arr=alpha)
        blurred = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), axis=1, arr=blurred)
        return blurred

    def _blur_surface(self, surf: pygame.Surface, color, radius: int = 3) -> pygame.Surface:
        alpha = pygame.surfarray.pixels_alpha(surf).astype(np.float32).copy()
        blurred_alpha = np.clip(self._blur_alpha(alpha, radius), 0, 255).astype(np.uint8)

        result = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        rgb = np.zeros((surf.get_width(), surf.get_height(), 3), dtype=np.uint8)
        rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2] = color[0], color[1], color[2]
        pygame.surfarray.blit_array(result, rgb)

        alpha_view = pygame.surfarray.pixels_alpha(result)
        alpha_view[:] = blurred_alpha
        del alpha_view

        return result

    def _render_text_with_soft_shadow(
        self, font, text, color, letter_spacing=0,
        shadow_alpha=130, shadow_offset=(0, 3), blur_radius=3,
    ) -> pygame.Surface:
        base = self._build_text_surface(font, text, color, letter_spacing)
        shadow_raw = self._build_text_surface(font, text, (0, 0, 0, shadow_alpha), letter_spacing)

        pad = blur_radius * 4
        padded_shadow = pygame.Surface(
            (shadow_raw.get_width() + pad * 2, shadow_raw.get_height() + pad * 2), pygame.SRCALPHA
        )
        padded_shadow.blit(shadow_raw, (pad, pad))
        blurred_shadow = self._blur_surface(padded_shadow, (0, 0, 0), radius=blur_radius)

        combined = pygame.Surface(blurred_shadow.get_size(), pygame.SRCALPHA)
        combined.blit(blurred_shadow, shadow_offset)
        combined.blit(base, (pad, pad))
        return combined

    def update(self, dt: float) -> None:
        self._time += dt
        self._update_menu_personapas(dt)
        self._update_button_tween(dt)

    def _update_button_tween(self, dt: float) -> None:
        if self.button_state == "confirming":
            self.button_tween_t = min(1.0, self.button_tween_t + dt / BUTTON_TWEEN_DURATION)
            if self.button_tween_t >= 1.0:
                self.button_state = "confirm"
        elif self.button_state == "returning":
            self.button_tween_t = max(0.0, self.button_tween_t - dt / BUTTON_TWEEN_DURATION)
            if self.button_tween_t <= 0.0:
                self.button_state = "main"

    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        return 1 - (1 - t) ** 3

    def on_input(self, input_id, input_data) -> None:
        if not getattr(input_data, "pressed", False):
            return

        if self.selecting_hats:
            self._on_input_hat_selection(input_id)
            return

        # Navegación del menú principal con W y S
        if input_id == "p1_up":
            self.selected_index = (self.selected_index - 1) % len(OPTIONS)
            self.hover_sound.play()
        elif input_id == "p1_down":
            self.selected_index = (self.selected_index + 1) % len(OPTIONS)
            self.hover_sound.play()
        elif input_id == "p1_main":
            self.click_sound.play()
            self._confirm_selection()

    def _on_input_hat_selection(self, input_id: str) -> None:
        if self.hat_current_player >= len(self.menu_personapas):
            return
        if not self.hat_available_indices:
            return

        # Ahora se puede navegar por los sombreros usando A / D y también W / S
        if input_id in ("p1_left", "p1_up"):
            self.hat_cursor = (self.hat_cursor - 1) % len(self.hat_available_indices)
            self.hover_sound.play()
            self._apply_hat_preview()

        elif input_id in ("p1_right", "p1_down"):
            self.hat_cursor = (self.hat_cursor + 1) % len(self.hat_available_indices)
            self.hover_sound.play()
            self._apply_hat_preview()

        elif input_id == "p1_main":
            self.click_sound.play()
            chosen_hat_index = self.hat_available_indices[self.hat_cursor]

            self.menu_personapas[self.hat_current_player].hat_index = chosen_hat_index
            self.hat_available_indices.remove(chosen_hat_index)

            self.hat_current_player += 1
            self.hat_cursor = 0

            if self.hat_current_player >= len(self.menu_personapas):
                self.state_machine.change("play", personapas=self.menu_personapas)
            else:
                self._apply_hat_preview()

    def _apply_hat_preview(self) -> None:
        if not self.hat_available_indices:
            return
        hat_index = self.hat_available_indices[self.hat_cursor]
        self.menu_personapas[self.hat_current_player].hat_index = hat_index

    def _start_hat_selection(self) -> None:
        self.selecting_hats = True
        self.hat_sprites = HatSprites()

        for p in self.menu_personapas:
            p.hat_sprites = self.hat_sprites
            p.hat_index = -1

        self.hat_current_player = 0
        self.hat_available_indices = list(range(self.hat_sprites.get_hat_count()))
        self.hat_cursor = 0
        self._apply_hat_preview()

    def _confirm_selection(self) -> None:
        if self.button_state not in ("main", "confirm"):
            return

        if self.selected_index == 0:  # Jugar
            if self.button_state == "main":
                self.button_state = "confirming"
                self._start_hat_selection()
        else:  # Salir
            if self.button_state == "confirm":
                self.button_state = "returning"
            else:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.stripes_surface, (0, 0))

        self._render_menu_personapas(surface)

        eased = self._ease_out_cubic(self.button_tween_t)
        title_alpha = int(255 * (1 - eased))

        if title_alpha > 0:
            title = self._title_surface
            title.set_alpha(title_alpha)
            title_rect = title.get_rect(center=(self.width // 2, self.height // 3 - 30))
            surface.blit(title, title_rect)

        self._render_buttons(surface, eased)

        if self.selecting_hats:
            self._render_hat_selection_overlay(surface)

    def _render_hat_selection_overlay(self, surface: pygame.Surface) -> None:
        title_text = self._hat_title_font.render("Selecciona tu Sombrero", True, "white")
        title_rect = title_text.get_rect(center=(self.width // 2, 40))
        surface.blit(title_text, title_rect)

        if self.hat_current_player < len(self.menu_personapas):
            player_text = self._hat_player_font.render(
                f"Jugador {self.hat_current_player + 1}", True, TITLE_COLOR
            )
            player_rect = player_text.get_rect(center=(self.width // 2, 80))
            surface.blit(player_text, player_rect)

        self._render_hat_carousel(surface)

        hint_text = self._hat_hint_font.render(
            "A / D o W / S: Navegar Sombreros | Botón principal: Seleccionar", True, "white"
        )
        hint_rect = hint_text.get_rect(center=(self.width // 2, 120))
        surface.blit(hint_text, hint_rect)

    def _render_hat_carousel(self, surface: pygame.Surface) -> None:
        if not self.hat_available_indices:
            return

        hat_previews = self.hat_sprites.get_all_hat_preview_frames()

        hat_size = 56
        spacing = 80
        visible_hats = 5
        carousel_y = 165

        num_available = len(self.hat_available_indices)
        start_pos = max(0, self.hat_cursor - visible_hats // 2)
        start_pos = min(start_pos, max(0, num_available - visible_hats))

        center_x = self.width // 2

        for i in range(min(visible_hats, num_available - start_pos)):
            list_pos = start_pos + i
            hat_idx = self.hat_available_indices[list_pos]

            offset = (i - visible_hats // 2) * spacing
            x = center_x + offset
            y = carousel_y

            preview = hat_previews[hat_idx]
            scaled = pygame.transform.scale(preview, (hat_size, hat_size))

            rect = scaled.get_rect(center=(x, y))

            backdrop = pygame.Surface((hat_size + 12, hat_size + 12), pygame.SRCALPHA)
            pygame.draw.rect(backdrop, (20, 20, 30, 160), backdrop.get_rect(), border_radius=10)
            surface.blit(backdrop, backdrop.get_rect(center=(x, y)))

            surface.blit(scaled, rect)

            if list_pos == self.hat_cursor:
                pygame.draw.rect(surface, TITLE_COLOR, rect.inflate(6, 6), width=3, border_radius=6)

    def _render_buttons(self, surface: pygame.Surface, eased: float) -> None:
        button_width, button_height = 260, 70
        spacing = 24
        start_y = self.height // 3 + 90
        margin = BUTTON_EDGE_MARGIN

        main_positions = [
            (self.width // 2, start_y),
            (self.width // 2, start_y + button_height + spacing),
        ]

        confirm_positions = [
            (self.width - margin - button_width // 2, self.height - margin - button_height // 2),
            (margin + button_width // 2, self.height - margin - button_height // 2),
        ]

        showing_arrow = self.button_state != "main"

        for i, option in enumerate(OPTIONS):
            if option == "SALIR" and self.selecting_hats:
                continue
            
            is_selected = i == self.selected_index
            bounce = math.sin(self._time * 6) * 4 if is_selected else 0

            main_x, main_y = main_positions[i]
            target_x, target_y = confirm_positions[i]
            center = (
                main_x + (target_x - main_x) * eased,
                main_y + (target_y - main_y) * eased + bounce,
            )

            fill = BUTTON_FILL_SELECTED if is_selected else BUTTON_FILL_IDLE
            text_color = BUTTON_TEXT_SELECTED if is_selected else BUTTON_TEXT_IDLE

            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = center

            shadow_rect = rect.copy()
            shadow_rect.y += 6
            pygame.draw.rect(surface, (20, 20, 30, 120), shadow_rect, border_radius=18)

            pygame.draw.rect(surface, fill, rect, border_radius=18)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect, width=4, border_radius=18)

            label = self._button_label_surfaces[(option, is_selected)]
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

    def _draw_back_arrow(self, surface: pygame.Surface, rect: pygame.Rect, color) -> None:
        cx, cy = rect.center
        size = 16
        points = [
            (cx + size, cy - size),
            (cx - size, cy),
            (cx + size, cy + size),
        ]
        pygame.draw.lines(surface, color, False, points, width=6)