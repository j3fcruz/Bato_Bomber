"""
Bato Bomber Sprite Generator
Generates all game sprites with cyberpunk hacker theme
"""

import pygame
import os
from PIL import Image, ImageDraw

class SpriteGenerator:
    """Generate sprite sheets for Bato Bomber"""
    
    TILE_SIZE = 48
    SPRITE_DIR = "D:/Python Sample/PyGames/Bato_Bomber/assets/sprites"
    
    @staticmethod
    def init_dir():
        """Create sprites directory if it doesn't exist"""
        if not os.path.exists(SpriteGenerator.SPRITE_DIR):
            os.makedirs(SpriteGenerator.SPRITE_DIR)
    
    @staticmethod
    def _draw_character(draw, x, y, size, color, dark_color, accent_color, direction, step_phase=0):
        """
        Helper to draw a character with direction.
        direction: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        step_phase: 0=Idle, 1=Left Leg, 2=Right Leg
        """
        # Body
        draw.rectangle([x, y, x + size, y + size], fill=color, outline=dark_color)
        
        # Eyes / Face details based on direction
        eye_size = size // 4
        eye_y = y + size // 4
        
        if direction == 0: # UP (Back view)
            # Hood/Backpack detail
            draw.rectangle([x + size//4, y + size//4, x + size*3//4, y + size*3//4], fill=dark_color)
            
        elif direction == 1: # DOWN (Front view)
            # Two eyes
            draw.ellipse([x + size//4 - 2, eye_y, x + size//4 + 4, eye_y + 6], fill=accent_color)
            draw.ellipse([x + size*3//4 - 4, eye_y, x + size*3//4 + 2, eye_y + 6], fill=accent_color)
            
        elif direction == 2: # LEFT (Side view)
            # One eye on left
            draw.ellipse([x + 2, eye_y, x + 8, eye_y + 6], fill=accent_color)
            # Backpack bump on right
            draw.rectangle([x + size, y + size//4, x + size + 4, y + size*3//4], fill=dark_color)
            
        elif direction == 3: # RIGHT (Side view)
            # One eye on right
            draw.ellipse([x + size - 8, eye_y, x + size - 2, eye_y + 6], fill=accent_color)
            # Backpack bump on left
            draw.rectangle([x - 4, y + size//4, x, y + size*3//4], fill=dark_color)

        # Legs
        leg_w = size // 4
        leg_h = size // 4
        leg_y = y + size
        
        left_leg_offset = 0
        right_leg_offset = 0
        
        if step_phase == 1: # Left leg forward/up
            left_leg_offset = -4
        elif step_phase == 2: # Right leg forward/up
            right_leg_offset = -4
            
        draw.rectangle([x + 4, leg_y + left_leg_offset, x + 4 + leg_w, leg_y + leg_h + left_leg_offset], fill=dark_color)
        draw.rectangle([x + size - 4 - leg_w, leg_y + right_leg_offset, x + size - 4, leg_y + leg_h + right_leg_offset], fill=dark_color)

    @staticmethod
    def generate_player_sheet():
        """Generate player sprite sheet (blue hacker character)"""
        width = 4 * SpriteGenerator.TILE_SIZE
        height = 6 * SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        skin = (100, 150, 255)
        dark = (50, 100, 200)
        accent = (200, 255, 100)
        
        char_size = 24
        offset = (SpriteGenerator.TILE_SIZE - char_size) // 2

        # Row 0: Idle (up, down, left, right)
        for col in range(4):
            x = col * SpriteGenerator.TILE_SIZE + offset
            y = offset
            SpriteGenerator._draw_character(draw, x, y, char_size, skin, dark, accent, direction=col, step_phase=0)
        
        # Row 1-4: Walk animation (4 frames per direction)
        # Frame sequence: Idle -> Left Step -> Idle -> Right Step
        step_phases = [0, 1, 0, 2]
        
        for row in range(1, 5):
            step_phase = step_phases[row - 1]
            for col in range(4):
                x = col * SpriteGenerator.TILE_SIZE + offset
                y = row * SpriteGenerator.TILE_SIZE + offset
                SpriteGenerator._draw_character(draw, x, y, char_size, skin, dark, accent, direction=col, step_phase=step_phase)
        
        # Row 5: Place bomb (2 frames) - Just use Front view for simplicity
        for i in range(2):
            x = i * SpriteGenerator.TILE_SIZE + offset
            y = 5 * SpriteGenerator.TILE_SIZE + offset
            SpriteGenerator._draw_character(draw, x, y, char_size, skin, dark, accent, direction=1, step_phase=0)
            # Arm raised
            draw.rectangle([x + char_size - 4, y - 4, x + char_size, y + 8], fill=skin, outline=dark)
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/player_blue.png")
        print(f"✓ Generated: player_blue.png ({width}x{height})")
    
    @staticmethod
    def generate_enemy_sheet():
        """Generate enemy sprite sheet (red hacker character)"""
        width = 4 * SpriteGenerator.TILE_SIZE
        height = 2 * SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        skin = (255, 100, 100)
        dark = (200, 50, 50)
        accent = (255, 200, 100)
        
        char_size = 24
        offset = (SpriteGenerator.TILE_SIZE - char_size) // 2

        # 2 walk frames per direction: Left Step -> Right Step
        step_phases = [1, 2]

        for row in range(2):
            step_phase = step_phases[row]
            for col in range(4):
                x = col * SpriteGenerator.TILE_SIZE + offset
                y = row * SpriteGenerator.TILE_SIZE + offset
                SpriteGenerator._draw_character(draw, x, y, char_size, skin, dark, accent, direction=col, step_phase=step_phase)
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/enemy_red.png")
        print(f"✓ Generated: enemy_red.png ({width}x{height})")
    
    @staticmethod
    def generate_bomb_sheet():
        """Generate bomb sprite sheet (3 frames)"""
        width = 3 * SpriteGenerator.TILE_SIZE
        height = SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bomb_color = (30, 30, 30)
        spark = (255, 255, 100)
        
        bomb_size = 24
        offset = (SpriteGenerator.TILE_SIZE - bomb_size) // 2

        for i in range(3):
            x = i * SpriteGenerator.TILE_SIZE + offset
            y = offset
            draw.ellipse([x, y, x + bomb_size, y + bomb_size], fill=bomb_color, outline=(0, 0, 0))
            draw.line([x + 12, y, x + 12, y - 6], fill=(100, 50, 0), width=3)
            spark_size = 4 + i * 2
            draw.ellipse([x + 8, y - 6 - spark_size, x + 16, y - 6], fill=spark)
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/bomb.png")
        print(f"✓ Generated: bomb.png ({width}x{height})")
    
    @staticmethod
    def generate_explosion_sheet():
        """Generate explosion sprite sheet (4 frames)"""
        width = 4 * SpriteGenerator.TILE_SIZE
        height = SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        colors = [(255, 200, 0), (255, 150, 0), (255, 100, 0), (200, 50, 0)]
        
        center = SpriteGenerator.TILE_SIZE // 2

        for frame in range(4):
            x = frame * SpriteGenerator.TILE_SIZE + center
            y = center
            size = 8 + frame * 6  # Scaled size
            
            draw.ellipse([x - size, y - size, x + size, y + size], fill=colors[frame])
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/explosion.png")
        print(f"✓ Generated: explosion.png ({width}x{height})")
    
    @staticmethod
    def generate_powerups_sheet():
        """Generate power-up sprites (bomb count, blast radius, speed)"""
        width = 3 * SpriteGenerator.TILE_SIZE
        height = SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        item_size = 32
        offset = (SpriteGenerator.TILE_SIZE - item_size) // 2

        # Power-up 0: Bomb Count (Gold)
        x, y = offset, offset
        draw.rectangle([x, y, x + item_size, y + item_size], fill=(255, 215, 0), outline=(200, 170, 0))
        draw.text((x + 12, y + 10), "B", fill=(0, 0, 0))
        
        # Power-up 1: Blast Radius (Red)
        x = SpriteGenerator.TILE_SIZE + offset
        draw.rectangle([x, y, x + item_size, y + item_size], fill=(255, 100, 100), outline=(200, 50, 50))
        draw.text((x + 12, y + 10), "R", fill=(0, 0, 0))
        
        # Power-up 2: Speed (Blue)
        x = 2 * SpriteGenerator.TILE_SIZE + offset
        draw.rectangle([x, y, x + item_size, y + item_size], fill=(100, 200, 255), outline=(50, 150, 200))
        draw.text((x + 12, y + 10), "S", fill=(0, 0, 0))
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/powerups.png")
        print(f"✓ Generated: powerups.png ({width}x{height})")
    
    @staticmethod
    def generate_tiles_sheet():
        """Generate tilemap sprites (wall, destructible, floor, home)"""
        width = 4 * SpriteGenerator.TILE_SIZE
        height = SpriteGenerator.TILE_SIZE
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        ts = SpriteGenerator.TILE_SIZE

        # Tile 0: Floor
        x = 0
        draw.rectangle([x, 0, x + ts, ts], fill=(220, 220, 220), outline=(180, 180, 180))
        
        # Tile 1: Wall
        x = ts
        draw.rectangle([x, 0, x + ts, ts], fill=(80, 80, 80), outline=(60, 60, 60))
        draw.rectangle([x + 6, 6, x + ts - 6, ts - 6], fill=(100, 100, 100))
        
        # Tile 2: Destructible
        x = 2 * ts
        draw.rectangle([x, 0, x + ts, ts], fill=(180, 120, 60), outline=(150, 90, 40))
        draw.rectangle([x + 6, 6, x + ts - 6, ts - 6], fill=(150, 100, 50))
        
        # Tile 3: Home/Goal
        x = 3 * ts
        draw.rectangle([x, 0, x + ts, ts], fill=(100, 150, 255), outline=(50, 100, 200))
        draw.line([x + 12, 12, x + ts - 12, ts - 12], fill=(200, 255, 100), width=3)
        draw.circle((x + ts - 12, 24), 4, fill=(255, 200, 100))
        
        img.save(f"{SpriteGenerator.SPRITE_DIR}/tiles.png")
        print(f"✓ Generated: tiles.png ({width}x{height})")
    
    @staticmethod
    def generate_all():
        """Generate all sprite sheets"""
        print("\n🎨 Generating Bato Bomber Sprites...")
        SpriteGenerator.init_dir()
        
        SpriteGenerator.generate_player_sheet()
        SpriteGenerator.generate_enemy_sheet()
        SpriteGenerator.generate_bomb_sheet()
        SpriteGenerator.generate_explosion_sheet()
        SpriteGenerator.generate_powerups_sheet()
        SpriteGenerator.generate_tiles_sheet()
        
        print("\n✅ All sprites generated in 'assets/sprites/' folder!")
        print("\nSprite files created:")
        print("  • player_blue.png     - Blue player character")
        print("  • enemy_red.png       - Red enemy characters")
        print("  • bomb.png            - Bomb animation")
        print("  • explosion.png       - Explosion animation")
        print("  • powerups.png        - Power-up items (B, R, S)")
        print("  • tiles.png           - Tilemap (floor, wall, destructible, home)")

if __name__ == "__main__":
    SpriteGenerator.generate_all()
