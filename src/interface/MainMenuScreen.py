from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QGridLayout,
)

from PyQt5.QtCore import Qt


class MainMenuScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        title_label = QLabel("Jamiron")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        main_layout.addLayout(grid_layout)

        self.login_button = QPushButton("로그인")
        grid_layout.addWidget(self.login_button, 0, 0)

        self.classified_folder_button = QPushButton("이동 폴더")
        grid_layout.addWidget(self.classified_folder_button, 0, 1)

        self.unclassified_folder_button = QPushButton("원본 폴더")
        grid_layout.addWidget(self.unclassified_folder_button, 1, 0, 1, 2)

        self.explore_button = QPushButton("폴더 탐색")
        self.explore_button.setEnabled(False)
        grid_layout.addWidget(self.explore_button, 2, 0, 1, 2)

        self.stop_button = QPushButton("탐색 중지")
        self.stop_button.setVisible(False)
        grid_layout.addWidget(self.stop_button, 3, 0, 1, 2)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setWordWrap(True)
        self.progress_label.setVisible(False)
        main_layout.addWidget(self.progress_label)
