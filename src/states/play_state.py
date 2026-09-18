"""PlayState: estado de partida. Usa HierarchicalState de Gale para
componer los subestados (ParkourState -> ScoreState -> nueva ronda).

La selección de sombreros YA NO pasa por aquí: ahora ocurre dentro de
MenuState, encima del propio menú (papas + botones), antes de llamar
a state_machine.change("play", ...). Las personapas que llegan aquí
ya traen su hat_index asignado.

IMPORTANTE: HierarchicalState ya delega enter/on_input/update/render al
substate activo automáticamente. Si sobreescribimos alguno de esos
métodos, hay que llamar a super().<metodo>(...) o el substate deja de
recibir esas llamadas.
"""

import pygame

from gale.state import HierarchicalState, BaseState, StateMachine

from src.states.play.parkour_state import ParkourState
from src.states.play.score_state import ScoreState
from src.states.win_state import WinState


class PlayState(HierarchicalState):
    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(
            state_machine,
            substates={
                "parkour": ParkourState,
                "score": ScoreState,
                "base": BaseState,
                "win": WinState,

            },
            initial_substate = "base"
        )

    def enter(self, **kwargs) -> None:
        super().enter(**kwargs)  # obligatorio: activa el substate inicial
        
        self.player_count = kwargs.get("player_count", 4) #it should be 2 as minimum
        self.rounds = 0
        self.max_rounds = int(3 + 2 * (self.player_count - 1))
        self.target_score = int(3 + 1.5 * (self.player_count - 2))
        self.scores = [0 for _ in range(self.player_count)]
        
        # se reenvía personapas (ya con su sombrero elegido en el menú)
        # junto con play_state, si no, change() solo pasaba play_state y
        # se perdía lo demás
        self.substate_machine.change("parkour", play_state=self, personapas=kwargs.get("personapas"))
        
    def are_rounds_over(self) -> bool:
        return self.rounds >= self.max_rounds
        
    def check_winner(self) -> int:
        # Verificamos si ya jugamos 3 rondas
        if self.rounds >= 3:
            # Buscamos cuál es el puntaje más alto
            max_score = max(self.scores)
            # Devolvemos el índice del jugador que tiene ese puntaje
            winner_index = self.scores.index(max_score)
            return winner_index
        
        # Si llevamos menos de 3 rondas, devolvemos -1 (aún no hay ganador)
        return -1
        
    def return_to_menu(self):
        self.state_machine.change("menu")