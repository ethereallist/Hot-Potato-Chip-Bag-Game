"""GamepadDirectController: lee un mando directamente con pygame
(pygame.joystick), sondeándolo cada frame en vez de depender del
sistema de eventos de Gale. Se usa porque confirmamos que la ruta de
eventos de Gale para el mando no estaba llegando de forma confiable,
mientras que el sondeo directo (igual que testerdemando.py) sí
funciona.
"""
 
import pygame
 
 
class GamepadDirectController:
    def __init__(
        self,
        joystick_index: int = 0,
        axis_x: int = 0,
        axis_y: int = 1,
        invert_y: bool = False,
        main_button: int = 0,
        secondary_button: int = 1,
        deadzone: float = 0.2,
    ) -> None:
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(joystick_index)
        self.joystick.init()
 
        self.axis_x = axis_x
        self.axis_y = axis_y
        self.invert_y = invert_y
        self.main_button = main_button
        self.secondary_button = secondary_button
        self.deadzone = deadzone
 
        self.possessed_entity = None
 
    def _apply_deadzone(self, value: float) -> float:
        return 0.0 if abs(value) <= self.deadzone else value
 
    def poll(self) -> None:
        """Llamar una vez por frame, en update(), ANTES de mover al
        personaje poseído."""
        if self.possessed_entity is None:
            return
 
        self.possessed_entity.move_intent.x = self._apply_deadzone(
            self.joystick.get_axis(self.axis_x)
        )
        y = self._apply_deadzone(self.joystick.get_axis(self.axis_y))
        self.possessed_entity.move_intent.y = -y if self.invert_y else y
        self.possessed_entity.main_action_intent = bool(
            self.joystick.get_button(self.main_button)
        )
        self.possessed_entity.secondary_action_intent = bool(
            self.joystick.get_button(self.secondary_button)
        )