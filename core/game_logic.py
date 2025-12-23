import random
from typing import List, Dict, Tuple, Optional, Set
from collections import deque

from config.settings import TileType, Direction, EntityState, GameConfig, GameDifficulty
from gameplay.entities import Player, Bomb, Explosion, PowerUp, Enemy, Home
from core.animation import SpriteFactory

class Tilemap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[TileType]] = [
            [TileType.FLOOR for _ in range(width)] for _ in range(height)
        ]
        self._generate_default_map()
    
    def _generate_default_map(self):
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = TileType.FLOOR
        
        for x in range(self.width):
            self.tiles[0][x] = TileType.WALL
            self.tiles[self.height - 1][x] = TileType.WALL
        for y in range(self.height):
            self.tiles[y][0] = TileType.WALL
            self.tiles[y][self.width - 1] = TileType.WALL
        
        for y in range(2, self.height - 1, 2):
            for x in range(2, self.width - 1, 2):
                self.tiles[y][x] = TileType.WALL
        
        spawn_area = [(1, 1), (2, 1), (1, 2)]
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.tiles[y][x] == TileType.FLOOR:
                    if (x, y) not in spawn_area:
                        if random.random() < 0.6:
                            self.tiles[y][x] = TileType.DESTRUCTIBLE
    
    def is_walkable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.tiles[y][x] == TileType.FLOOR
    
    def destroy_tile(self, x: int, y: int):
        if self.tiles[y][x] == TileType.DESTRUCTIBLE:
            self.tiles[y][x] = TileType.FLOOR

class GamePhysics:
    @staticmethod
    def can_move(player: Player, tilemap: Tilemap, 
                 bombs: List[Bomb]) -> bool:
        next_x = player.target_x
        next_y = player.target_y
        
        if not tilemap.is_walkable(next_x, next_y):
            return False
        
        for bomb in bombs:
            if bomb.grid_x == next_x and bomb.grid_y == next_y:
                return False
        
        return True
    
    @staticmethod
    def get_blast_tiles(center_x: int, center_y: int, radius: int, 
                       tilemap: Tilemap) -> Set[Tuple[int, int]]:
        affected = {(center_x, center_y)}
        
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            dx, dy = direction.value
            for i in range(1, radius + 1):
                x, y = center_x + dx * i, center_y + dy * i
                
                if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                    break
                if tilemap.tiles[y][x] == TileType.WALL:
                    break
                
                affected.add((x, y))
                if tilemap.tiles[y][x] == TileType.DESTRUCTIBLE:
                    break
        
        return affected

class GameEvents:
    def __init__(self):
        self.listeners: Dict[str, List] = {}
    
    def subscribe(self, event_type: str, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit(self, event_type: str, data: dict = None):
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(data or {})

class GameState:
    def __init__(self, config: GameConfig = GameConfig(), level: int = 1, difficulty: GameDifficulty = GameDifficulty.NORMAL, initial_score: int = 0, player_stats: Optional[Dict] = None):
        self.config = config
        self.level = level
        self.difficulty = difficulty
        self.score = initial_score
        self.game_over = False
        self.level_complete = False
        
        self.tilemap = Tilemap(config.GRID_SIZE, config.GRID_SIZE)
        
        if player_stats:
            max_bombs = player_stats.get("max_bombs", 1)
            blast_radius = player_stats.get("blast_radius", 2)
            self.player = Player(
                grid_x=1, grid_y=1, pixel_x=0.0, pixel_y=0.0,
                max_bombs=max_bombs,
                bomb_count=max_bombs,  # Refill bombs
                blast_radius=blast_radius
            )
        else:
            self.player = Player(grid_x=1, grid_y=1, pixel_x=0.0, pixel_y=0.0)

        self.bombs: List[Bomb] = []
        self.explosions: List[Explosion] = []
        self.power_ups: List[PowerUp] = []
        self.enemies: List[Enemy] = []
        self.home: Optional[Home] = None
        self.events = GameEvents()
        
        self._generate_power_ups()
        self._spawn_home()
        self._spawn_enemies()
        
        self.events.subscribe("bomb_placed", self._on_bomb_placed)
        self.events.subscribe("explosion", self._on_explosion)
    
    def _generate_power_ups(self):
        power_types = ["bomb_count", "blast_radius", "speed"]
        
        for y in range(1, self.config.GRID_SIZE - 1):
            for x in range(1, self.config.GRID_SIZE - 1):
                if self.tilemap.tiles[y][x] == TileType.DESTRUCTIBLE:
                    if random.random() < 0.15:
                        pu = PowerUp(
                            grid_x=x, grid_y=y, pixel_x=0.0, pixel_y=0.0,
                            power_type=random.choice(power_types)
                        )
                        self.power_ups.append(pu)
    
    def _spawn_home(self):
        home_x = self.config.GRID_SIZE - 2
        home_y = self.config.GRID_SIZE - 2
        self.home = Home(grid_x=home_x, grid_y=home_y, pixel_x=0.0, pixel_y=0.0)
    
    def _spawn_enemies(self):
        # Define difficulty parameters
        diff_params = {
            GameDifficulty.EASY: {"base": 3, "speed": 0.5},
            GameDifficulty.NORMAL: {"base": 4, "speed": 0.4},
            GameDifficulty.HARD: {"base": 6, "speed": 0.3},
            GameDifficulty.NIGHTMARE: {"base": 8, "speed": 0.2},
        }
        params = diff_params.get(self.difficulty, diff_params[GameDifficulty.NORMAL])
        
        # Calculate number of enemies
        num_enemies = min(params["base"] + (self.level - 1), 12)
        
        # Generate potential spawn points (all floor tiles except near player)
        spawn_candidates = []
        for y in range(1, self.config.GRID_SIZE - 1):
            for x in range(1, self.config.GRID_SIZE - 1):
                # Skip safe zone around player (1,1)
                if x <= 3 and y <= 3:
                    continue
                if self.tilemap.is_walkable(x, y):
                    spawn_candidates.append((x, y))
        
        if not spawn_candidates:
            return

        # Select spawn points
        selected_points = random.sample(spawn_candidates, min(num_enemies, len(spawn_candidates)))
        
        for x, y in selected_points:
            enemy = Enemy(
                grid_x=x, grid_y=y, pixel_x=0.0, pixel_y=0.0,
                direction=random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]),
                move_interval=params["speed"]
            )
            self.enemies.append(enemy)
    
    def _on_bomb_placed(self, data):
        self.score += 10
        self.events.emit("ui_update", {"score": self.score})
    
    def _on_explosion(self, data):
        self.score += 50
    
    def update(self, dt: float):
        self._update_player(dt)
        self._update_bombs(dt)
        self._update_explosions(dt)
        self._update_enemies(dt)
        self._check_collisions()
        self._check_power_up_collection()
    
    def _update_player(self, dt: float):
        if self.player.is_moving:
            self.player.move_progress += (self.config.MOVE_SPEED / self.config.TILE_WIDTH)
            
            if self.player.move_progress >= 1.0:
                self.player.grid_x = self.player.target_x
                self.player.grid_y = self.player.target_y
                self.player.is_moving = False
                self.player.move_progress = 0.0
                self.player.update_pixel_pos()
                self.player.state = EntityState.IDLE
            else:
                self.player.pixel_x = (self.player.grid_x + 
                    (self.player.target_x - self.player.grid_x) * self.player.move_progress
                ) * self.config.TILE_WIDTH
                self.player.pixel_y = (self.player.grid_y + 
                    (self.player.target_y - self.player.grid_y) * self.player.move_progress
                ) * self.config.TILE_HEIGHT
        
        if self.player.animation_controller:
            self.player.animation_controller.update(dt)
    
    def _update_bombs(self, dt: float):
        for bomb in self.bombs[:]:
            bomb.timer -= dt
            if bomb.timer <= 0:
                self._detonate_bomb(bomb)
            if bomb.animation_controller:
                bomb.animation_controller.update(dt)
    
    def _update_explosions(self, dt: float):
        for exp in self.explosions[:]:
            exp.duration -= dt
            if exp.duration <= 0:
                self.explosions.remove(exp)
            elif exp.animation_controller:
                exp.animation_controller.update(dt)
    
    def _update_enemies(self, dt: float):
        for enemy in self.enemies:
            enemy.move_timer += dt
            
            if enemy.move_timer >= enemy.move_interval:
                enemy.move_timer = 0.0
                
                dx = self.player.grid_x - enemy.grid_x
                dy = self.player.grid_y - enemy.grid_y
                dist = abs(dx) + abs(dy)
                
                if dist < enemy.chase_distance:
                    if abs(dx) > abs(dy):
                        enemy.direction = Direction.LEFT if dx < 0 else Direction.RIGHT
                    else:
                        enemy.direction = Direction.UP if dy < 0 else Direction.DOWN
                
                next_x = enemy.grid_x + enemy.direction.value[0]
                next_y = enemy.grid_y + enemy.direction.value[1]
                
                can_move = False
                if self.tilemap.is_walkable(next_x, next_y):
                    bomb_at_pos = any(b.grid_x == next_x and b.grid_y == next_y for b in self.bombs)
                    if not bomb_at_pos:
                        can_move = True
                        enemy.stuck_counter = 0
                
                if can_move:
                    enemy.grid_x = next_x
                    enemy.grid_y = next_y
                    enemy.update_pixel_pos()
                else:
                    enemy.stuck_counter += 1
                    if enemy.stuck_counter >= 2:
                        enemy.stuck_counter = 0
                        valid_directions = []
                        for test_dir in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
                            test_x = enemy.grid_x + test_dir.value[0]
                            test_y = enemy.grid_y + test_dir.value[1]
                            if self.tilemap.is_walkable(test_x, test_y):
                                bomb_at_pos = any(b.grid_x == test_x and b.grid_y == test_y for b in self.bombs)
                                if not bomb_at_pos:
                                    valid_directions.append(test_dir)
                        
                        if valid_directions:
                            enemy.direction = random.choice(valid_directions)
                
                dir_name = {
                    Direction.UP: 0, Direction.DOWN: 1,
                    Direction.LEFT: 2, Direction.RIGHT: 3
                }.get(enemy.direction, 1)
                if enemy.animation_controller:
                    enemy.animation_controller.set_state(f"walk_{dir_name}")
            
            if enemy.animation_controller:
                enemy.animation_controller.update(dt)
    
    def _detonate_bomb(self, bomb: Bomb):
        blast_tiles = GamePhysics.get_blast_tiles(
            bomb.grid_x, bomb.grid_y, bomb.blast_radius, self.tilemap
        )
        
        for x, y in blast_tiles:
            self.explosions.append(Explosion(grid_x=x, grid_y=y, pixel_x=0.0, pixel_y=0.0))
            self.tilemap.destroy_tile(x, y)
            
            for pu in self.power_ups:
                if pu.grid_x == x and pu.grid_y == y:
                    pu.is_revealed = True
        
        self.bombs.remove(bomb)
        if bomb.owner:
            bomb.owner.bomb_count += 1
        
        for other_bomb in self.bombs[:]:
            if (other_bomb.grid_x, other_bomb.grid_y) in blast_tiles:
                other_bomb.timer = 0
        
        self.events.emit("explosion", {"tiles": list(blast_tiles)})
    
    def _check_collisions(self):
        for exp in self.explosions:
            if self.player.grid_x == exp.grid_x and self.player.grid_y == exp.grid_y:
                self.player.state = EntityState.DEAD
                self.game_over = True
                self.events.emit("player_dead", {})
        
        for enemy in self.enemies:
            if self.player.grid_x == enemy.grid_x and self.player.grid_y == enemy.grid_y:
                self.player.state = EntityState.DEAD
                self.game_over = True
                self.events.emit("player_dead", {})
        
        for enemy in self.enemies[:]:
            for exp in self.explosions:
                if enemy.grid_x == exp.grid_x and enemy.grid_y == exp.grid_y:
                    self.enemies.remove(enemy)
                    self.score += 200
                    self.events.emit("enemy_killed", {"score": 200})
                    break
        
        if len(self.enemies) == 0 and self.home:
            self.home.is_revealed = True
        
        if self.home and self.home.is_revealed:
            if self.player.grid_x == self.home.grid_x and self.player.grid_y == self.home.grid_y:
                self.level_complete = True
                self.events.emit("level_complete", {"level": self.level})
    
    def _check_power_up_collection(self):
        for pu in self.power_ups[:]:
            if self.player.grid_x == pu.grid_x and self.player.grid_y == pu.grid_y:
                self._apply_power_up(pu)
                self.power_ups.remove(pu)
    
    def _apply_power_up(self, pu: PowerUp):
        if pu.power_type == "bomb_count":
            self.player.max_bombs += 1
            self.player.bomb_count += 1
            self.score += 100
        elif pu.power_type == "blast_radius":
            self.player.blast_radius += 1
            self.score += 100
        elif pu.power_type == "speed":
            self.score += 50
        
        self.events.emit("power_up_collected", {"type": pu.power_type})
    
    def place_bomb(self):
        if (not self.player.can_place_bomb or 
            self.player.bomb_count <= 0 or
            any(b.grid_x == self.player.grid_x and b.grid_y == self.player.grid_y 
                for b in self.bombs)):
            return
        
        bomb = Bomb(grid_x=self.player.grid_x, grid_y=self.player.grid_y, 
                   pixel_x=0.0, pixel_y=0.0,
                   blast_radius=self.player.blast_radius, owner=self.player)
        self.bombs.append(bomb)
        self.player.bomb_count -= 1
        self.player.state = EntityState.PLACING_BOMB
        self.events.emit("bomb_placed", {"pos": (self.player.grid_x, self.player.grid_y)})
    
    def try_move(self, direction: Direction):
        if self.player.is_moving:
            self.player.move_queue.append(direction)
            return
        
        next_x = self.player.grid_x + direction.value[0]
        next_y = self.player.grid_y + direction.value[1]
        
        self.player.target_x = next_x
        self.player.target_y = next_y
        
        if GamePhysics.can_move(self.player, self.tilemap, self.bombs):
            self.player.is_moving = True
            self.player.state = EntityState.WALKING
            self.player.direction = direction
            
            dir_map = {Direction.UP: 0, Direction.DOWN: 1, Direction.LEFT: 2, Direction.RIGHT: 3}
            dir_idx = dir_map.get(direction, 1)
            self.player.animation_controller.set_state(f"walk_{dir_idx}")
