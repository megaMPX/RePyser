from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class GraphView(QWidget):
    def __init__(self):
        super().__init__()
        self._current_code = None

        self._label = QLabel("Load a file to build graph")
        self._label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout = QVBoxLayout(self)
        layout.addWidget(self._label)

    def set_code(self, codeobj):
        self._current_code = codeobj
        self._label.setText("-")
