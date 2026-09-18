"""SpriteAnimation: recorta un spritesheet horizontal (todos los frames
en una sola fila, del mismo tamaño) y va devolviendo el frame que toca
según el tiempo transcurrido."""

import pygame


class SpriteAnimation:
    def __init__(
        self,
        sheet_path: str,
        frame_width: int,
        frame_height: int,
        frame_count: int,
        columns: int = None,
        fps: float = 8,
    ) -> None:
        sheet = pygame.image.load(sheet_path).convert_alpha()

        if columns is None:
            columns = frame_count  # antes: todos los frames en una sola fila

        self.frames = []
        for i in range(frame_count):
            row, col = divmod(i, columns)
            rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
            frame = sheet.subsurface(rect).copy()
            self.frames.append(frame)

        # versión espejada de cada frame, calculada una sola vez aquí
        # (no cada frame del juego) para poder usarla al ir hacia la
        # izquierda sin necesitar un spritesheet aparte
        self.frames_flipped = [pygame.transform.flip(f, True, False) for f in self.frames]

        self.frame_duration = 1.0 / fps

    def get_frame(self, elapsed_time: float, flipped: bool = False) -> pygame.Surface:
        index = int(elapsed_time / self.frame_duration) % len(self.frames)
        return self.frames_flipped[index] if flipped else self.frames[index]