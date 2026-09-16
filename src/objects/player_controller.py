"""ControladorDelJugador: recibe los inputs asociados a un jugador
particular y activa las intenciones correspondientes en su objeto
poseído (Personapa o Cursor, según la fase)."""

from typing import Optional
from gale.input_handler import InputData, apply_deadzone
from gale.command import Command, CommandBindings

class MoveRightCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x += 1
        
class StopMoveRightCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x -= 1

        
class MoveDownCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_down_intent = True
        
class StopMoveDownCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_down_intent = False

        
class MoveLeftCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_left_intent = True
        
class StopMoveLeftCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_left_intent = False

        
class MoveUpCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_up_intent = True
        
class StopMoveUpCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_up_intent = False
        
        
        
class MoveVectorRightCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x = 0 if receiver.move_intent.x < -0.01 else 1 

class MoveVectorLeftCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.x = 0 if receiver.move_intent.x > 0.01 else -1

class MoveVectorUpCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.y = 0 if receiver.move_intent.y > 0.01 else -1

class MoveVectorDownCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.move_intent.y = 0 if receiver.move_intent.y < -0.01 else 1



class MainActionCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.main_action_intent = True
        
class StopMainActionCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.main_action_intent = False



class SecondaryActionCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.secondary_action_intent = True
        
class StopSecondaryActionCommand (Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.secondary_action_intent = False        
        
MOVEC_L = MoveVectorLeftCommand()
MOVEC_R = MoveVectorRightCommand()
MOVEC_U = MoveVectorUpCommand()
MOVEC_D = MoveVectorDownCommand()
MAIN = MainActionCommand()
STOP_MAIN = StopMainActionCommand()
SECONDARY  = SecondaryActionCommand()
STOP_SECONDARY  = StopSecondaryActionCommand()

class PlayerController:
    def __init__(self, params :dict) -> None:
        self.device = params["device"]
        self.gamepad_id = params.get("gamepad_id", -1)
        self.possessed_entity: any = None
        
        self.command_bindings = CommandBindings()
        
        if self.device == "keyboard":
            self.command_bindings.bind(params["left"], press=MOVEC_L, release=MOVEC_R)
            self.command_bindings.bind(params["right"], press=MOVEC_R, release=MOVEC_L)
            self.command_bindings.bind(params["up"], press=MOVEC_U, release=MOVEC_D)
            self.command_bindings.bind(params["down"], press=MOVEC_D, release=MOVEC_U)
        
        self.command_bindings.bind(params["main_action"], press=MAIN, release=STOP_MAIN)
        self.command_bindings.bind(params["secondary_action"], press=SECONDARY, release=STOP_SECONDARY)
            
    def on_input(self, input_id: str, input_data: InputData):
        if self.possessed_entity == None:
            return        
        print("input")
        if self.device == "gamepad":
            print(input_data.get_action_name())
            if (
                input_data.get_action_name() == "gamepad_axis"
                or input_data.get_action_name() == "gamepad_button"
            ):
                if not self.gamepad_id == input_data.gamepad_id:
                    return
            else:
                return

        self.command_bindings.dispatch(self.possessed_entity, input_id, input_data)
        
        if input_id == "axis_x":
            self.possessed_entity.move_intent.x = apply_deadzone(input_data.value)

        if input_id == "axis_y":
            self.possessed_entity.move_intent.y = apply_deadzone(input_data.value)
