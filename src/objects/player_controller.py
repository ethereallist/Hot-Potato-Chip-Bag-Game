"""PlayerController: recibe los inputs asociados a un jugador particular
y activa las intenciones correspondientes en su objeto poseído
(Personapa o Cursor, según la fase)."""

from gale.input_handler import InputData, apply_deadzone
from gale.command import Command, CommandBindings


class MoveVectorRightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x += 1


class MoveVectorLeftCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x -= 1


class MoveVectorUpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.y -= 1


class MoveVectorDownCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.y += 1


class MainActionCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.main_action_intent = True


class StopMainActionCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.main_action_intent = False


class SecondaryActionCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.secondary_action_intent = True


class StopSecondaryActionCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.secondary_action_intent = False


MOVEC_L = MoveVectorLeftCommand()
MOVEC_R = MoveVectorRightCommand()
MOVEC_U = MoveVectorUpCommand()
MOVEC_D = MoveVectorDownCommand()
MAIN = MainActionCommand()
STOP_MAIN = StopMainActionCommand()
SECONDARY = SecondaryActionCommand()
STOP_SECONDARY = StopSecondaryActionCommand()


class PlayerController:
    def __init__(self, params: dict) -> None:
        self.device = params["device"]
        self.gamepad_id = params.get("gamepad_id", -1)
        self.possessed_entity = None

        self.command_bindings = CommandBindings()

        if self.device in ("keyboard", "gamepad"):
            # el D-pad de un mando se reporta como botones (press/release),
            # igual que las teclas, así que se bindea de la misma forma
            self.command_bindings.bind(params["left"], press=MOVEC_L, release=MOVEC_R)
            self.command_bindings.bind(params["right"], press=MOVEC_R, release=MOVEC_L)
            self.command_bindings.bind(params["up"], press=MOVEC_U, release=MOVEC_D)
            self.command_bindings.bind(params["down"], press=MOVEC_D, release=MOVEC_U)

        self.command_bindings.bind(params["main_action"], press=MAIN, release=STOP_MAIN)
        self.command_bindings.bind(params["secondary_action"], press=SECONDARY, release=STOP_SECONDARY)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.possessed_entity is None:
            return

        if self.device == "gamepad":
            if input_data.get_action_name() not in ("gamepad_axis", "gamepad_button"):
                return  # ignora eventos que no son de mando (teclado, mouse, etc.)
            if input_data.gamepad_id != self.gamepad_id:
                return

            if input_id == "axis_x":
                self.possessed_entity.move_intent.x = apply_deadzone(input_data.value)
            if input_id == "axis_y":
                self.possessed_entity.move_intent.y = apply_deadzone(input_data.value)

        self.command_bindings.dispatch(self.possessed_entity, input_id, input_data)