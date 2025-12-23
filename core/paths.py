import os
import sys

def project_root() -> str:
    """
    Returns the absolute path to the project root.
    Works for scripts, PyInstaller, and Nuitka.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller/Nuitka
        return sys._MEIPASS
    # Go up from the current file (e.g., config/settings.py)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
