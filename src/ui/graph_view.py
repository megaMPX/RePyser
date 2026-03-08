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

        self._scroll = GraphScrollArea(self._zoom_by_wheel)
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
        try:
            png_data = build_cfg_png(self._current_code, scale=self._zoom)
        except Exception as exc:
            self._label.setText(f"Не удалось построить график:\n{exc}")
            self._label.setPixmap(QPixmap())
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(png_data):
            self._label.setText("Ошибка потсроения графа")
            return

        self._label.setText("")
        self._label.setPixmap(pixmap)
        self._label.resize(pixmap.size())

    def _zoom_by_wheel(self, delta):
        if self._current_code is None:
            return
        if delta > 0:
            self._zoom *= 1.12
        else:
            self._zoom /= 1.12
        self._zoom = max(0.08, min(10.0, self._zoom))
        self._render_graph()


def build_cfg_png(codeobj, scale=1.0):
    dpi = max(96, int(120 * scale))
    instructions = list(dis.get_instructions(codeobj))
    if not instructions:
        graph = pydot.Dot("cfg", graph_type="digraph")
        graph.set("dpi", str(dpi))
        return graph.create_png()

    blocks = _split_basic_blocks(instructions)
    index_by_offset = {ins.offset: idx for idx, ins in enumerate(instructions)}
    block_by_offset = {block["start"]: idx for idx, block in enumerate(blocks)}

    for block in blocks:
        last = block["ins"][-1]
        i = index_by_offset[last.offset]
        block["next_offset"] = instructions[i + 1].offset if i + 1 < len(instructions) else None
        block["succ"] = _block_successors(last, block["next_offset"])

    graph = pydot.Dot(
        "cfg",
        graph_type="digraph",
        rankdir="TB",
        bgcolor="transparent",
        splines="ortho",
        nodesep="0.55",
        ranksep="0.70",
    )
    graph.set("dpi", str(dpi))
    graph.set_node_defaults(
        shape="box",
        style="filled",
        fillcolor="#1b1b1b",
        color="#6c6c6c",
        penwidth="1.0",
        fontname="JetBrains Mono",
        fontsize="12",
        fontcolor="#e6e6e6",
    )
    graph.set_edge_defaults(color="#9a9a9a", penwidth="1.2", arrowsize="0.8")

    for idx, block in enumerate(blocks):
        lines = [_instruction_to_html(ins) for ins in block["ins"]]
        label = (
            "<<FONT FACE='JetBrains Mono' POINT-SIZE='11'>"
            + "<BR ALIGN='LEFT'/>".join(lines)
            + "<BR ALIGN='LEFT'/></FONT>>"
        )
        graph.add_node(pydot.Node(f"b{idx}", label=label))

    for idx, block in enumerate(blocks):
        for to_offset, edge_label in block["succ"]:
            dst = block_by_offset.get(to_offset)
            if dst is None:
                continue
            graph.add_edge(
                pydot.Edge(
                    f"b{idx}",
                    f"b{dst}",
                    color="#9a9a9a",
                )
            )

    return graph.create_png()


def _split_basic_blocks(instructions):
    leaders = {instructions[0].offset}
    offsets = {ins.offset for ins in instructions}

    for i, ins in enumerate(instructions):
        jump_target = _jump_target(ins)
        if jump_target is not None and jump_target in offsets:
            leaders.add(jump_target)
        if _is_jump(ins.opname) and i + 1 < len(instructions):
            leaders.add(instructions[i + 1].offset)

    blocks = []
    current = []
    for ins in instructions:
        if current and ins.offset in leaders:
            blocks.append({"start": current[0].offset, "ins": current})
            current = []
        current.append(ins)

    if current:
        blocks.append({"start": current[0].offset, "ins": current})

    return blocks


def _block_successors(last_ins, next_offset):
    op = last_ins.opname
    target = _jump_target(last_ins)

    if op in {"RETURN_VALUE", "RERAISE"}:
        return []

    if _is_conditional_jump(op):
        succ = []
        if target is not None:
            succ.append((target, "T"))
        if next_offset is not None:
            succ.append((next_offset, "F"))
        return succ

    if op.startswith("JUMP"):
        return [(target, "")] if target is not None else []

    if op == "FOR_ITER":
        succ = []
        if next_offset is not None:
            succ.append((next_offset, "loop"))
        if target is not None:
            succ.append((target, "exit"))
        return succ

    if next_offset is None:
        return []
    return [(next_offset, "")]


def _is_jump(opname):
    return (
        opname.startswith("JUMP")
        or opname.startswith("POP_JUMP")
        or opname == "FOR_ITER"
    )


def _is_conditional_jump(opname):
    return "JUMP" in opname and "IF" in opname


def _jump_target(ins):
    if isinstance(ins.argval, int):
        return ins.argval
    return None


def _instruction_to_html(ins):
    offset = f"{ins.offset:04x}:"
    opname = html.escape(ins.opname)
    arg = html.escape(ins.argrepr) if ins.argrepr else ""

    parts = [
        f"<FONT COLOR='#8aa8ff'>{offset}</FONT>",
        f"<FONT COLOR='#c586c0'>{opname}</FONT>",
    ]
    if arg:
        parts.append(f"<FONT COLOR='#ce9178'>{arg}</FONT>")
    return " ".join(parts)


class GraphScrollArea(QScrollArea):
    def __init__(self, zoom_callback):
        super().__init__()
        self._zoom_callback = zoom_callback
        self._drag_active = False
        self._last_pos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._last_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and self._last_pos is not None:
            delta = event.pos() - self._last_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._last_pos = event.pos()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_active:
            self._drag_active = False
            self._last_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta != 0:
            self._zoom_callback(delta)
            event.accept()
            return
        super().wheelEvent(event)
