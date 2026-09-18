"""HatSprites: carga todos los sombreros disponibles desde los spritesheets.

En vez de asumir un margen/gap fijo entre sprites (que resultó no ser
consistente entre hojas y llevó a varios intentos fallidos a ojo), esta
versión DETECTA automáticamente dónde empieza y termina cada sprite
analizando el canal alpha de la imagen: una columna o fila de píxeles
totalmente transparente se interpreta como separación entre sprites.

La carga se hace en DOS PASADAS:
  1) Detectar la grilla y recortar el contenido real (sin transparencia
     sobrante) de las 3 hojas, guardando todo en memoria.
  2) Calcular UN SOLO tamaño de canvas cuadrado, el máximo de TODOS los
     sombreros de las 3 hojas juntas, y centrar cada recorte ahí.
Si el canvas se calculara hoja por hoja (como en una versión anterior),
sombreros de una hoja con menos "aire" alrededor terminarían viéndose
más chicos que los de otra hoja al escalarlos todos al mismo tamaño
final en el juego. Con un solo canvas global, todos quedan consistentes.

Cada sombrero tiene 6 frames de direcciones diferentes:
  0: frente (abajo)
  1: derecha (se usa volteado)
  2: arriba (variante 1)
  3: arriba (variante 2 - vuelta al frente)
  4: diagonal abajo-izquierda
  5: diagonal abajo-derecha
"""

import pygame
import numpy as np
from typing import List, Tuple


class HatSprites:
    """Carga todos los sombreros disponibles desde 3 spritesheets,
    detectando automáticamente los límites de cada sprite y
    normalizándolos todos al mismo tamaño de canvas."""

    FRAMES_PER_HAT = 6  # columnas esperadas: 6 sprites de dirección
    HATS_PER_SHEET = 6  # filas esperadas: 6 sombreros por hoja

    ALPHA_THRESHOLD = 8  # por debajo de esto se considera "transparente"

    def __init__(self):
        """Carga los sombreros desde los 3 spritesheets."""
        self.hats: List[dict] = []
        self.hat_names: List[str] = []

        sheet_paths = [
            "assets/sprites/hats-personapa-1.png",
            "assets/sprites/hats-personapa-2.png",
            "assets/sprites/hats-personapa-3.png",
        ]

        # --- Pasada 1: detectar y recortar el contenido real de cada hoja ---
        tight_hats_per_sheet: List[List[List[pygame.Surface]]] = []
        max_content_size = 32  # tamaño mínimo por si algo falla

        for sheet_path in sheet_paths:
            try:
                tight_rows = self._extract_tight_frames(sheet_path)
                tight_hats_per_sheet.append(tight_rows)

                for row in tight_rows:
                    for frame in row:
                        max_content_size = max(
                            max_content_size, frame.get_width(), frame.get_height()
                        )
            except Exception as e:
                print(f"[HatSprites] ERROR cargando {sheet_path}: {type(e).__name__}: {e}")
                tight_hats_per_sheet.append([])

        # --- Pasada 2: centrar cada recorte en el canvas global único ---
        canvas_size = max_content_size

        for tight_rows in tight_hats_per_sheet:
            for row in tight_rows:
                hat_frames = []

                for tight_frame in row:
                    canvas = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
                    offset_x = (canvas_size - tight_frame.get_width()) // 2
                    offset_y = (canvas_size - tight_frame.get_height()) // 2
                    canvas.blit(tight_frame, (offset_x, offset_y))
                    hat_frames.append(canvas)

                hat_frames_flipped = [pygame.transform.flip(f, True, False) for f in hat_frames]

                self.hats.append({
                    "normal": hat_frames,
                    "flipped": hat_frames_flipped,
                })
                self.hat_names.append(f"Sombrero {len(self.hats)}")

    @staticmethod
    def _find_blocks(mask: np.ndarray) -> List[Tuple[int, int]]:
        """Dado un array booleano 1D (True = tiene contenido no
        transparente), retorna la lista de rangos (inicio, fin_exclusivo)
        de cada bloque contiguo de True, ignorando huecos de 1px
        (ruido de anti-aliasing) para no partir un sprite en dos."""
        blocks = []
        in_block = False
        start = 0
        gap_run = 0

        for i, val in enumerate(mask):
            if val:
                if not in_block:
                    start = i
                    in_block = True
                gap_run = 0
            else:
                if in_block:
                    gap_run += 1
                    if gap_run > 1:  # más de 1px transparente: sí es separación real
                        blocks.append((start, i - gap_run + 1))
                        in_block = False
                        gap_run = 0

        if in_block:
            blocks.append((start, len(mask) - gap_run))

        return blocks

    def _detect_grid(self, sheet: pygame.Surface):
        """Detecta los bloques de columnas (direcciones) y filas
        (sombreros) analizando el canal alpha de toda la hoja."""
        alpha = pygame.surfarray.pixels_alpha(sheet)  # shape: (width, height)
        has_content = alpha > self.ALPHA_THRESHOLD

        col_has_content = np.any(has_content, axis=1)  # por columna (ancho)
        row_has_content = np.any(has_content, axis=0)  # por fila (alto)

        col_blocks = self._find_blocks(col_has_content)
        row_blocks = self._find_blocks(row_has_content)

        return col_blocks, row_blocks

    def _extract_tight_frames(self, sheet_path: str) -> List[List[pygame.Surface]]:
        """Carga una hoja, detecta su grilla, y devuelve los recortes
        SIN normalizar a un canvas todavía (eso se hace después, con
        el tamaño global calculado entre las 3 hojas)."""
        sheet = pygame.image.load(sheet_path).convert_alpha()

        col_blocks, row_blocks = self._detect_grid(sheet)

        rows: List[List[pygame.Surface]] = []
        for row_start, row_end in row_blocks:
            row_frames = []
            for col_start, col_end in col_blocks:
                rect = pygame.Rect(col_start, row_start, col_end - col_start, row_end - row_start)
                row_frames.append(sheet.subsurface(rect).copy())
            rows.append(row_frames)

        return rows

    def get_hat_frame(self, hat_index: int, direction_index: int, flipped: bool = False) -> pygame.Surface:
        """Obtiene un frame específico de un sombrero."""
        if hat_index < 0 or hat_index >= len(self.hats):
            return None

        hat = self.hats[hat_index]
        frames = hat["flipped"] if flipped else hat["normal"]

        if direction_index < 0 or direction_index >= len(frames):
            return frames[0]

        return frames[direction_index]

    def get_hat_count(self) -> int:
        """Retorna el número total de sombreros disponibles."""
        return len(self.hats)

    def get_hat_name(self, hat_index: int) -> str:
        """Retorna el nombre del sombrero."""
        if 0 <= hat_index < len(self.hat_names):
            return self.hat_names[hat_index]
        return "Unknown"

    def get_all_hat_preview_frames(self) -> List[pygame.Surface]:
        """Retorna el primer frame (frente) de cada sombrero para preview."""
        return [hat["normal"][0] for hat in self.hats]