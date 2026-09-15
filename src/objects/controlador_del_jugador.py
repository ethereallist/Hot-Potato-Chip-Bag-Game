"""ControladorDelJugador: recibe los inputs asociados a un jugador
particular y activa las intenciones correspondientes en su objeto
poseído (Personapa o Cursor, según la fase)."""


class ControladorDelJugador:
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id

    def get_input(self):
        pass
