import dis
import html

import pydot
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
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
        self._render_graph()

    def _render_graph(self):
        if self._current_code is None:
            return

        png_data = build_cfg_png(self._current_code)
        pixmap = QPixmap()
        if not pixmap.loadFromData(png_data):
            self._label.setText("Ошибка построения графа")
            return

        self._label.setText("")
        self._label.setPixmap(pixmap)


def build_cfg_png(codeobj):
    instructions = list(dis.get_instructions(codeobj))

    graph = pydot.Dot("cfg", graph_type="digraph")
    graph.set("dpi", "120")

    lines = []
    for ins in instructions:
        arg = f" {html.escape(ins.argrepr)}" if ins.argrepr else ""
        lines.append(f"{ins.offset:04x}: {html.escape(ins.opname)}{arg}")

    label = "\\n".join(lines) if lines else "<empty>"
    graph.add_node(pydot.Node("b0", shape="box", label=label))
    return graph.create_png()
