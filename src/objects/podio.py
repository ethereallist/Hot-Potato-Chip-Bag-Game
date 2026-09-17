"""Podio: representa a un jugador sobre su pedestal de puntaje durante
ScoreState."""
import pygame


class Podio:
    def __init__(self, params: dict) -> None:
        self.x = params.get("x", 0)
        self.y = params.get("y", 0)
        self.height: float = params.get("height", 0.0)
        self.width: float = params.get("width", 0.0)
        self.personapa_ref = params.get("personapa_ref", None)
        self.color = params.get("color", (100, 100, 100))

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dibujar el rectángulo del podio
        # Como (x, y) es la esquina inferior izquierda, restamos la altura para la coordenada top_y
        rect_top_y = self.y - self.height
        rectulo_podio = pygame.Rect(self.x, rect_top_y, self.width, self.height)
        pygame.draw.rect(surface, self.color, rectulo_podio)

        # 2. Dibujar la imagen sobre el rectángulo (si está definida)
        if self.personapa_ref is not None:
            img_rect = self.personapa_ref.get_rect()
            
            # Alinear horizontalmente al centro del podio
            img_x = self.x + (self.width - img_rect.width) / 2
            
            # Alinear verticalmente para que la base de la imagen toque la parte superior del podio
            img_y = rect_top_y - img_rect.height
            
            surface.blit(self.personapa_ref, (img_x, img_y))
