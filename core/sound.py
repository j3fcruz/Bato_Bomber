import pygame
import os
import sys
import tempfile

from PyQt5.QtCore import QFile, QIODevice

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.base_path = self._get_base_path()
        self.sound_dir = os.path.join(self.base_path, "assets", "sounds")

        self._temp_files = []  # prevent GC of temp files

        self.sounds = {
            "place_bomb": self._load_sound_hybrid(
                qrc=":/sounds/place_bomb.wav",
                file="place_bomb.wav",
            ),
            "explosion": self._load_sound_hybrid(
                qrc=":/sounds/explosion.wav",
                file="explosion.wav",
            ),
            "level_complete": self._load_sound_hybrid(
                qrc=":/sounds/level_complete.wav",
                file="level_complete.wav",
            ),
            "enemy_dead": self._load_sound_hybrid(
                qrc=":/sounds/enemy_dead.wav",
                file="enemy_dead.wav",
            ),
            "hero_dead": self._load_sound_hybrid(
                qrc=":/sounds/hero_dead.wav",
                file="hero_dead.wav",
            ),
            "powerup": self._load_sound_hybrid(
                qrc=":/sounds/powerup.wav",
                file="powerup.wav",
            ),
        }

        self._load_music_hybrid(
            qrc=":/sounds/background_music.ogg",
            file="background_music.ogg",
        )

    # --------------------------------------------------
    # Base path (safe for PyInstaller / Nuitka)
    # --------------------------------------------------
    def _get_base_path(self):
        if getattr(sys, "frozen", False):
            return sys._MEIPASS
        # Go one level up from the 'core' directory to the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # --------------------------------------------------
    # Hybrid loaders
    # --------------------------------------------------
    def _load_sound_hybrid(self, qrc: str, file: str):
        # 1. Try QRC
        try:
            data = self._read_qrc_bytes(qrc)
            path = self._bytes_to_tempfile(data, suffix=".wav")
            return pygame.mixer.Sound(path)
        except Exception:
            pass

        # 2. Fallback to filesystem
        try:
            path = os.path.join(self.sound_dir, file)
            return pygame.mixer.Sound(path)
        except pygame.error:
            print(f"[SoundManager] Missing sound: {file}")
            return None

    def _load_music_hybrid(self, qrc: str, file: str):
        # 1. Try QRC
        try:
            data = self._read_qrc_bytes(qrc)
            path = self._bytes_to_tempfile(data, suffix=".ogg")
            pygame.mixer.music.load(path)
            return
        except Exception:
            pass

        # 2. Fallback to filesystem
        try:
            path = os.path.join(self.sound_dir, file)
            pygame.mixer.music.load(path)
        except pygame.error:
            print(f"[SoundManager] Missing music: {file}")

    # --------------------------------------------------
    # QRC helpers
    # --------------------------------------------------
    def _read_qrc_bytes(self, qrc_path) -> bytes:
        file = QFile(qrc_path)
        if not file.open(QIODevice.ReadOnly):
            raise FileNotFoundError(qrc_path)
        return bytes(file.readAll())

    def _bytes_to_tempfile(self, data: bytes, suffix: str) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(data)
        tmp.close()
        self._temp_files.append(tmp.name)
        return tmp.name

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def play_sfx(self, name, volume=1.0):
        snd = self.sounds.get(name)
        if snd:
            snd.set_volume(volume)
            snd.play()

    def play_background_music(self, volume=0.7, loops=-1):
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    def stop_background_music(self):
        pygame.mixer.music.stop()

    def set_sfx_volume(self, volume):
        for s in self.sounds.values():
            if s:
                s.set_volume(volume)

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)
