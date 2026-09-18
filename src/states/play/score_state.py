"""ScoreState: estado de puntuación después de una ronda."""
import pygame
from gale.state import BaseState
from gale.timer import Timer

from src.objects.podio import Podio
from src.objects.personapa_sprite_renderer import PersonapaSpriteRenderer
from src.objects.transitions import FadeInOut

class ScoreState(BaseState):
    def enter(self, **kwargs) -> None:
        self.play_state = kwargs["play_state"]
        self.death_log = kwargs["death_log"]
        self.personapas = kwargs["personapas"]

        # 1. Actualizar puntajes
        for i, survived in enumerate(self.death_log):
            if survived:
                self.play_state.scores[i] += 1
        self.play_state.rounds += 1

        self.renderer = PersonapaSpriteRenderer()
        self.anim_time = 0.0

        # 2. Configurar podios
        self.podios = []
        screen_w, screen_h = pygame.display.get_surface().get_size()
        ancho_podio = 80
        espacio = 60
        total_w = (ancho_podio * len(self.personapas)) + (espacio * (len(self.personapas) - 1))
        start_x = (screen_w - total_w) // 2

        colores = [(245, 60, 60), (100, 255, 100), (60, 150, 255), (255, 175, 55)]

        for i in range(len(self.personapas)):
            puntos = self.play_state.scores[i]
            altura = 40 + (puntos * 40)  # La barra crece según los puntos
            podio = Podio({
                "x": start_x + (ancho_podio + espacio) * i,
                "y": screen_h - 130, # Espacio extra abajo para los números
                "width": ancho_podio,
                "height": altura,
                "color": colores[i % len(colores)]
            })
            self.podios.append(podio)

        # 3. Fuentes estilo UI
        try:
            self.font = pygame.font.Font("assets/fonts/Hansief.otf", 40)
        except:
            self.font = pygame.font.SysFont(None, 40)

        self.transition = None
        self.is_transitioning = False

        # Esperar 3.5 segundos mostrando resultados y luego iniciar transición
        Timer.after(3.5, self._start_transition)

    def _start_transition(self):
        self.is_transitioning = True
        self.transition = FadeInOut(duration=1.0, color=(20, 22, 32), fade_out=True, on_finish=self._on_transition_finish)

    def _on_transition_finish(self):
        winner_index = self.play_state.check_winner()
        if winner_index != -1:
            # Pasa al estado de victoria
            self.state_machine.change("win", play_state=self.play_state, winner_index=winner_index, personapas=self.personapas)
        else:
            # Siguiente ronda
            self.play_state.substate_machine.change("parkour", play_state=self.play_state, personapas=self.personapas)

    def update(self, dt: float) -> None:
        self.anim_time += dt

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 22, 32)) # Fondo oscuro estilo UI

        for i, podio in enumerate(self.podios):
            # Dibujar el podio (barra)
            podio.render(surface)

            # Dibujar el texto de los puntos JUSTO DEBAJO del podio
            puntos_str = f"{self.play_state.scores[i]} pts"
            text_surf = self.font.render(puntos_str, True, (245, 245, 245))
            text_rect = text_surf.get_rect(center=(podio.x + podio.width // 2, podio.y + 30))
            surface.blit(text_surf, text_rect)

            # Dibujar la Personapa (y su sombrero) ARRIBA de la barra
            personapa = self.personapas[i]
            
            # Truco: Temporalmente movemos la posición del personapa a la cima del podio para renderizar
            pos_original = personapa.position.copy()
            # Apoyamos la parte baja de la personapa en la parte superior del podio (podio.y - podio.height)
            personapa.position = pygame.Vector2(
                podio.x + (podio.width // 2) - (personapa.size // 2),
                podio.y - podio.height - personapa.size + 15
            )
            # Forzamos que miren hacia el frente 
            personapa.move_intent = pygame.Vector2(0, 0)
            personapa.facing_direction = pygame.Vector2(0, 1)

            # Usamos el renderer para que dibuje el sprite animado y el sombrero encima
            self.renderer.render(surface, personapa, self.anim_time, visual_scale=1.5)

            # Restauramos la posición original
            personapa.position = pos_original

        # Si está transicionando, pintar encima el Fade
        if self.is_transitioning and self.transition:
            self.transition.render(surface)