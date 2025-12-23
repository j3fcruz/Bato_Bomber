from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import pygame
import os
import sys

from config.settings import GameConfig


@dataclass
class AnimationFrame:
    rect: pygame.Rect
    duration: float


@dataclass
class SpriteAnimation:
    frames: List[AnimationFrame]
    loop: bool = True
    current_frame: int = 0
    elapsed: float = 0.0

    def update(self, dt: float) -> Tuple[pygame.Rect, bool]:
        if not self.frames:
            return pygame.Rect(0, 0, 0, 0), False

        self.elapsed += dt
        frame = self.frames[self.current_frame]

        if self.elapsed >= frame.duration:
            self.elapsed -= frame.duration
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                    return frame.rect, False
                else:
                    self.current_frame = len(self.frames) - 1
                    return frame.rect, True

        return frame.rect, False

    def reset(self):
        self.current_frame = 0
        self.elapsed = 0.0


class AnimationController:
    def __init__(self):
        self.animations: Dict[str, SpriteAnimation] = {}
        self.current_state: str = "idle_down"
        self.previous_state: Optional[str] = None

    def add_animation(self, state: str, anim: SpriteAnimation):
        self.animations[state] = anim

    def set_state(self, state: str):
        if state in self.animations and state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = state
            self.animations[state].reset()

    def update(self, dt: float) -> Tuple[pygame.Rect, bool]:
        if self.current_state not in self.animations:
            return pygame.Rect(0, 0, 0, 0), False
        return self.animations[self.current_state].update(dt)

    def get_current_frame(self) -> pygame.Rect:
        if self.current_state in self.animations:
            return self.animations[self.current_state].frames[
                self.animations[self.current_state].current_frame
            ].rect
        return pygame.Rect(0, 0, 0, 0)


class SpriteFactory:
    sprite_cache = {}
    sprites_loaded = False

    @staticmethod
    def _get_base_path():
        if getattr(sys, "frozen", False):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def load_sprite(filename: str) -> Optional[pygame.Surface]:
        """Load sprite from file with caching"""
        if filename in SpriteFactory.sprite_cache:
            return SpriteFactory.sprite_cache[filename]

        try:
            base_path = SpriteFactory._get_base_path()
            sprite_path = os.path.join(base_path, "assets", "sprites", filename)
            sprite = pygame.image.load(sprite_path).convert_alpha()
            SpriteFactory.sprite_cache[filename] = sprite
            return sprite
        except Exception:
            # Silently fail if sprites don't exist yet
            return None

    @staticmethod
    def create_player_animations(tile_size: int = None) -> AnimationController:
        """Create player animations with proper tile size"""
        if tile_size is None:
            tile_size = GameConfig.TILE_WIDTH

        controller = AnimationController()
        fs = 1.0 / GameConfig.ANIMATION_FPS
        sprite = SpriteFactory.load_sprite("player_blue.png")

        if sprite is None:
            # Create dummy animations if sprite not loaded
            dummy_frame = AnimationFrame(pygame.Rect(0, 0, tile_size, tile_size), fs)
            for i in range(4):
                controller.add_animation(f"idle_{i}", SpriteAnimation([dummy_frame], loop=True))
                walk_frames = [dummy_frame for _ in range(4)]
                controller.add_animation(f"walk_{i}", SpriteAnimation(walk_frames, loop=True))
            controller.add_animation("placing_bomb", SpriteAnimation([dummy_frame], loop=False))
            controller.set_state("idle_0")
            return controller

        # Idle animations (row 0)
        for i in range(4):
            controller.add_animation(
                f"idle_{i}",
                SpriteAnimation([AnimationFrame(
                    pygame.Rect(i * tile_size, 0, tile_size, tile_size),
                    fs * 2
                )], loop=True)
            )

        # Walk animations (rows 1-4, 4 frames each direction)
        for i in range(4):
            walk_frames = [
                AnimationFrame(pygame.Rect(i * tile_size, (1 + j) * tile_size, tile_size, tile_size), fs)
                for j in range(4)
            ]
            controller.add_animation(f"walk_{i}", SpriteAnimation(walk_frames, loop=True))

        # Place bomb animations (row 5, 2 frames)
        place_frames = [
            AnimationFrame(pygame.Rect(0, 5 * tile_size, tile_size, tile_size), fs),
            AnimationFrame(pygame.Rect(tile_size, 5 * tile_size, tile_size, tile_size), fs * 0.5),
        ]
        controller.add_animation("placing_bomb", SpriteAnimation(place_frames, loop=False))

        controller.set_state("idle_0")
        return controller

    @staticmethod
    def create_bomb_animations(tile_size: int = None) -> AnimationController:
        """Create bomb animations with proper tile size"""
        if tile_size is None:
            tile_size = GameConfig.TILE_WIDTH

        controller = AnimationController()
        fs = 1.0 / GameConfig.ANIMATION_FPS
        sprite = SpriteFactory.load_sprite("bomb.png")

        if sprite is None:
            dummy_frame = AnimationFrame(pygame.Rect(0, 0, tile_size, tile_size), fs)
            controller.add_animation("active", SpriteAnimation([dummy_frame], loop=True))
            controller.set_state("active")
            return controller

        frames = [
            AnimationFrame(pygame.Rect(i * tile_size, 0, tile_size, tile_size), fs)
            for i in range(3)
        ]
        controller.add_animation("active", SpriteAnimation(frames, loop=True))
        controller.set_state("active")
        return controller

    @staticmethod
    def create_explosion_animations(tile_size: int = None) -> AnimationController:
        """Create explosion animations with proper tile size"""
        if tile_size is None:
            tile_size = GameConfig.TILE_WIDTH

        controller = AnimationController()
        fs = 1.0 / (GameConfig.ANIMATION_FPS * 2)
        sprite = SpriteFactory.load_sprite("explosion.png")

        if sprite is None:
            dummy_frame = AnimationFrame(pygame.Rect(0, 0, tile_size, tile_size), fs)
            controller.add_animation("burst", SpriteAnimation([dummy_frame], loop=False))
            controller.set_state("burst")
            return controller

        frames = [
            AnimationFrame(pygame.Rect(i * tile_size, 0, tile_size, tile_size), fs)
            for i in range(4)
        ]
        controller.add_animation("burst", SpriteAnimation(frames, loop=False))
        controller.set_state("burst")
        return controller

    @staticmethod
    def create_enemy_animations(tile_size: int = None) -> AnimationController:
        """Create enemy animations with proper tile size"""
        if tile_size is None:
            tile_size = GameConfig.TILE_WIDTH

        controller = AnimationController()
        fs = 1.0 / GameConfig.ANIMATION_FPS
        sprite = SpriteFactory.load_sprite("enemy_red.png")

        if sprite is None:
            dummy_frame = AnimationFrame(pygame.Rect(0, 0, tile_size, tile_size), fs)
            for i in range(4):
                controller.add_animation(f"walk_{i}", SpriteAnimation([dummy_frame], loop=True))
            controller.set_state("walk_0")
            return controller

        # 4 directions, 2 frames each
        for i in range(4):
            walk_frames = [
                AnimationFrame(pygame.Rect(i * tile_size, j * tile_size, tile_size, tile_size), fs)
                for j in range(2)
            ]
            controller.add_animation(f"walk_{i}", SpriteAnimation(walk_frames, loop=True))

        controller.set_state("walk_0")
        return controller