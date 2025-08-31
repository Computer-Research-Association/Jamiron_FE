from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QGridLayout,
    QLineEdit,
    QComboBox,
    QHBoxLayout
)

from PyQt5.QtCore import Qt
import datetime

from src.interface.loadingBar import LoadingIndicator

class LoginScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.loadingIndicator = LoadingIndicator()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # 수직 중앙 정렬
        self.setLayout(main_layout)

        # 타이틀 레이블
        title_label = QLabel("로그인")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 폼 레이아웃
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        main_layout.addLayout(form_layout)

        form_layout.addWidget(QLabel("ID:"), 0, 0)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디를 입력하세요")
        form_layout.addWidget(self.id_input, 0, 1)

        form_layout.addWidget(QLabel("PW:"), 1, 0)
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.pw_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.pw_input, 1, 1)

        form_layout.addWidget(QLabel("년도:"), 2, 0)
        current_year = datetime.datetime.now().year
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(current_year, 2010, -1)])
        form_layout.addWidget(self.year_combo, 2, 1)

        form_layout.addWidget(QLabel("학기:"), 3, 0)
        current_month = datetime.datetime.now().month
        if current_month <= 2:
            current_hakgi = "Winter"
        elif current_month <= 6:
            current_hakgi = "1"
        elif current_month <= 8:
            current_hakgi = "Summer"
        else:
            current_hakgi = "2"
        self.hakgi_combo = QComboBox()
        self.hakgi_combo.addItems(["1", "2", "Summer", "Winter"])
        index = self.hakgi_combo.findText(current_hakgi)
        if index >= 0:
            self.hakgi_combo.setCurrentIndex(index)
        form_layout.addWidget(self.hakgi_combo, 3, 1)

        # 로그인 버튼
        self.login_button = QPushButton("로그인")
        main_layout.addWidget(self.login_button)

        # 로딩 인디케이터를 위한 수평 레이아웃 (좌우 중앙 정렬)
        loading_layout = QHBoxLayout()
        loading_layout.setAlignment(Qt.AlignCenter)  # 좌우 중앙 정렬
        self.progress_bar = self.loadingIndicator
        self.progress_bar.setVisible(False)
        loading_layout.addWidget(self.progress_bar)
        main_layout.addLayout(loading_layout)

        # 진행 상황 레이블
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setWordWrap(True)
        self.progress_label.setFixedHeight(120)
        main_layout.addWidget(self.progress_label)

        # 폴더 선택 버튼
        self.select_folder_button = QPushButton("폴더 선택")
        self.select_folder_button.setVisible(False)
        main_layout.addWidget(self.select_folder_button)