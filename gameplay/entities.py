from dataclasses import dataclass, field
from typing import Optional
from collections import deque

from config.settings import Direction, EntityState, GameConfig
from core.animation import AnimationController, SpriteFactory

@dataclass
class GridEntity:
    grid_x: int
    grid_y: int
    pixel_x: float
    pixel_y: float
    state: EntityState = EntityState.IDLE
    animation_controller: Optional[AnimationController] = None
    
    def grid_pos(self):
        return self.grid_x, self.grid_y
    
    def pixel_pos(self):
        return self.pixel_x, self.pixel_y
    
    def update_pixel_pos(self):
        self.pixel_x = self.grid_x * GameConfig.TILE_WIDTH
        self.pixel_y = self.grid_y * GameConfig.TILE_HEIGHT

@dataclass
class Player(GridEntity):
    direction: Direction = Direction.IDLE
    move_queue: deque = field(default_factory=deque)
    bomb_count: int = 1
    max_bombs: int = 1
    blast_radius: int = 2
    is_moving: bool = False
    move_progress: float = 0.0
    target_x: int = 0
    target_y: int = 0
    can_place_bomb: bool = True
    
    def __post_init__(self):
        if self.pixel_x == 0 and self.pixel_y == 0:
            self.update_pixel_pos()
        self.animation_controller = SpriteFactory.create_player_animations()

@dataclass
class Bomb(GridEntity):
    timer: float = GameConfig.BOMB_TIMER
    blast_radius: int = 2
    owner: Optional[Player] = None
    
    def __post_init__(self):
        self.animation_controller = SpriteFactory.create_bomb_animations()
        self.update_pixel_pos()

@dataclass
class Explosion(GridEntity):
    duration: float = GameConfig.EXPLOSION_DURATION
    
    def __post_init__(self):
        self.animation_controller = SpriteFactory.create_explosion_animations()
        self.update_pixel_pos()

@dataclass
class PowerUp(GridEntity):
    power_type: str = "bomb_count"
    is_revealed: bool = False
    
    def __post_init__(self):
        self.update_pixel_pos()

@dataclass
class Enemy(GridEntity):
    move_timer: float = 0.0
    move_interval: float = 0.4
    direction: Direction = Direction.DOWN
    ai_mode: str = "patrol"
    chase_distance: int = 6
    stuck_counter: int = 0
    
    def __post_init__(self):
        self.animation_controller = SpriteFactory.create_enemy_animations()
        self.update_pixel_pos()

@dataclass
class Home(GridEntity):
    is_revealed: bool = False
    
    def __post_init__(self):
        self.update_pixel_pos()
