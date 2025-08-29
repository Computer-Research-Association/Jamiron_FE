from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QProgressBar,
    QLabel,
    QHBoxLayout
)
from PyQt5.QtCore import Qt

from src.interface.loadingBar import LoadingIndicator


class ProgressScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.loadingIndicator = LoadingIndicator()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # 수직 중앙 정렬
        layout.setSpacing(15)
        self.setLayout(layout)

        # 타이틀 레이블
        title_label = QLabel("파일 처리 중...")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 로딩 인디케이터를 위한 수평 레이아웃 (좌우 중앙 정렬)
        loading_layout = QHBoxLayout()
        loading_layout.setAlignment(Qt.AlignCenter)  # 좌우 중앙 정렬
        self.progress_bar = self.loadingIndicator
        self.progress_bar.setVisible(True)  # 기본적으로 표시
        loading_layout.addWidget(self.progress_bar)
        layout.addLayout(loading_layout)

        # 진행 상황 레이블
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setWordWrap(True)
        self.progress_label.setFixedHeight(120)
        layout.addWidget(self.progress_label)