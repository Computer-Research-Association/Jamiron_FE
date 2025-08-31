from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

class LoadingIndicator(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 60)
        self.dots = [(0, 0, 0) for _ in range(5)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(50)
        self.step = 0

    def updateAnimation(self):
        self.step = (self.step + 1) % 40
        for i in range(5):
            offset = (self.step + i * 8) % 40
            x = 30 + (offset * 240 / 40)
            opacity = max(0, 1 - abs(offset - 20) / 20)
            self.dots[i] = (x, opacity, 1 if offset < 20 else -1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for x, opacity, _ in self.dots:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, int(opacity * 255)))
            painter.drawEllipse(int(x), 15, 30, 30)
        painter.end()