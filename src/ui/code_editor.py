from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QFont, QPainter, QColor, QTextCharFormat
from PyQt6.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("JetBrains Mono", 10))
        self.line_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_area_width)
        self.updateRequest.connect(self.update_line_area)
        self.update_line_area_width(0)

    def line_number_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_area_width(self, _):
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def update_line_area(self, rect, dy):
        if dy:
            self.line_area.scroll(0, dy)
        else:
            self.line_area.update(0, rect.y(), self.line_area.width(), rect.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_width(), cr.height())
        )

    def paint_line_numbers(self, event):
        painter = QPainter(self.line_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(
            self.contentOffset()
        ).top()

        while block.isValid() and top <= event.rect().bottom():
            painter.setPen(QColor("#888"))
            painter.drawText(
                0, int(top),
                self.line_area.width() - 4,
                int(self.fontMetrics().height()),
                Qt.AlignmentFlag.AlignRight,
                str(number + 1)
            )
            block = block.next()
            top += self.blockBoundingRect(block).height()
            number += 1

    def highlight_line(self, line_no, color=QColor("#264F78")):
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(color)
        sel.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)

        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(
            cursor.MoveOperation.Down,
            cursor.MoveMode.MoveAnchor,
            line_no
        )

        sel.cursor = cursor
        self.setExtraSelections([sel])
