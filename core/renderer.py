import pygame
import random
import os
from typing import List, Optional

from config.settings import GameConfig, TileType, GameSettings
from gameplay.entities import Player, Bomb, Explosion, PowerUp, Enemy, Home
from core.animation import SpriteFactory
from gameplay.leaderboard import Leaderboard
from core.game_logic import GameState

class GameRenderer:
    def __init__(self, width: int, height: int):
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Bato Bomber")
        
        # Load fonts
        try:
            self.font_large = pygame.font.SysFont("Bauhaus 93", 64)
            self.font_medium = pygame.font.SysFont("Bauhaus 93", 42)
            self.font_small = pygame.font.SysFont("Bauhaus 93", 32)
            self.font_tiny = pygame.font.SysFont("Bauhaus 93", 20)
        except:
            print("Warning: Bauhaus 93 font not found, falling back to default.")
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 42)
            self.font_small = pygame.font.Font(None, 32)
            self.font_tiny = pygame.font.Font(None, 20)

        self.tile_size = GameConfig.TILE_WIDTH
        
        # Screen shake attributes
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset = (0, 0)

        # Load background
        self.background_image = self._load_background()

    def _load_background(self):
        try:
            base_path = SpriteFactory._get_base_path()
            bg_path = os.path.join(base_path, "assets", "sprites", "menu_background.png")
            bg = pygame.image.load(bg_path).convert()
            return pygame.transform.scale(bg, (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        except Exception as e:
            print(f"Warning: Could not load menu background: {e}")
            return None

    def trigger_shake(self, duration=0.2, intensity=5):
        """Trigger the screen shake effect."""
        self.shake_duration = duration
        self.shake_intensity = intensity

    def render(self, state: GameState, dt: float):
        """Render the entire game state."""
        render_surface = pygame.Surface((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        render_surface.fill((20, 20, 30))

        self._render_tilemap(render_surface, state.tilemap)
        self._render_power_ups(render_surface, state.power_ups)
        self._render_home(render_surface, state.home)
        self._render_bombs(render_surface, state.bombs)
        self._render_explosions(render_surface, state.explosions)
        self._render_enemies(render_surface, state.enemies)
        self._render_player(render_surface, state.player)
        self._render_hud(render_surface, state)

        if self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_offset = (0, 0)
            else:
                self.shake_offset = (
                    random.randint(-self.shake_intensity, self.shake_intensity),
                    random.randint(-self.shake_intensity, self.shake_intensity)
                )
        
        self.surface.fill((20, 20, 30))
        self.surface.blit(render_surface, self.shake_offset)
        pygame.display.flip()

    def _render_tilemap(self, surface, tilemap):
        tiles_sprite = SpriteFactory.load_sprite("tiles.png")
        
        for y in range(tilemap.height):
            for x in range(tilemap.width):
                tile = tilemap.tiles[y][x]
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                  self.tile_size, self.tile_size)
                
                if tiles_sprite:
                    tile_index = {
                        TileType.FLOOR: 0,
                        TileType.WALL: 1,
                        TileType.DESTRUCTIBLE: 2,
                    }.get(tile, 0)
                    
                    source_rect = pygame.Rect(tile_index * self.tile_size, 0, 
                                            self.tile_size, self.tile_size)
                    surface.blit(tiles_sprite, rect, source_rect)
                else:
                    if tile == TileType.WALL:
                        pygame.draw.rect(surface, (80, 80, 80), rect)
                    elif tile == TileType.DESTRUCTIBLE:
                        pygame.draw.rect(surface, (180, 120, 60), rect)
                    else:
                        pygame.draw.rect(surface, (220, 220, 220), rect)
    
    def _render_player(self, surface, player: Player):
        player_sprite = SpriteFactory.load_sprite("player_blue.png")
        rect = pygame.Rect(int(player.pixel_x), int(player.pixel_y),
                          self.tile_size, self.tile_size)
        
        if player_sprite and player.animation_controller:
            frame_rect = player.animation_controller.get_current_frame()
            surface.blit(player_sprite, rect, frame_rect)
        else:
            pygame.draw.ellipse(surface, (100, 200, 255), rect)
            pygame.draw.circle(surface, (255, 255, 255), rect.center, 4)
    
    def _render_bombs(self, surface, bombs: List[Bomb]):
        bomb_sprite = SpriteFactory.load_sprite("bomb.png")
        
        for bomb in bombs:
            rect = pygame.Rect(int(bomb.pixel_x), int(bomb.pixel_y),
                              self.tile_size, self.tile_size)
            
            if bomb_sprite and bomb.animation_controller:
                frame_rect = bomb.animation_controller.get_current_frame()
                surface.blit(bomb_sprite, rect, frame_rect)
            else:
                pygame.draw.circle(surface, (50, 50, 50),
                                  rect.center, self.tile_size // 3)
            
            timer_text = f"{int(bomb.timer + 1)}"
            text = self.font_small.render(timer_text, True, (255, 255, 0))
            surface.blit(text, (rect.centerx - 5, rect.centery - 5))
    
    def _render_explosions(self, surface, explosions: List[Explosion]):
        explosion_sprite = SpriteFactory.load_sprite("explosion.png")
        
        for exp in explosions:
            rect = pygame.Rect(int(exp.pixel_x), int(exp.pixel_y),
                              self.tile_size, self.tile_size)
            
            if explosion_sprite and exp.animation_controller:
                frame_rect = exp.animation_controller.get_current_frame()
                surface.blit(explosion_sprite, rect, frame_rect)
            else:
                pygame.draw.rect(surface, (255, 200, 50), rect)
    
    def _render_power_ups(self, surface, power_ups: List[PowerUp]):
        powerups_sprite = SpriteFactory.load_sprite("powerups.png")
        
        for pu in power_ups:
            if not pu.is_revealed:
                continue
            
            rect = pygame.Rect(int(pu.pixel_x), int(pu.pixel_y), 
                              self.tile_size, self.tile_size)
            
            if powerups_sprite:
                pu_index = {
                    "bomb_count": 0,
                    "blast_radius": 1,
                    "speed": 2,
                }.get(pu.power_type, 0)
                
                source_rect = pygame.Rect(pu_index * self.tile_size, 0,
                                        self.tile_size, self.tile_size)
                surface.blit(powerups_sprite, rect, source_rect)
            else:
                pygame.draw.rect(surface, (255, 215, 0), rect)
    
    def _render_enemies(self, surface, enemies: List[Enemy]):
        enemy_sprite = SpriteFactory.load_sprite("enemy_red.png")
        
        for enemy in enemies:
            rect = pygame.Rect(int(enemy.pixel_x), int(enemy.pixel_y),
                              self.tile_size, self.tile_size)
            
            if enemy_sprite and enemy.animation_controller:
                frame_rect = enemy.animation_controller.get_current_frame()
                surface.blit(enemy_sprite, rect, frame_rect)
            else:
                pygame.draw.ellipse(surface, (255, 100, 100), rect)
                pygame.draw.circle(surface, (255, 255, 255), rect.center, 3)
    
    def _render_home(self, surface, home: Optional[Home]):
        if not home or not home.is_revealed:
            return
        
        tiles_sprite = SpriteFactory.load_sprite("tiles.png")
        rect = pygame.Rect(int(home.pixel_x), int(home.pixel_y), 
                          self.tile_size, self.tile_size)
        
        if tiles_sprite:
            source_rect = pygame.Rect(3 * self.tile_size, 0,
                                    self.tile_size, self.tile_size)
            surface.blit(tiles_sprite, rect, source_rect)
        else:
            pygame.draw.rect(surface, (100, 150, 255), rect)
            pygame.draw.rect(surface, (200, 255, 100), rect, 3)
    
    def _render_hud(self, surface, state: GameState):
        hud_y = GameConfig.WINDOW_HEIGHT - 25
        hud_texts = [
            f"Level: {state.level}",
            f"Score: {state.score}",
            f"Bombs: {state.player.bomb_count}/{state.player.max_bombs}",
            f"Enemies: {len(state.enemies)}",
        ]
        
        for i, text_str in enumerate(hud_texts):
            text = self.font_tiny.render(text_str, True, (255, 255, 150))
            surface.blit(text, (10 + i * 150, hud_y))

    def _draw_menu_background(self):
        if self.background_image:
            self.surface.blit(self.background_image, (0, 0))
        else:
            self.surface.fill((20, 20, 40))
    
    def render_main_menu(self, selected: int = 0):
        self._draw_menu_background()
        
        subtitle_y = 260
        menu_start_y = subtitle_y + 60
        
        subtitle = self.font_small.render("Political Satire Game", True, (255, 255, 150))
        subtitle_rect = subtitle.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, subtitle_y))
        self.surface.blit(subtitle, subtitle_rect)
        
        menu_items = ["Start Game", "Leaderboard", "Options", "Credits", "Exit"]
        item_height = 60
        
        for i, item in enumerate(menu_items):
            color = (0, 255, 100) if i == selected else (255, 255, 150)
            text = self.font_medium.render(item, True, color)
            text_rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, menu_start_y + i * item_height))
            
            if i == selected:
                shadow = self.font_medium.render(item, True, (0, 0, 0))
                shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
                self.surface.blit(shadow, shadow_rect)
            
            self.surface.blit(text, text_rect)
        
        pygame.display.flip()
    
    def render_options_menu(self, settings: GameSettings, selected: int = 0):
        self._draw_menu_background()
        
        title = self.font_large.render("OPTIONS", True, (0, 255, 255))
        title_rect = title.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 150))
        self.surface.blit(title, title_rect)
        
        options = [
            f"Difficulty: {settings.difficulty.name}",
            f"Music Volume: {int(settings.music_volume * 100)}%",
            f"SFX Volume: {int(settings.sfx_volume * 100)}%",
            f"Screen Shake: {'ON' if settings.screen_shake else 'OFF'}",
            "Back"
        ]
        
        item_y = 240
        item_height = 70
        
        for i, option in enumerate(options):
            color = (0, 255, 100) if i == selected else (255, 255, 150)
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, item_y + i * item_height))
            
            if i == selected:
                shadow = self.font_medium.render(option, True, (0, 0, 0))
                shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
                self.surface.blit(shadow, shadow_rect)
            
            self.surface.blit(text, text_rect)
        
        hint = self.font_tiny.render("Use UP/DOWN arrows, LEFT/RIGHT to adjust, SPACE to confirm", True, (255, 255, 150))
        hint_rect = hint.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT - 40))
        self.surface.blit(hint, hint_rect)
        
        pygame.display.flip()
    
    def render_difficulty_menu(self, selected: int = 0):
        self._draw_menu_background()
        
        title = self.font_large.render("DIFFICULTY", True, (0, 255, 255))
        title_rect = title.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 150))
        self.surface.blit(title, title_rect)
        
        difficulties = [
            ("EASY", "3 enemies per level"),
            ("NORMAL", "4 enemies per level"),
            ("HARD", "6 enemies, faster"),
            ("NIGHTMARE", "8 enemies, very fast")
        ]
        
        item_y = 240
        item_height = 90
        
        for i, (name, desc) in enumerate(difficulties):
            color = (0, 255, 100) if i == selected else (255, 255, 150)
            
            name_text = self.font_medium.render(name, True, color)
            desc_text = self.font_small.render(desc, True, (200, 200, 100))
            
            name_rect = name_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, item_y + i * item_height))
            desc_rect = desc_text.get_rect(center=(name_rect.centerx, name_rect.centery + 40))
            
            if i == selected:
                shadow = self.font_medium.render(name, True, (0, 0, 0))
                shadow_rect = shadow.get_rect(center=(name_rect.centerx + 2, name_rect.centery + 2))
                self.surface.blit(shadow, shadow_rect)
            
            self.surface.blit(name_text, name_rect)
            self.surface.blit(desc_text, desc_rect)
        
        pygame.display.flip()
    
    def render_credits(self):
        self._draw_menu_background()
        
        title = self.font_large.render("CREDITS", True, (0, 255, 255))
        title_rect = title.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 150))
        self.surface.blit(title, title_rect)
        
        credit_lines = [
            "BATO BOMBER v1.0",
            "",
            "A Political Satire Game",
            "",
            "Design & Programming",
            "PatronHubDevs Team",
            "",
            "Built with Pygame",
            "",
            "Press SPACE to return"
        ]
        
        y = 220
        for line in credit_lines:
            text = self.font_small.render(line, True, (255, 255, 150))
            text_rect = text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, y))
            self.surface.blit(text, text_rect)
            y += 40
        
        pygame.display.flip()
    
    def render_leaderboard(self):
        self._draw_menu_background()
        
        title = self.font_large.render("TOP SCORES", True, (0, 255, 255))
        title_rect = title.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 150))
        self.surface.blit(title, title_rect)
        
        scores = Leaderboard.get_top_scores()
        
        if not scores:
            no_scores = self.font_medium.render("No scores yet!", True, (255, 255, 150))
            no_scores_rect = no_scores.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2))
            self.surface.blit(no_scores, no_scores_rect)
        else:
            y = 220
            for i, score in enumerate(scores):
                rank = f"#{i+1}"
                rank_text = self.font_small.render(rank, True, (0, 255, 100))
                
                entry_text = self.font_small.render(
                    f"{score.name:<15} {score.score:>6} (Lvl {score.level})",
                    True, (255, 255, 150)
                )
                
                date_text = self.font_tiny.render(
                    f"{score.date} - {score.difficulty}",
                    True, (200, 200, 100)
                )
                
                self.surface.blit(rank_text, (40, y))
                self.surface.blit(entry_text, (100, y))
                self.surface.blit(date_text, (100, y + 25))
                y += 50
        
        hint = self.font_tiny.render("Press SPACE to return", True, (255, 255, 150))
        hint_rect = hint.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT - 30))
        self.surface.blit(hint, hint_rect)
        
        pygame.display.flip()
        
    def render_name_input(self, player_name: str = ""):
        """Render name input screen"""
        self._draw_menu_background()

        title = self.font_large.render("NEW HIGH SCORE!", True, (255, 255, 0)) # Changed to yellow
        self.surface.blit(title, title.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 80)))

        score_text = self.font_medium.render(
            f"Score: {self.score if hasattr(self, 'score') else 0}",
            True, (255, 255, 150) # Changed to yellow
        )
        self.surface.blit(score_text, score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 180)))

        name_label = self.font_medium.render("Enter Name:", True, (255, 255, 150)) # Changed to yellow
        self.surface.blit(name_label, name_label.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, 260)))

        # Input box
        input_rect = pygame.Rect(GameConfig.WINDOW_WIDTH // 2 - 150, 320, 300, 60)
        pygame.draw.rect(self.surface, (255, 255, 150), input_rect, 2) # Changed outline to yellow

        name_display = self.font_medium.render(player_name if player_name else "_", True, (255, 255, 255))
        self.surface.blit(name_display, name_display.get_rect(center=input_rect.center))

        # Multiline hint (correct)
        hint_lines = [
            "Type your name (max 15 chars),",
            "SPACE to submit"
        ]

        start_y = 440
        line_spacing = 6

        for i, line in enumerate(hint_lines):
            surf = self.font_small.render(line, True, (255, 255, 150)) # Changed to yellow
            rect = surf.get_rect(
                center=(GameConfig.WINDOW_WIDTH // 2,
                        start_y + i * (surf.get_height() + line_spacing))
            )
            self.surface.blit(surf, rect)

        pygame.display.flip()
    
    def show_level_complete(self):
        self._draw_menu_background()
        
        lc_text = self.font_large.render("LEVEL COMPLETE!", True, (0, 255, 100))
        score_text = self.font_small.render(f"Score: {self.score if hasattr(self, 'score') else 0}", True, (255, 255, 150))
        next_text = self.font_small.render("Next Level...", True, (0, 255, 255))
        
        self.surface.blit(lc_text, lc_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 - 50)))
        self.surface.blit(score_text, score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 20)))
        self.surface.blit(next_text, next_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 60)))
        
        pygame.display.flip()
        pygame.time.wait(2000)
    
    def show_game_over(self):
        self._draw_menu_background()
        
        go_text = self.font_large.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font_small.render(f"Final Score: {self.score if hasattr(self, 'score') else 0}", True, (255, 255, 150))
        level_text = self.font_small.render(f"Level Reached: {self.level if hasattr(self, 'level') else 1}", True, (255, 255, 150))
        
        self.surface.blit(go_text, go_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 - 50)))
        self.surface.blit(score_text, score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 20)))
        self.surface.blit(level_text, level_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 60)))
        
        pygame.display.flip()
        pygame.time.wait(3000)
    
    def show_game_won(self):
        self._draw_menu_background()
        
        won_text = self.font_large.render("YOU WIN!", True, (0, 255, 100))
        score_text = self.font_small.render(f"Final Score: {self.score if hasattr(self, 'score') else 0}", True, (255, 255, 150))
        
        self.surface.blit(won_text, won_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 - 50)))
        self.surface.blit(score_text, score_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2 + 20)))
        
        pygame.display.flip()
        pygame.time.wait(3000)

    def render_pause_screen(self):
        overlay = pygame.Surface((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        pause_text = self.font_large.render("PAUSED", True, (255, 255, 150))
        text_rect = pause_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2))
        
        self.surface.blit(overlay, (0, 0))
        self.surface.blit(pause_text, text_rect)
        pygame.display.flip()
