import pygame
import os
import sys
from PyQt5.QtCore import QFile
from io import BytesIO
import resources.resources_rc
_ = resources.resources_rc

APP_NAME = "Bato Bomber"
SCREEN_WIDTH = 416
SCREEN_HEIGHT = 416

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATH_QRC = ":/assets/icon/bato_bomber.png"
ICON_PATH_FS  = "assets/icon/bato_bomber.png"


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(BASE_DIR, "..", relative)


def load_icon(qrc_path, fallback_path, size=(32, 32)):
    try:
        file = QFile(qrc_path)
        if file.open(QFile.ReadOnly):
            data = bytes(file.readAll())
            file.close()
            icon = pygame.image.load(BytesIO(data)).convert_alpha()
            return pygame.transform.smoothscale(icon, size)
    except Exception:
        pass

    try:
        icon = pygame.image.load(resource_path(fallback_path)).convert_alpha()
        return pygame.transform.smoothscale(icon, size)
    except Exception:
        return None


def setup_pygame():
    pygame.mixer.init()
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(APP_NAME)

    icon = load_icon(ICON_PATH_QRC, ICON_PATH_FS)
    if icon:
        pygame.display.set_icon(icon)

    return screen, pygame.time.Clock()
