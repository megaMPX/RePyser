PYINSTALLER_MAGIC = b"MEI\x0c\x0b\x0a\x0b\x0e"

SUSPICIOUS_KEYWORDS = {
    "eval", "exec", "socket", "subprocess",
    "requests", "urllib", "http", "pty", "ctypes"
}
