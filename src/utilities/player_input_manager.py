"""Archivo con funciones de utilidades respecto a los inputs de los jugadores"""

from src.objects.player_controller import PlayerController
from gale.input_handler import InputData
  
class PlayerTracker:
    registered_players = [] #(int, PlayerControler) pairs, the int is the player's id
    
    @classmethod
    def clear(cls):
        cls.clear_possessed()
        registered_players = []
    
    @classmethod
    def is_unregistered_player(cls, input_name: str) -> bool:
        player = cls.get_player_id_from_input(input_name)
        for p in cls.registered_players:
            if player == p[0]:
                return False
        return True
    
    @classmethod
    def make_keyboard_player_controller(cls, player: int) -> PlayerController:
        p_c = PlayerController(
            cls.get_player_keyboard_inputs(player)
        )
        cls.registered_players.append((player, p_c))
        return p_c
    
    @classmethod    
    def get_player_controllers(cls, player: int) -> list[PlayerController]:
        controllers = []
        for i, p_c in cls.registered_players:
            controllers.append(p_c)
        return controllers
        
    @classmethod
    def get_player_controller_by_id(cls, player: int):
        for i in range(len(cls.registered_players)):
            if player == cls.registered_players[i][0]:
                return cls.registered_players[i][1]
        return None
    
    @classmethod
    def get_player_count(cls) -> int:
        return len(cls.registered_players)
       
    @classmethod
    def get_player_keyboard_inputs(cls, player: int) -> dict:
        d = {
            "device" : "keyboard",
            "left" : f"p{player}_left",
            "right" : f"p{player}_right",
            "up" : f"p{player}_up",
            "down" : f"p{player}_down",
            "main_action" : f"p{player}_main_action",
            "secondary_action" : f"p{player}_secondary_action",
        }
        return d
        
    @classmethod
    def get_player_id_from_input(cls, input_name: str) -> int:
        return int(input_name[1])
    
    @classmethod
    def process_inputs(cls, input_id: str, input_data: InputData) -> None:
        for i, p_c in cls.registered_players:
            p_c.on_input(input_id, input_data)
    
    @classmethod
    def clear_possessed(cls) -> None:
        for i, p_c in cls.registered_players:
            p_c.possessed = None