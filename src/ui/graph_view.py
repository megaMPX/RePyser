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

    if not instructions:
        return graph.create_png()

    blocks = _split_basic_blocks(instructions)
    index_by_offset = {ins.offset: idx for idx, ins in enumerate(instructions)}
    block_by_offset = {block["start"]: idx for idx, block in enumerate(blocks)}

    for block in blocks:
        last = block["ins"][-1]
        i = index_by_offset[last.offset]
        next_offset = instructions[i + 1].offset if i + 1 < len(instructions) else None
        block["succ"] = _block_successors(last, next_offset)

    for idx, block in enumerate(blocks):
        lines = []
        for ins in block["ins"]:
            arg = html.escape(ins.argrepr) if ins.argrepr else ""
            text = f"{ins.offset:04x}: {html.escape(ins.opname)} {arg}".rstrip()
            lines.append(text)
        graph.add_node(pydot.Node(f"b{idx}", shape="box", label="\\n".join(lines)))

    for idx, block in enumerate(blocks):
        for to_offset in block["succ"]:
            dst = block_by_offset.get(to_offset)
            if dst is not None:
                graph.add_edge(pydot.Edge(f"b{idx}", f"b{dst}"))

    return graph.create_png()


def _split_basic_blocks(instructions):
    leaders = {instructions[0].offset}
    offsets = {ins.offset for ins in instructions}

    for i, ins in enumerate(instructions):
        target = _jump_target(ins)
        if target is not None and target in offsets:
            leaders.add(target)
        if "JUMP" in ins.opname and i + 1 < len(instructions):
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
    if op.startswith("JUMP"):
        return [target] if target is not None else []
    if next_offset is None:
        return []
    return [next_offset]


def _jump_target(ins):
    if isinstance(ins.argval, int):
        return ins.argval
    return None
