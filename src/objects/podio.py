"""Podio: representa a un jugador sobre su pedestal de puntaje durante
ScoreState."""


class Podio:
    def __init__(self) -> None:
        self.altura: float = 0.0
        self.personapa_ref = None  # Personapa

    def grow(self) -> None:
        pass
