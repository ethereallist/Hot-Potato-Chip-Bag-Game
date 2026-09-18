"""WinState: Pantalla final que muestra al jugador ganador con su puntuación."""
import pygame
from gale.state import BaseState
from src.objects.personapa_sprite_renderer import PersonapaSpriteRenderer
from src.objects.transitions import FadeInOut # Ajusta la ruta si es necesario

class WinState(BaseState):
    def enter(self, **kwargs) -> None:
        self.play_state = kwargs["play_state"]
        self.winner_index = kwargs["winner_index"]
        self.personapas = kwargs["personapas"]
        
        self.winner_personapa = self.personapas[self.winner_index]
        self.winner_score = self.play_state.scores[self.winner_index]

        self.renderer = PersonapaSpriteRenderer()
        self.anim_time = 0.0

        try:
            self.font_title = pygame.font.Font("assets/fonts/Hansief.otf", 96)
            self.font_score = pygame.font.Font("assets/fonts/Hansief.otf", 48)
        except:
            self.font_title = pygame.font.SysFont(None, 96)
            self.font_score = pygame.font.SysFont(None, 48)

        # Transición de entrada (desaparece el fundido en negro y aparece la UI)
        self.transition = FadeInOut(duration=1.5, color=(20, 22, 32), fade_out=False)

    def update(self, dt: float) -> None:
        self.anim_time += dt

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 22, 32))  # Fondo oscuro base UI

        screen_w, screen_h = surface.get_size()

        # Título ¡GANADOR!
        title_text = "¡TENEMOS GANADOR!"
        title_surf = self.font_title.render(title_text, True, (255, 215, 0)) # Dorado
        title_rect = title_surf.get_rect(center=(screen_w // 2, screen_h // 2 - 160))
        
        # Sombra del título
        shadow_surf = self.font_title.render(title_text, True, (10, 10, 15))
        surface.blit(shadow_surf, (title_rect.x + 5, title_rect.y + 5))
        surface.blit(title_surf, title_rect)

        # Puntos Obtenidos
        score_text = f"El Jugador {self.winner_index + 1} arrasó con {self.winner_score} Puntos"
        score_surf = self.font_score.render(score_text, True, (245, 245, 245))
        score_rect = score_surf.get_rect(center=(screen_w // 2, screen_h // 2 + 150))
        surface.blit(score_surf, score_rect)

        # Dibujar a la Personapa ganadora (Grande y en el centro)
        pos_original = self.winner_personapa.position.copy()
        
        # Forzamos que mire al frente contenta
        self.winner_personapa.move_intent = pygame.Vector2(0, 0)
        self.winner_personapa.facing_direction = pygame.Vector2(0, 1)

        # Centrar en pantalla
        self.winner_personapa.position = pygame.Vector2(
            (screen_w // 2) - (self.winner_personapa.size // 2), 
            (screen_h // 2) - (self.winner_personapa.size // 2) - 10
        )

        # Escala gigante para que el ganador destaque (x3.0)
        self.renderer.render(surface, self.winner_personapa, self.anim_time, visual_scale=3.0)

        # Restaurar posición
        self.winner_personapa.position = pos_original

        # Aplicar el render de la transición
        if not self.transition.finished:
            self.transition.render(surface)