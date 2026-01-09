import dis
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout,
    QListWidget, QTableWidget, QTableWidgetItem,
    QPushButton
)
from .code_editor import CodeEditor
from .syntax_highlighter import PythonHighlighter

class BytecodeVM:
    def __init__(self, codeobj):
        self.instructions = list(dis.get_instructions(codeobj))
        self.ip = 0
        self.stack = []
        self.locals = {}
        self.finished = False

    def step(self):
        if self.ip >= len(self.instructions):
            self.finished = True
            return

        ins = self.instructions[self.ip]
        op = ins.opname
        arg = ins.argval

        if op == "LOAD_CONST":
            self.stack.append(arg)
        elif op == "STORE_NAME":
            self.locals[arg] = self.stack.pop()
        elif op == "LOAD_NAME":
            self.stack.append(self.locals.get(arg))
        elif op == "BINARY_ADD":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif op == "POP_TOP":
            self.stack.pop()
        elif op == "RETURN_VALUE":
            self.finished = True

        self.ip += 1


class BytecodeDebugWindow(QDialog):
    def __init__(self, codeobj):
        super().__init__()
        self.setWindowTitle("Bytecode Debugger")
        self.resize(1100, 700)

        self.vm = BytecodeVM(codeobj)

        self.disasm = CodeEditor()
        self.disasm.setReadOnly(True)
        self.disasm_hl = PythonHighlighter(self.disasm.document())

        lines = [
            f"{ins.offset:04x} {ins.opname:<20} {ins.argrepr}"
            for ins in self.vm.instructions
        ]
        self.disasm.setPlainText("\n".join(lines))

        self.stack_view = QListWidget()
        self.locals_view = QTableWidget(0, 2)
        self.locals_view.setHorizontalHeaderLabels(["Name", "Value"])

        self.step_btn = QPushButton("Step")
        self.run_btn = QPushButton("Run")
        self.close_btn = QPushButton("Close")

        self.step_btn.clicked.connect(self.do_step)
        self.run_btn.clicked.connect(self.do_run)
        self.close_btn.clicked.connect(self.close)

        btns = QHBoxLayout()
        btns.addWidget(self.step_btn)
        btns.addWidget(self.run_btn)
        btns.addWidget(self.close_btn)

        right = QVBoxLayout()
        right.addWidget(self.stack_view)
        right.addWidget(self.locals_view)
        right.addLayout(btns)

        layout = QHBoxLayout(self)
        layout.addWidget(self.disasm, 3)
        layout.addLayout(right, 2)

        self.update_ui()

    def do_step(self):
        if not self.vm.finished:
            self.vm.step()
            self.update_ui()

    def do_run(self):
        while not self.vm.finished:
            self.vm.step()
        self.update_ui()

    def update_ui(self):
        if self.vm.ip < len(self.vm.instructions):
            self.disasm.highlight_line(self.vm.ip)

        self.stack_view.clear()
        for v in reversed(self.vm.stack):
            self.stack_view.addItem(repr(v))

        self.locals_view.setRowCount(len(self.vm.locals))
        for i, (k, v) in enumerate(self.vm.locals.items()):
            self.locals_view.setItem(i, 0, QTableWidgetItem(str(k)))
            self.locals_view.setItem(i, 1, QTableWidgetItem(repr(v)))
