"""PlayState: estado de partida. Usa HierarchicalState de Gale para
componer los 3 subestados del diagrama (ConstructionState -> ParkourState
-> ScoreState -> nueva ronda), y mantiene los datos persistentes entre
ellos (controladores, temporizador, apariencias, datos del mapa, puntaje,
contador de rondas)."""

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

        # TODO: datos persistentes a través de las 3 fases
        self.controladores_del_jugador = []  # list[ControladorDelJugador]
        self.temporizador = None
        self.apariencias_de_las_personapas = []
        self.datos_del_mapa = None  # Grid2D (tipo de casilla + índices de objetos)
        self.puntaje = []  # list[int], uno por jugador
        self.contador_de_rondas: int = 0

    def enter(self, **kwargs) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def transition_to_substate(self, next_substate: str) -> None:
        pass

    def check_win_condition(self) -> bool:
        pass
