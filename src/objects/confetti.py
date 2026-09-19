"""Confeti: lluvia de papelitos de colores que cae desde arriba.

Sigue el mismo patrón que DashParticle / DashTrail de personapa.py:
una partícula chiquita con update()/render()/is_alive y un emisor que
las suelta con emit(dt), las actualiza con update(dt) y las dibuja con
render(surface).

(No se usa gale.particle_system.ParticleSystem porque su Particle dibuja
un cuadrito opaco de 4x4 con fondo negro -- justo el problema que
DashParticle ya había resuelto con superficies SRCALPHA.) Aquí ni
siquiera hacen falta superficies: cada papelito es un polígono que se
dibuja directo sobre la superficie destino, así que es barato aunque
haya cientos en pantalla.
"""

import math
import random

import pygame


# Casi todos vienen de los colores de los podios/jugadores (score_state.py)
# y el amarillo es el del título de WinState. El azul de los podios se
# cambió por blanco: WinState tiene fondo de franjas azules y un confeti
# azul se perdía por completo.
CONFETTI_COLORS = [
    (245, 60, 60),     # rojo
    (100, 255, 100),   # verde
    (255, 255, 255),   # blanco
    (255, 175, 55),    # naranja
    (255, 221, 0),     # amarillo
    (255, 105, 180),   # rosa
    (170, 90, 230),    # morado
    (60, 220, 220),    # cian
]


class ConfettiParticle:
    """Un papelito: cae con velocidad casi constante, se mece de lado a
    lado, gira sobre sí mismo y se "voltea" (se encoge en una dimensión y
    muestra su cara oscura) para que parezca que da vueltas en 3D."""

    __slots__ = (
        "x", "y", "vy", "fall_speed",
        "sway_amp", "sway_freq", "sway_phase",
        "angle", "spin", "flip_phase", "flip_speed",
        "width", "height", "color", "shade", "kill_y", "age",
    )

    def __init__(self, x: float, y: float, color: tuple, kill_y: float) -> None:
        self.x, self.y = x, y
        self.color = color
        self.shade = tuple(int(c * 0.6) for c in color)  # la "cara de atrás"
        self.kill_y = kill_y

        self.fall_speed = random.uniform(80, 170)   # px/s, velocidad de crucero
        self.vy = random.uniform(0, 60)             # arranca lento y acelera
        self.sway_amp = random.uniform(18, 46)      # px/s de vaivén lateral
        self.sway_freq = random.uniform(1.5, 3.5)
        self.sway_phase = random.uniform(0, math.tau)

        self.angle = random.uniform(0, math.tau)
        self.spin = random.uniform(-4, 4)           # rad/s
        self.flip_phase = random.uniform(0, math.tau)
        self.flip_speed = random.uniform(4, 9)      # rad/s

        self.width = random.uniform(6, 11)
        self.height = random.uniform(3, 6)
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt
        # Aceleración suave hacia la velocidad de crucero (como resistencia
        # del aire), en vez de caer en picada.
        self.vy += (self.fall_speed - self.vy) * min(1.0, 2.5 * dt)
        self.y += self.vy * dt
        self.x += math.sin(self.age * self.sway_freq + self.sway_phase) * self.sway_amp * dt
        self.angle += self.spin * dt
        self.flip_phase += self.flip_speed * dt

    @property
    def is_alive(self) -> bool:
        return self.y < self.kill_y

    def render(self, surface: pygame.Surface) -> None:
        flip = math.cos(self.flip_phase)
        half_w = self.width / 2
        half_h = max(0.5, (self.height / 2) * abs(flip))
        color = self.color if flip >= 0 else self.shade

        cos_a, sin_a = math.cos(self.angle), math.sin(self.angle)
        points = [
            (
                self.x + dx * cos_a - dy * sin_a,
                self.y + dx * sin_a + dy * cos_a,
            )
            for dx, dy in (
                (-half_w, -half_h),
                (half_w, -half_h),
                (half_w, half_h),
                (-half_w, half_h),
            )
        ]
        pygame.draw.polygon(surface, color, points)


class ConfettiRain:
    """Emisor: mantiene una lluvia continua de confeti que nace justo
    arriba del borde superior y cae hasta salir por abajo."""

    def __init__(self, width: int, height: int, rate: float = 40.0, colors=None) -> None:
        self.width = width
        self.height = height
        self.rate = rate                      # papelitos por segundo
        self.colors = colors or CONFETTI_COLORS
        self.particles: list[ConfettiParticle] = []
        self._spawn_acc: float = 0.0

    def _spawn(self, y: float) -> None:
        self.particles.append(
            ConfettiParticle(
                x=random.uniform(0, self.width),
                y=y,
                color=random.choice(self.colors),
                kill_y=self.height + 20,
            )
        )

    def prefill(self, count: int, depth: float) -> None:
        """Deja `count` papelitos ya "en camino" repartidos por encima de
        la pantalla (hasta `depth` px arriba), para que la lluvia arranque
        como un aguacero y no gota a gota."""
        for _ in range(count):
            self._spawn(-random.uniform(10, depth))

    def emit(self, dt: float) -> None:
        self._spawn_acc += self.rate * dt
        while self._spawn_acc >= 1.0:
            self._spawn_acc -= 1.0
            self._spawn(-random.uniform(6, 40))  # jitter para no formar una línea

    def update(self, dt: float) -> None:
        dt = min(dt, 0.05)  # un tirón de frame no debe teletransportar el confeti
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

    def render(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.render(surface)