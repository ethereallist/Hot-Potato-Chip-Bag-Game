"""Personapa: the player character during ParkourState."""

import pygame

from gale.particle_system import ParticleSystem


class DashTrail:
    """Continuous particle effect built on top of gale.particle_system.
    ParticleSystem is meant to generate a single batch at once, so this
    just spawns a new tiny ParticleSystem every `spawn_interval` seconds
    and keeps them all updated until they finish on their own."""

    def __init__(self, spawn_interval: float = 0.03) -> None:
        self.active_systems: list[ParticleSystem] = []
        self.spawn_interval = spawn_interval
        self._spawn_timer: float = 0.0

    def emit(self, dt: float, position: tuple) -> None:
        self._spawn_timer -= dt
        if self._spawn_timer > 0:
            return
        self._spawn_timer = self.spawn_interval

        puff = ParticleSystem(position[0], position[1], n=3)
        puff.set_life_time(0.15, 0.25)
        puff.set_linear_acceleration(0, 0, 0, 0)  # no acceleration: just fade in place
        puff.set_colors([pygame.Color(255, 255, 255, 255)])
        puff.set_area_spread(6, 6)
        puff.generate()
        self.active_systems.append(puff)

    def update(self, dt: float) -> None:
        for system in self.active_systems:
            system.update(dt)
        self.active_systems = [s for s in self.active_systems if s.particles]

    def render(self, surface: pygame.Surface) -> None:
        for system in self.active_systems:
            system.render(surface)


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
        self.dash_speed: float = 600
        self.dash_duration: float = 0.15
        self.dash_cooldown: float = 0.6
        self.is_dashing: bool = False
        self.dash_time_left: float = 0.0
        self.cooldown_time_left: float = 0.0
        self.dash_direction = pygame.Vector2(1, 0)
        self.facing_direction = pygame.Vector2(1, 0)
        self._main_action_was_pressed: bool = False

        self.dash_trail = DashTrail()

    def move(self, dt: float) -> None:
        if self.move_intent.length_squared() > 0:
            self.facing_direction = self.move_intent.normalize()

        if self.cooldown_time_left > 0:
            self.cooldown_time_left -= dt

        pressed_now = self.main_action_intent
        if pressed_now and not self._main_action_was_pressed:
            self.dash()
        self._main_action_was_pressed = pressed_now

        if self.is_dashing:
            self.position += self.dash_direction * self.dash_speed * dt
            self.dash_time_left -= dt
            if self.dash_time_left <= 0:
                self.is_dashing = False

            self.dash_trail.emit(dt, self.collide_box.center)
        else:
            direction = self.move_intent
            if direction.length_squared() > 0:
                direction = direction.normalize()
            self.position += direction * self.max_speed * dt

        self.collide_box.topleft = (self.position.x, self.position.y)
        self.dash_trail.update(dt)  # keep fading even after the dash ends

    def dash(self) -> None:
        if self.is_dashing or self.cooldown_time_left > 0:
            return

        self.is_dashing = True
        self.dash_time_left = self.dash_duration
        self.cooldown_time_left = self.dash_cooldown
        self.dash_direction = pygame.Vector2(self.facing_direction)

    def _get_other_box(self, other) -> pygame.Rect:
        return getattr(other, "collide_box", None) or getattr(other, "collidebox", None)

    def collides_with(self, other) -> bool:
        other_box = self._get_other_box(other)
        if other_box is None:
            return False
        return self.collide_box.colliderect(other_box)

    def handle_collision(self, other) -> None:
        if not self.collides_with(other):
            return

        if hasattr(other, "on_collide"):
            other.on_collide()

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
        self.dash_trail.render(surface)

        # placeholder: white circle while there's no sprite/appearance yet;
        # red while dashing
        color = "red" if self.is_dashing else "white"
        pygame.draw.circle(surface, color, self.collide_box.center, self.size // 2)