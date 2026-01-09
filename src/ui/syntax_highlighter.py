import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from ..constants import SUSPICIOUS_KEYWORDS

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)

        def fmt(fg, bg=None, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(fg))
            if bg:
                f.setBackground(QColor(bg))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            return f

        self.rules = [
            (re.compile(r"\b(def|class|if|else|elif|for|while|try|except|import|from|return)\b"),
             fmt("#C586C0", bold=True)),
            (re.compile(r'".*?"|".*?"'), fmt("#CE9178")),
            (re.compile(r"#.*"), fmt("#6A9955")),
            (re.compile(r"\b\d+\b"), fmt("#B5CEA8")),
        ]

        self.danger = re.compile(r"\b(" + "|".join(SUSPICIOUS_KEYWORDS) + r")\b")

    def highlightBlock(self, text):
        for rx, f in self.rules:
            for m in rx.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), f)

        for m in self.danger.finditer(text):
            df = QTextCharFormat()
            df.setForeground(QColor("white"))
            df.setBackground(QColor("#B71C1C"))
            df.setFontWeight(QFont.Weight.Bold)
            self.setFormat(m.start(), m.end() - m.start(), df)


class ReportHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)

        def fmt(fg, bg=None, bold=False, italic=False):
            f = QTextCharFormat()
            f.setForeground(QColor(fg))
            if bg:
                f.setBackground(QColor(bg))
            if bold:
                f.setFontWeight(QFont.Weight.Bold)
            if italic:
                f.setFontItalic(True)
            return f

        self.rules = [
            (re.compile(r"^/.*\.pyc$"), fmt("#569CD6", bold=True)),  
            (re.compile(r"^line \d+ offset \d+$"), fmt("#9CDCFE")), 
            (re.compile(r"^trigger: .*$"), fmt("#DCDCAA", bold=True)), 
            (re.compile(r"^[A-Z_]+ .*$"), fmt("#CE9178")), 
            (re.compile(r"^-{40}$"), fmt("#6A9955")), 
        ]

    def highlightBlock(self, text):
        for rx, f in self.rules:
            for m in rx.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), f)