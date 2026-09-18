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
        
        self.player_count = 4
        self.rounds = 0
        self.max_rounds = int(2*self.player_count)
        self.target_score = int(3*self.player_count)
        self.scores = [0 for _ in range(self.player_count)]

    def enter(self, **kwargs) -> None:
        super().enter(**kwargs)  # obligatorio: activa el substate inicial
        self.substate_machine.change("parkour", play_state=self)
