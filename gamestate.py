from enum import Enum

class game_state(Enum):
    """Game states used by the game. Members use PascalCase as requested."""
    Menu = "menu"
    Playing = "playing"
    Paused = "paused"
    GameOver = "gameover"