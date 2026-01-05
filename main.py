import sys
import os
import subprocess
import tempfile
import marshal
import dis

import qdarktheme
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout,
    QTreeWidget, QTreeWidgetItem,
    QFileDialog, QSplitter, QTabWidget,
    QToolBar, QStatusBar,
    QMessageBox
)
from PyQt6.QtCore import Qt

from src.file_utils import classify_pyc
from src.pyinstaller_utils import is_pyinstaller_bundle
from src.ui.code_editor import CodeEditor
from src.ui.syntax_highlighter import PythonHighlighter
from src.ui.bytecode_debugger import BytecodeDebugWindow
from src.reporting import collect_suspicious, export_html, export_txt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python RE Tool")
        self.resize(1600, 900)
        self.setup_ui()
        self.open_file()

    def setup_ui(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        dbg = toolbar.addAction("🐞 Bytecode Debug")
        dbg.triggered.connect(self.open_debugger)

        rep = toolbar.addAction("📄 Export report")
        rep.triggered.connect(self.export_report)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self.files = QTreeWidget()
        self.files.setHeaderLabels(["Files"])
        self.files.itemClicked.connect(self.load_file)

        left = QTabWidget()
        left.addTab(self.files, "Files")

        self.decomp = CodeEditor()
        self.disasm = CodeEditor()

        self.decomp_hl = PythonHighlighter(self.decomp.document())
        self.disasm_hl = PythonHighlighter(self.disasm.document())

        right = QTabWidget()
        right.addTab(self.decomp, "Decompilation")
        right.addTab(self.disasm, "Disassembly")

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([400, 1200])

        layout.addWidget(splitter)
        self.setStatusBar(QStatusBar())

    def open_debugger(self):
        if not hasattr(self, "current_code"):
            QMessageBox.warning(self, "Debugger", "No code loaded")
            return
        BytecodeDebugWindow(self.current_code).exec()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select file", "", "Python bytecode (*.pyc);;Executable (*)"
        )
        if not path:
            return

        self.files.clear()

        if path.endswith(".pyc"):
            self.add_file(path)
        elif is_pyinstaller_bundle(path):
            self.extract_pyinstaller(path)

    def add_file(self, path):
        item = QTreeWidgetItem([os.path.basename(path)])
        item.setData(0, Qt.ItemDataRole.UserRole, path)
        item.setForeground(0, classify_pyc(path))
        self.files.addTopLevelItem(item)

    def extract_pyinstaller(self, path):
        temp = tempfile.mkdtemp(prefix="pyi_")
        pyinst = os.path.join(os.path.dirname(__file__), "pyinstxtractor.py")
        subprocess.run([sys.executable, pyinst, path], cwd=temp)

        extracted = next(d for d in os.listdir(temp) if d.endswith("_extracted"))
        root = QTreeWidgetItem(self.files, [os.path.basename(path)])

        for r, _, files in os.walk(os.path.join(temp, extracted)):
            for f in files:
                if f.endswith(".pyc"):
                    full = os.path.join(r, f)
                    item = QTreeWidgetItem(root, [os.path.relpath(full, temp)])
                    item.setData(0, Qt.ItemDataRole.UserRole, full)
                    item.setForeground(0, classify_pyc(full))

    def load_file(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path:
            return

        self.current_file_path = path

        with open(path, "rb") as f:
            f.read(16)
            self.current_code = marshal.load(f)

        self.disasm.setPlainText(dis.Bytecode(self.current_code).dis())

        proc = subprocess.run(
            ["pycdc", path],
            capture_output=True,
            text=True
        )
        self.decomp.setPlainText(proc.stdout)

    def export_report(self):
        if not hasattr(self, "current_code"):
            QMessageBox.warning(self, "Report", "No file loaded")
            return

        report = collect_suspicious(self.current_code, self.current_file_path)

        if not report:
            QMessageBox.information(self, "Report", "No suspicious activity")
            return

        out, _ = QFileDialog.getSaveFileName(
            self,
            "Save report",
            "",
            "Text (*.txt)"
        )
        if not out:
            return

        if out.endswith(".html"):
            export_html(report, out)
        else:
            export_txt(report, out)

        QMessageBox.information(self, "Report", "Report saved")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
