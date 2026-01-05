import os
from .constants import PYINSTALLER_MAGIC

def is_pyinstaller_bundle(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            f.seek(-1024 * 1024, os.SEEK_END)
            return PYINSTALLER_MAGIC in f.read()
    except Exception:
        return False
