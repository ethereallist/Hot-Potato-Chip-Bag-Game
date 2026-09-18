"""HatSelectionState: permite a cada jugador seleccionar un sombrero
antes de entrar a ParkourState. Usa el mismo sistema de acciones
nombradas de gale (p1_left, p1_main, p2_left, ...) que ya usan
PlayerController y MenuState, en vez de eventos crudos de pygame.

Cada sombrero elegido por un jugador se retira del carrusel para los
jugadores siguientes, así nadie puede repetir el sombrero de otro."""

import pygame
from gale.state import BaseState

from src.objects.personapa import Personapa
from src.objects.hat_sprites import HatSprites


class HatSelectionState(BaseState):
    """Estado para seleccionar sombreros para cada jugador."""

    def enter(self, **kwargs) -> None:
        """Inicializar el estado de selección de sombreros."""

        self.play_state = kwargs["play_state"]
        self.personapas = kwargs.get("personapas", [])

        # Instancia compartida de HatSprites (carga todos los sombreros una sola vez)
        self.hat_sprites = HatSprites()

        for personapa in self.personapas:
            personapa.hat_sprites = self.hat_sprites

        self.current_player = 0

        # Índices de sombreros que todavía se pueden elegir. Se van
        # quitando de aquí conforme cada jugador confirma su elección,
        # así el siguiente jugador ya no lo ve como opción.
        self.available_indices = list(range(self.hat_sprites.get_hat_count()))

        pygame.font.init()
        try:
            self._title_font = pygame.font.Font("assets/fonts/Hansief.otf", 48)
            self._text_font = pygame.font.Font("assets/fonts/Hansief.otf", 32)
            self._small_font = pygame.font.Font("assets/fonts/Hansief.otf", 20)
        except (FileNotFoundError, pygame.error):
            self._title_font = pygame.font.SysFont(None, 48)
            self._text_font = pygame.font.SysFont(None, 32)
            self._small_font = pygame.font.SysFont(None, 20)

        self.hat_previews = self.hat_sprites.get_all_hat_preview_frames()

        # Posición del cursor DENTRO de available_indices (no es el
        # índice real del sombrero, sino su posición en la lista de
        # los que todavía quedan disponibles).
        self.hat_cursor = 0

    def on_input(self, input_id: str, input_data) -> None:
        """Gale llama esto por cada acción nombrada que se dispara
        (ver settings.py: p1_left, p1_main, p2_left, etc.), no con
        una cola de eventos de pygame.

        En esta pantalla se "pasa el control": no importa qué jugador
        tenga técnicamente asignada la tecla que se presionó, cualquier
        left/right/main de cualquier player_config cuenta como
        navegar/confirmar para quien le toca elegir ahora."""

        if not getattr(input_data, "pressed", False):
            return

        if self.current_player >= len(self.personapas):
            return  # ya todos seleccionaron (por seguridad)

        if not self.available_indices:
            return  # no quedan sombreros disponibles (por seguridad)

        if input_id.endswith("_left"):
            self.hat_cursor = (self.hat_cursor - 1) % len(self.available_indices)

        elif input_id.endswith("_right"):
            self.hat_cursor = (self.hat_cursor + 1) % len(self.available_indices)

        elif input_id.endswith("_main"):
            chosen_hat_index = self.available_indices[self.hat_cursor]

            self.personapas[self.current_player].hat_index = chosen_hat_index
            self.available_indices.remove(chosen_hat_index)

            self.current_player += 1
            self.hat_cursor = 0  # empezar desde el primero disponible para el siguiente

            if self.current_player >= len(self.personapas):
                self._proceed_to_parkour()

    def _proceed_to_parkour(self) -> None:
        """Pasar a ParkourState después de que todos seleccionen."""
        self.state_machine.change(
            "parkour",
            play_state=self.play_state,
            personapas=self.personapas
        )

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        """Renderizar la pantalla de selección."""
        surface.fill("black")

        title_text = self._title_font.render("Selecciona tu Sombrero", True, "white")
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, 40))
        surface.blit(title_text, title_rect)

        player_text = self._text_font.render(f"Jugador {self.current_player + 1}", True, "yellow")
        player_rect = player_text.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(player_text, player_rect)

        self._render_hat_carousel(surface)

        controls_text = self._small_font.render(
            "Izquierda/Derecha: Navegar | Botón principal: Seleccionar", True, "white"
        )
        controls_rect = controls_text.get_rect(center=(surface.get_width() // 2, surface.get_height() - 40))
        surface.blit(controls_text, controls_rect)

    def _render_hat_carousel(self, surface: pygame.Surface) -> None:
        """Renderizar carrusel con solo los sombreros TODAVÍA disponibles."""

        hat_size = 82
        spacing = 110
        visible_hats = 5

        if not self.available_indices:
            return  # nada que mostrar (no debería pasar)

        num_available = len(self.available_indices)
        start_pos = max(0, self.hat_cursor - visible_hats // 2)
        start_pos = min(start_pos, max(0, num_available - visible_hats))

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        for i in range(min(visible_hats, num_available - start_pos)):
            list_pos = start_pos + i
            hat_idx = self.available_indices[list_pos]  # índice real del sombrero

            offset = (i - visible_hats // 2) * spacing
            x = center_x + offset
            y = center_y

            preview = self.hat_previews[hat_idx]
            scaled = pygame.transform.scale(preview, (hat_size, hat_size))

            if list_pos == self.hat_cursor:
                rect = scaled.get_rect(center=(x, y))
                surface.blit(scaled, rect)
                pygame.draw.rect(surface, "yellow", rect, 3)

                name_text = self._text_font.render(self.hat_sprites.get_hat_name(hat_idx), True, "yellow")
                name_rect = name_text.get_rect(center=(x, y + hat_size // 2 + 30))
                surface.blit(name_text, name_rect)
            else:
                rect = scaled.get_rect(center=(x, y))
                surface.blit(scaled, rect)