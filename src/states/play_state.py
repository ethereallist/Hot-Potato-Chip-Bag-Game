"""PlayState: estado de partida. Usa HierarchicalState de Gale para
componer los 3 subestados del diagrama (ConstructionState -> ParkourState
-> ScoreState -> nueva ronda).

IMPORTANTE: HierarchicalState ya delega enter/on_input/update/render al
substate activo automáticamente. Si sobreescribimos alguno de esos
métodos, hay que llamar a super().<metodo>(...) o el substate deja de
recibir esas llamadas.
"""

import pygame

from gale.state import HierarchicalState, StateMachine

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
            },
            initial_substate="parkour",
        )

    def enter(self, **kwargs) -> None:
        super().enter(**kwargs)  # obligatorio: activa el substate inicial
