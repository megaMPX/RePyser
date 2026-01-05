from PyQt6.QtGui import QColor
import marshal
from .constants import SUSPICIOUS_KEYWORDS

def classify_pyc(path: str) -> QColor:
    low = path.lower()
    if "site-packages" in low or "pyz_" in low or "_pyi_" in low:
        return QColor("#4FC1FF")
    try:
        with open(path, "rb") as f:
            f.read(16)
            code = marshal.load(f)
        if set(code.co_names) & SUSPICIOUS_KEYWORDS:
            return QColor("#F44336")
    except Exception:
        pass
    return QColor("#9CDCFE")
