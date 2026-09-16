"""Personapa: the player character during ParkourState."""

import pygame


class Personapa:
    def __init__(self) -> None:
        self.position = pygame.Vector2(0, 0)
        self.max_speed: float = 200  # px/second

        # Intents filled in by PlayerController through the Commands
        self.move_intent = pygame.Vector2(0, 0)
        self.main_action_intent: bool = False  # dash
        self.secondary_action_intent: bool = False

        self.appearance = None
        self.is_hot_potato: bool = False
        self.is_alive: bool = True
        self.size: int = 40  # width/height of the box, while there's no sprite
        self.collide_box = pygame.Rect(0, 0, self.size, self.size)

        # --- Dash ---
        self.dash_speed: float = 600  # px/second, while dashing
        self.dash_duration: float = 0.15  # seconds the dash lasts
        self.dash_cooldown: float = 0.6  # seconds before dashing again
        self.is_dashing: bool = False
        self.dash_time_left: float = 0.0
        self.cooldown_time_left: float = 0.0
        self.dash_direction = pygame.Vector2(1, 0)
        # last non-zero movement direction, in case you release the
        # stick/key right before dashing (so you don't dash with no direction)
        self.facing_direction = pygame.Vector2(1, 0)
        self._main_action_was_pressed: bool = False

    def move(self, dt: float) -> None:
        if self.move_intent.length_squared() > 0:
            self.facing_direction = self.move_intent.normalize()

        if self.cooldown_time_left > 0:
            self.cooldown_time_left -= dt

        # dash triggers only on the frame it's pressed, not while held down
        pressed_now = self.main_action_intent
        if pressed_now and not self._main_action_was_pressed:
            self.dash()
        self._main_action_was_pressed = pressed_now

        if self.is_dashing:
            self.position += self.dash_direction * self.dash_speed * dt
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.is_dashing = False
        else:
            direction = self.move_intent
            if direction.length_squared() > 0:
                direction = direction.normalize()
            self.position += direction * self.max_speed * dt

        self.collide_box.topleft = (self.position.x, self.position.y)

    def dash(self) -> None:
        if self.is_dashing or self.cooldown_time_left > 0:
            return  # still on cooldown, or already dashing: ignore

        self.is_dashing = True
        self.dash_time_left = self.dash_duration
        self.cooldown_time_left = self.dash_cooldown
        self.dash_direction = pygame.Vector2(self.facing_direction)

    def _get_other_box(self, other) -> pygame.Rect:
        # accepts either an Objeto (which uses "collidebox") or a
        # Personapa/Cursor (which uses "collide_box")
        return getattr(other, "collide_box", None) or getattr(other, "collidebox", None)

    def collides_with(self, other) -> bool:
        other_box = self._get_other_box(other)
        if other_box is None:
            return False
        return self.collide_box.colliderect(other_box)

    def handle_collision(self, other) -> None:
        if not self.collides_with(other):
            return

        # trigger the other object's own reaction, e.g. an Objeto placed
        # on the map (does nothing if "other" has no on_collide, like
        # another Personapa)
        if hasattr(other, "on_collide"):
            other.on_collide()

        # push this Personapa back out of the overlap along the shorter
        # axis, so it doesn't stay stuck inside a wall/object/player
        other_box = self._get_other_box(other)
        overlap = self.collide_box.clip(other_box)

        if overlap.width < overlap.height:
            if self.collide_box.centerx < other_box.centerx:
                self.position.x -= overlap.width
            else:
                self.position.x += overlap.width
        else:
            if self.collide_box.centery < other_box.centery:
                self.position.y -= overlap.height
            else:
                self.position.y += overlap.height

        self.collide_box.topleft = (self.position.x, self.position.y)

    def render(self, surface: pygame.Surface) -> None:
        # placeholder: white box while there's no sprite/appearance yet;
        # red while dashing, just so you can see it working
        color = "red" if self.is_dashing else "white"
        pygame.draw.rect(surface, color, self.collide_box)