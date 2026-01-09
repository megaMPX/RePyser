PYINSTALLER_MAGIC = b"MEI\x0c\x0b\x0a\x0b\x0e"

SUSPICIOUS_KEYWORDS = {
    "eval", "exec", "compile", "__import__",

    "subprocess", "os", "system", "popen", "fork", "execve",
    "kill", "signal",

    "socket", "requests", "urllib", "http", "https",
    "ftplib", "smtplib", "telnetlib",

    "open", "write", "unlink", "remove", "rmdir",
    "chmod", "chown", "rename", "copyfile",

    "pty", "ctypes", "mmap", "fcntl",

    "pickle", "marshal", "base64", "zlib", "bz2", "lzma",

    "getattr", "setattr", "globals", "locals", "vars",

    "crontab", "schedule", "startup", "autorun",

    "environ", "getenv",

    "sys", "traceback", "inspect"
}
