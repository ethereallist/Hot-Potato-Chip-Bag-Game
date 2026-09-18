"""Personapa: the player character during ParkourState."""

import random

import pygame


class DashParticle:
    """Partícula chiquita y orgánica del dash: se va encogiendo y
    desvaneciendo (alpha real, no un cuadrito opaco), dejando una
    traza suave que desaparece sola."""

    __slots__ = ("x", "y", "vx", "vy", "radius", "life", "max_life")

    def __init__(self, x: float, y: float, vx: float, vy: float, radius: float, life: float) -> None:
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.radius = radius
        self.life = life
        self.max_life = life

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.9
        self.vy *= 0.9
        self.life -= dt

    @property
    def is_alive(self) -> bool:
        return self.life > 0

    def render(self, surface: pygame.Surface) -> None:
        t = max(0.0, self.life / self.max_life)
        radius = max(1, round(self.radius * t))  # se encoge con el tiempo
        alpha = int(200 * t)
        if alpha <= 0:
            return

        temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp, (255, 255, 255, alpha), (radius, radius), radius)
        surface.blit(temp, (int(self.x - radius), int(self.y - radius)))


class DashTrail:
    """Suelta un par de DashParticle cada spawn_interval segundos,
    mientras el personaje esté dasheando."""

    def __init__(self, spawn_interval: float = 0.025) -> None:
        self.particles: list[DashParticle] = []
        self.spawn_interval = spawn_interval
        self._spawn_timer: float = 0.0

    def emit(self, dt: float, position: tuple) -> None:
        self._spawn_timer -= dt
        if self._spawn_timer > 0:
            return
        self._spawn_timer = self.spawn_interval

        for _ in range(12):
            angle = random.uniform(0, 360)
            speed = random.uniform(9, 42)
            direction = pygame.Vector2(1, 0).rotate(angle)
            radius = random.uniform(3, 7)
            life = random.uniform(0.18, 0.4)
            # dispersión en la posición de nacimiento, no solo en la
            # velocidad, para que se vea como una nube llena y no una
            # sola línea de puntos
            offset = pygame.Vector2(random.uniform(-9, 9), random.uniform(-9, 9))
            x = position[0] + offset.x
            y = position[1] + offset.y
            self.particles.append(
                DashParticle(x, y, direction.x * speed, direction.y * speed, radius, life)
            )

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

    def render(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.render(surface)


class Personapa:
    def __init__(self) -> None:
        
        # Sombrero del personaje
        self.hat_index: int = -1  # -1 significa sin sombrero
        self.hat_sprites = None  # instancia compartida de HatSprites
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

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size, self.size)

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

            self.dash_trail.emit(dt, self.get_rect().center)
        else:
            direction = self.move_intent
            if direction.length_squared() > 0:
                direction = direction.normalize()
            self.position += direction * self.max_speed * dt

        self.dash_trail.update(dt)  # keep fading even after the dash ends

    def dash(self) -> None:
        if self.is_dashing or self.cooldown_time_left > 0:
            return

        self.is_dashing = True
        self.dash_time_left = self.dash_duration
        self.cooldown_time_left = self.dash_cooldown
        self.dash_direction = pygame.Vector2(self.facing_direction)

    def _get_other_box(self, other) -> pygame.Rect:
        method = getattr(other, "get_rect", None)
        if method is not None:
            return method()
        return None

    def collides_with(self, other) -> bool:
        other_box = self._get_other_box(other)
        if other_box is None:
            return False
        return self.get_rect().colliderect(other_box)

    def handle_collision(self, other) -> None:
        if not self.collides_with(other):
            return

        if hasattr(other, "on_collide"):
            other.on_collide()

        other_box = self._get_other_box(other)
        overlap = self.get_rect().clip(other_box)

        if overlap.width < overlap.height:
            if self.get_rect().centerx < other_box.centerx:
                self.position.x -= overlap.width
            else:
                self.position.x += overlap.width
        else:
            if self.get_rect().centery < other_box.centery:
                self.position.y -= overlap.height
            else:
                self.position.y += overlap.height

    def render(self, surface: pygame.Surface) -> None:
        self.dash_trail.render(surface)

        # placeholder: white circle while there's no sprite/appearance yet;
        # red while dashing
        color = "red" if self.is_dashing else "white"
        pygame.draw.circle(surface, color, self.get_rect().center, self.size // 2)