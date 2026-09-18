"""PersonapaSpriteRenderer: dibuja una Personapa usando las mismas
animaciones de sprite que el menú (idle, caminar a los lados, caminar
hacia arriba) en vez del círculo placeholder. Elige cuál según hacia
dónde apunte move_intent, igual que en MenuState. También renderiza
el sombrero encima si el personaje tiene uno."""

import pygame

from src.objects.sprite_animation import SpriteAnimation


class PersonapaSpriteRenderer:
    def __init__(self) -> None:
        self.walk_right_animation = SpriteAnimation(
            "assets/sprites/personapa_walk_right.png",
            frame_width=32, frame_height=32, frame_count=6, fps=8,
        )
        self.idle_animation = SpriteAnimation(
            "assets/sprites/personapa_idle.png",
            frame_width=32, frame_height=32, frame_count=7, columns=3, fps=6,
        )
        self.walk_up_animation = SpriteAnimation(
            "assets/sprites/personapa_walk_up.png",
            frame_width=32, frame_height=32, frame_count=4, fps=8,
        )

    def _get_hat_direction_index(self, move_intent: pygame.Vector2) -> tuple:
        """Determina qué índice de dirección del sombrero usar.

        Retorna (hat_frame_index, flipped)

        Mapeo de move_intent a índices de sombrero:
        - frame 0: abajo (frente)
        - frame 1: derecha (o izquierda si flipped)
        - frame 2: arriba variante 1
        - frame 3: arriba variante 2 (vuelta al frente)
        - frame 4: diagonal abajo-izquierda
        - frame 5: diagonal abajo-derecha
        """

        if move_intent.length_squared() < 0.01:
            return 0, False  # Sin movimiento: frente

        norm = move_intent.normalize()
        x, y = norm.x, norm.y

        if abs(x) > abs(y):
            # Movimiento horizontal predominante
            if x > 0:
                return 1, True    # Derecha: frame 1 volteado
            else:
                return 1, False   # Izquierda: frame 1 tal cual

        elif y < -0.1:
            return 2, False  # Arriba

        elif y > 0.1:
            if x < -0.3:
                return 4, False  # Diagonal abajo-izquierda
            elif x > 0.3:
                return 5, False  # Diagonal abajo-derecha
            else:
                return 0, False  # Abajo puro (frente)

        else:
            return 0, False

    def render(self, surface: pygame.Surface, personapa, anim_time: float, visual_scale: float = 1.0) -> None:
        personapa.dash_trail.render(surface)  # la estela va detrás del personaje

        move_intent = personapa.move_intent

        if abs(move_intent.x) > abs(move_intent.y) and abs(move_intent.x) > 0.1:
            flipped = move_intent.x < 0
            frame = self.walk_right_animation.get_frame(anim_time, flipped=flipped)
        elif move_intent.y < -0.1 and abs(move_intent.y) >= abs(move_intent.x):
            frame = self.walk_up_animation.get_frame(anim_time)
        else:
            flipped = personapa.facing_direction.x < 0
            frame = self.idle_animation.get_frame(anim_time, flipped=flipped)

        render_size = int(personapa.size * visual_scale)
        frame = pygame.transform.scale(frame, (render_size, render_size))
        rect = frame.get_rect(center=personapa.get_rect().center)
        surface.blit(frame, rect)

        if personapa.hat_index >= 0 and personapa.hat_sprites is not None:
            self._render_hat(surface, personapa, anim_time, visual_scale, rect)

    def _render_hat(self, surface: pygame.Surface, personapa, anim_time: float, visual_scale: float, character_rect: pygame.Rect) -> None:
        """Renderiza el sombrero arriba del personaje."""

        hat_sprites = personapa.hat_sprites
        hat_index = personapa.hat_index

        frame_idx, flipped = self._get_hat_direction_index(personapa.move_intent)
        hat_frame = hat_sprites.get_hat_frame(hat_index, frame_idx, flipped=flipped)

        if hat_frame is None:
            return

        # Escalar el sombrero: tamaño base según el personaje, +10px
        # (5px arriba, 5px abajo) para que se vea más grande.
        # Escalar el sombrero: tamaño base según el personaje, +16px
        # (8px arriba, 8px abajo aprox.) para que se vea más grande.
        hat_size = int(48 * visual_scale) + 16
        hat_frame = pygame.transform.scale(hat_frame, (hat_size, hat_size))
        
        # Posicionar el sombrero arriba del personaje, no a media altura:
        # el sombrero queda centrado horizontalmente, y su borde inferior
        # se apoya cerca del borde superior del personaje (con un solape
        # para que no se vea flotando separado), bajado 31px en total
        # (16 + 15 más) porque quedaba demasiado alto sobre la cabeza.
        overlap = hat_size // 4 + 40
        hat_rect = hat_frame.get_rect()
        hat_rect.centerx = character_rect.centerx
        hat_rect.bottom = character_rect.top + overlap

        surface.blit(hat_frame, hat_rect)