import pygame
import sys
from config.settings import GameConfig, GameSettings, MenuState, Direction, GameDifficulty
from core.game_logic import GameState
from core.renderer import GameRenderer
from gameplay.leaderboard import Leaderboard
from core.sound import SoundManager
from config.app_config import setup_pygame

class GameController:
    def __init__(self, state: GameState, renderer: GameRenderer):
        self.state = state
        self.renderer = renderer
        self.sound_manager = SoundManager()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Menu state
        self.menu_state = MenuState.MAIN
        self.menu_selected = 0
        self.settings = GameSettings.load()
        
        # Name input
        self.player_name = ""
        self.game_score = 0
        self.game_level = 0
        
        # Update game difficulty and sound volumes
        self._apply_difficulty()
        self.sound_manager.set_sfx_volume(self.settings.sfx_volume)
        self.sound_manager.set_music_volume(self.settings.music_volume)
        
        # Subscribe to game events
        self.state.events.subscribe("explosion", self._on_explosion)
        self.state.events.subscribe("bomb_placed", self._on_bomb_placed)
        self.state.events.subscribe("level_complete", self._on_level_complete)
        self.state.events.subscribe("enemy_killed", self._on_enemy_killed)
        self.state.events.subscribe("player_dead", self._on_player_dead)
        self.state.events.subscribe("power_up_collected", self._on_power_up_collected)

    def _on_explosion(self, data):
        """Handle the explosion event."""
        if self.settings.screen_shake:
            self.renderer.trigger_shake()
        self.sound_manager.play_sfx('explosion', self.settings.sfx_volume)

    def _on_bomb_placed(self, data):
        """Handle the bomb placed event."""
        self.sound_manager.play_sfx('place_bomb', self.settings.sfx_volume)

    def _on_level_complete(self, data):
        """Handle the level complete event."""
        self.sound_manager.play_sfx('level_complete', self.settings.sfx_volume)

    def _on_enemy_killed(self, data):
        """Handle the enemy killed event."""
        self.sound_manager.play_sfx('enemy_dead', self.settings.sfx_volume)

    def _on_player_dead(self, data):
        """Handle the player dead event."""
        self.sound_manager.play_sfx('hero_dead', self.settings.sfx_volume)

    def _on_power_up_collected(self, data):
        """Handle the power-up collected event."""
        self.sound_manager.play_sfx('powerup', self.settings.sfx_volume)

    def _apply_difficulty(self):
        """Apply difficulty settings to game state"""
        if self.state:
            multiplier = self.settings.difficulty.value
            GameConfig.BOMB_TIMER = 3.0 / multiplier
    
    def handle_menu_input(self):
        """Handle menu navigation"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.menu_state == MenuState.MAIN:
                    if event.key == pygame.K_UP:
                        self.menu_selected = (self.menu_selected - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected = (self.menu_selected + 1) % 5
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self._handle_main_menu_select()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.menu_state == MenuState.LEADERBOARD:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.menu_state = MenuState.MAIN
                        self.menu_selected = 1
                
                elif self.menu_state == MenuState.NAME_INPUT:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.player_name.strip():
                            Leaderboard.add_score(self.player_name, self.game_score, 
                                                self.game_level, self.settings.difficulty.name)
                            self.player_name = ""
                            self.menu_state = MenuState.MAIN
                            self.menu_selected = 0
                    elif event.unicode.isalnum() or event.unicode == " ":
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode
                
                elif self.menu_state == MenuState.OPTIONS:
                    if event.key == pygame.K_UP:
                        self.menu_selected = (self.menu_selected - 1) % 5
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected = (self.menu_selected + 1) % 5
                    elif event.key == pygame.K_LEFT:
                        self._adjust_option(False)
                    elif event.key == pygame.K_RIGHT:
                        self._adjust_option(True)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.menu_selected == 4:  # Back
                            self.menu_state = MenuState.MAIN
                            self.menu_selected = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_state = MenuState.MAIN
                        self.menu_selected = 0
                
                elif self.menu_state == MenuState.DIFFICULTY:
                    if event.key == pygame.K_UP:
                        self.menu_selected = (self.menu_selected - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected = (self.menu_selected + 1) % 4
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        difficulties = [GameDifficulty.EASY, GameDifficulty.NORMAL, 
                                      GameDifficulty.HARD, GameDifficulty.NIGHTMARE]
                        self.settings.difficulty = difficulties[self.menu_selected]
                        self.settings.save()
                        self.menu_state = MenuState.MAIN
                        self.menu_selected = 2
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_state = MenuState.MAIN
                        self.menu_selected = 2
                
                elif self.menu_state == MenuState.CREDITS:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.menu_state = MenuState.MAIN
                        self.menu_selected = 3
    
    def _handle_main_menu_select(self):
        """Handle main menu selection"""
        if self.menu_selected == 0:  # Start Game
            self.menu_state = MenuState.GAME
            self.state = GameState(GameConfig(), level=1, difficulty=self.settings.difficulty)
            self.state.events.subscribe("explosion", self._on_explosion)
            self.state.events.subscribe("bomb_placed", self._on_bomb_placed)
            self.state.events.subscribe("level_complete", self._on_level_complete)
            self.state.events.subscribe("enemy_killed", self._on_enemy_killed)
            self.state.events.subscribe("player_dead", self._on_player_dead)
            self.state.events.subscribe("power_up_collected", self._on_power_up_collected)
            self._apply_difficulty()
            self.sound_manager.play_background_music(self.settings.music_volume)
        elif self.menu_selected == 1:  # Leaderboard
            self.menu_state = MenuState.LEADERBOARD
        elif self.menu_selected == 2:  # Options
            self.menu_state = MenuState.OPTIONS
            self.menu_selected = 0
        elif self.menu_selected == 3:  # Credits
            self.menu_state = MenuState.CREDITS
        elif self.menu_selected == 4:  # Exit
            self.running = False
    
    def _adjust_option(self, increase: bool):
        """Adjust selected option"""
        step = 0.1 if increase else -0.1
        
        if self.menu_selected == 1:  # Music volume
            self.settings.music_volume = max(0.0, min(1.0, self.settings.music_volume + step))
            self.sound_manager.set_music_volume(self.settings.music_volume)
        elif self.menu_selected == 2:  # SFX volume
            self.settings.sfx_volume = max(0.0, min(1.0, self.settings.sfx_volume + step))
            self.sound_manager.set_sfx_volume(self.settings.sfx_volume)
        elif self.menu_selected == 3:  # Screen shake
            self.settings.screen_shake = not self.settings.screen_shake
        elif self.menu_selected == 0:  # Difficulty
            self.menu_state = MenuState.DIFFICULTY
            self.menu_selected = 0
    
    def handle_game_input(self):
        """Handle in-game input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.menu_state = MenuState.MAIN
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if self.menu_state == MenuState.GAME:
                        self.menu_state = MenuState.PAUSED
                    elif self.menu_state == MenuState.PAUSED:
                        self.menu_state = MenuState.GAME
                elif self.menu_state == MenuState.GAME:
                    if event.key == pygame.K_UP:
                        self.state.try_move(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.state.try_move(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.state.try_move(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.state.try_move(Direction.RIGHT)
                    elif event.key == pygame.K_SPACE:
                        self.state.place_bomb()
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_state = MenuState.MAIN
                        self.sound_manager.stop_background_music()
                        self.menu_selected = 0
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(GameConfig.FPS) / 1000.0
            
            if self.menu_state == MenuState.MAIN:
                self.handle_menu_input()
                self.renderer.render_main_menu(self.menu_selected)
            
            elif self.menu_state == MenuState.LEADERBOARD:
                self.handle_menu_input()
                self.renderer.render_leaderboard()
            
            elif self.menu_state == MenuState.NAME_INPUT:
                self.handle_menu_input()
                self.renderer.render_name_input(self.player_name)
            
            elif self.menu_state == MenuState.OPTIONS:
                self.handle_menu_input()
                self.renderer.render_options_menu(self.settings, self.menu_selected)
            
            elif self.menu_state == MenuState.DIFFICULTY:
                self.handle_menu_input()
                self.renderer.render_difficulty_menu(self.menu_selected)
            
            elif self.menu_state == MenuState.CREDITS:
                self.handle_menu_input()
                self.renderer.render_credits()
            
            elif self.menu_state == MenuState.PAUSED:
                self.handle_game_input()
                self.renderer.render_pause_screen()

            elif self.menu_state == MenuState.GAME:
                if not self.state.game_over:
                    self.handle_game_input()
                    self.state.update(dt)
                    self.renderer.render(self.state, dt)
                    
                    if self.state.level_complete:
                        self.renderer.score = self.state.score
                        self.renderer.level = self.state.level
                        self.renderer.show_level_complete()
                        if self.state.level < GameConfig.MAX_LEVELS:
                            next_level = self.state.level + 1
                            current_score = self.state.score
                            player_stats = {
                                "max_bombs": self.state.player.max_bombs,
                                "blast_radius": self.state.player.blast_radius
                            }
                            self.state = GameState(GameConfig(), level=next_level, difficulty=self.settings.difficulty, initial_score=current_score, player_stats=player_stats)
                            self.state.events.subscribe("explosion", self._on_explosion)
                            self.state.events.subscribe("bomb_placed", self._on_bomb_placed)
                            self.state.events.subscribe("level_complete", self._on_level_complete)
                            self.state.events.subscribe("enemy_killed", self._on_enemy_killed)
                            self.state.events.subscribe("player_dead", self._on_player_dead)
                            self.state.events.subscribe("power_up_collected", self._on_power_up_collected)
                        else:
                            self.renderer.show_game_won()
                            self.game_score = self.state.score
                            self.game_level = self.state.level
                            self.menu_state = MenuState.NAME_INPUT
                            self.player_name = ""
                            self.sound_manager.stop_background_music()
                else:
                    self.renderer.score = self.state.score
                    self.renderer.level = self.state.level
                    self.renderer.show_game_over()
                    self.game_score = self.state.score
                    self.game_level = self.state.level
                    self.menu_state = MenuState.NAME_INPUT
                    self.player_name = ""
                    self.sound_manager.stop_background_music()
            
            self.clock.tick(GameConfig.FPS)

def main():
    pygame.init()

    screen, clock = setup_pygame()

    config = GameConfig()
    renderer = GameRenderer(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    # Start with menu (no initial game state)
    state = GameState(config, level=1)
    controller = GameController(state, renderer)
    controller.menu_state = MenuState.MAIN
    controller.menu_selected = 0
    
    controller.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


