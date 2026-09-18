"""PersonapaSpriteRenderer: dibuja una Personapa usando las mismas
animaciones de sprite que el menú (idle, caminar a los lados, caminar
hacia arriba) en vez del círculo placeholder. Elige cuál según hacia
dónde apunte move_intent, igual que en MenuState."""

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

    def render(self, surface: pygame.Surface, personapa, anim_time: float, visual_scale: float = 1.0) -> None:
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