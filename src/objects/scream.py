"""Gritos de los jugadores (acción secundaria).

Hay 13 sonidos de grito (settings.SOUNDS["screams"]) y 4 jugadores. Al
empezar CADA partida se "reparte" un grito distinto a cada jugador
(ScreamDeck.deal), sacándolos de una bolsa barajada: los sonidos no se
repiten hasta que ya salieron todos, así que a lo largo de varias
partidas se terminan usando los 13, y dentro de una misma partida dos
jugadores nunca comparten el mismo grito.
"""

import random

import pygame

import settings

SCREAM_VOLUME = 0.5  # 0.0 a 1.0; la música de fondo suena muy bajito, así que el grito no debe taparla


class ScreamDeck:
    _sounds: dict = {}   # ruta -> pygame.mixer.Sound (cache, se cargan una sola vez)
    _bag: list = []      # rutas que todavía no han salido en esta "vuelta"

    @classmethod
    def _load(cls, path: str) -> pygame.mixer.Sound:
        if path not in cls._sounds:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(SCREAM_VOLUME)
            cls._sounds[path] = sound
        return cls._sounds[path]

    @classmethod
    def deal(cls, count: int) -> list:
        """Devuelve `count` sonidos distintos (uno por jugador)."""
        paths = list(settings.SOUNDS["screams"])
        hand: list = []
        while len(hand) < count:
            if not cls._bag:
                # bolsa nueva con todos los gritos, menos los que ya están en esta mano
                cls._bag = [p for p in paths if p not in hand] or paths[:]
                random.shuffle(cls._bag)
            hand.append(cls._bag.pop())
        return [cls._load(p) for p in hand]