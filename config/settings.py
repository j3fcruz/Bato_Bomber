import json
from enum import Enum
from dataclasses import dataclass
from security.encryption import encrypt_data, decrypt_data

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    IDLE = (0, 0)

class TileType(Enum):
    FLOOR = 0
    WALL = 1
    DESTRUCTIBLE = 2
    SPAWN = 3

class EntityState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    PLACING_BOMB = "placing_bomb"
    DAMAGED = "damaged"
    DEAD = "dead"

class MenuState(Enum):
    MAIN = "main"
    OPTIONS = "options"
    DIFFICULTY = "difficulty"
    CREDITS = "credits"
    LEADERBOARD = "leaderboard"
    NAME_INPUT = "name_input"
    GAME = "game"
    PAUSED = "paused"

class GameDifficulty(Enum):
    EASY = 1.0
    NORMAL = 1.0
    HARD = 1.5
    NIGHTMARE = 2.0

@dataclass
class GameSettings:
    """Game settings management"""
    difficulty: GameDifficulty = GameDifficulty.NORMAL
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    screen_shake: bool = True
    
    def save(self):
        """Save settings to file"""
        try:
            settings_json = json.dumps({
                "difficulty": self.difficulty.name,
                "music_volume": self.music_volume,
                "sfx_volume": self.sfx_volume,
                "screen_shake": self.screen_shake
            })
            encrypted_settings = encrypt_data(settings_json)
            with open("settings.json", "wb") as f:
                f.write(encrypted_settings)
        except:
            pass
    
    @staticmethod
    def load():
        """Load settings from file"""
        try:
            with open("settings.json", "rb") as f:
                encrypted_data = f.read()
            decrypted_json = decrypt_data(encrypted_data)
            data = json.loads(decrypted_json)
            return GameSettings(
                difficulty=GameDifficulty[data.get("difficulty", "NORMAL")],
                music_volume=data.get("music_volume", 0.7),
                sfx_volume=data.get("sfx_volume", 0.8),
                screen_shake=data.get("screen_shake", True)
            )
        except:
            return GameSettings()

class GameConfig:
    GRID_SIZE = 13
    TILE_WIDTH = 48  # Changed from 32 to 48
    TILE_HEIGHT = 48 # Changed from 32 to 48
    WINDOW_WIDTH = 624 # Changed from 416 to 624 (13 * 48)
    WINDOW_HEIGHT = 624 # Changed from 416 to 624 (13 * 48)
    FPS = 60
    ANIMATION_FPS = 8
    MOVE_SPEED = 4.0
    BOMB_TIMER = 3.0
    EXPLOSION_DURATION = 0.5
    MAX_LEVELS = 5
