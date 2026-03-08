import dis
import html

import pydot
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class GraphView(QWidget):
    def __init__(self):
        super().__init__()
        self._current_code = None
        self._zoom = 0.75

        self._label = QLabel("Load a file to build graph")
        self._label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._label)

        layout = QVBoxLayout(self)
        layout.addWidget(self._scroll)

    def set_code(self, codeobj):
        self._current_code = codeobj
        self._zoom = 0.75
        self._render_graph()

    def _render_graph(self):
        if self._current_code is None:
            return

        png_data = build_cfg_png(self._current_code, scale=self._zoom)
        pixmap = QPixmap()
        if not pixmap.loadFromData(png_data):
            self._label.setText("Ошибка построения графа")
            return

        self._label.setText("")
        self._label.setPixmap(pixmap)
        self._label.resize(pixmap.size())

    def wheelEvent(self, event):
        if self._current_code is None:
            return

        delta = event.angleDelta().y()
        if delta > 0:
            self._zoom *= 1.12
        else:
            self._zoom /= 1.12
        self._zoom = max(0.08, min(10.0, self._zoom))
        self._render_graph()
        event.accept()


def build_cfg_png(codeobj, scale=1.0):
    dpi = max(96, int(120 * scale))
    instructions = list(dis.get_instructions(codeobj))

    graph = pydot.Dot("cfg", graph_type="digraph")
    graph.set("dpi", str(dpi))

    lines = []
    for ins in instructions:
        arg = html.escape(ins.argrepr) if ins.argrepr else ""
        text = f"{ins.offset:04x}: {html.escape(ins.opname)} {arg}".rstrip()
        lines.append(text)

    graph.add_node(pydot.Node("b0", shape="box", label="\\n".join(lines) if lines else "<empty>"))
    return graph.create_png()
