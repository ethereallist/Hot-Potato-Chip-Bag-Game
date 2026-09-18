"""PlayState: estado de partida. Usa HierarchicalState de Gale para
componer los 3 subestados del diagrama (ConstructionState -> ParkourState
-> ScoreState -> nueva ronda).

IMPORTANTE: HierarchicalState ya delega enter/on_input/update/render al
substate activo automáticamente. Si sobreescribimos alguno de esos
métodos, hay que llamar a super().<metodo>(...) o el substate deja de
recibir esas llamadas.
"""

import pygame

from gale.state import HierarchicalState, BaseState, StateMachine

from src.states.play.construction_state import ConstructionState
from src.states.play.parkour_state import ParkourState
from src.states.play.score_state import ScoreState


class PlayState(HierarchicalState):
    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(
            state_machine,
            substates={
                "construction": ConstructionState,
                "parkour": ParkourState,
                "score": ScoreState,
                "base": BaseState,
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
        
        self.substate_machine.change("parkour", play_state=self)
        
    def are_rounds_over(self) -> bool:
        return self.rounds >= self.max_rounds
        
    def check_winner(self) -> int:
        for i in range(self.player_count):
            if self.scores[i] >= self.target_score:
                return i
        
        return -1
        
    def return_to_menu(self):
        self.state_machine.change("menu")
        
