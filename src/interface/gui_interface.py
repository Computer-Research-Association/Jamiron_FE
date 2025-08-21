from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from .MainMenuScreen import MainMenuScreen
from .LoginScreen import LoginScreen
from .ProgressScreen import ProgressScreen
from src.utils.file_system.file_handler import get_resource_path


class GUIInterface(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Jamiron")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Top bar for theme toggle and back buttons
        top_bar_layout = QHBoxLayout()

        # Back button
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("src/asset/icon/back-arrow.png"))
        self.back_button.setFixedSize(40, 40)
        self.back_button.setIconSize(self.back_button.size())
        # back_button.clicked.connect(self.app.show_main_menu_screen)
        top_bar_layout.addWidget(self.back_button)

        top_bar_layout.addStretch()

        # Theme toggle button
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon("src/asset/icon/dark-theme.png"))
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setIconSize(self.theme_button.size())
        # theme_button.clicked.connect(self.app.ui_manager.toggle_theme)
        top_bar_layout.addWidget(self.theme_button)

        main_layout.addLayout(top_bar_layout)

        self.stacked_widget = QStackedWidget()
        self.main_menu_screen = MainMenuScreen(self.app)
        self.login_screen = LoginScreen(self.app)
        self.progress_screen = ProgressScreen(self.app)

        self.stacked_widget.addWidget(self.main_menu_screen)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.progress_screen)

        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setFixedSize(800, 800)
