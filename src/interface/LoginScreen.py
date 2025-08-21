from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QGridLayout,
    QLineEdit,
    QComboBox
)

from PyQt5.QtCore import Qt
import datetime

class LoginScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        title_label = QLabel("로그인")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

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
        index = self.hakgi_combo.findText(current_hakgi)
        self.hakgi_combo.setCurrentIndex(index)
        self.hakgi_combo.addItems(["1", "2", "Summer", "Winter"])
        form_layout.addWidget(self.hakgi_combo, 3, 1)
        index = self.hakgi_combo.findText(current_hakgi)
        self.hakgi_combo.setCurrentIndex(index)

        self.login_button = QPushButton("로그인")
        main_layout.addWidget(self.login_button)

        self.load_login_data()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setWordWrap(True)
        self.progress_label.setFixedHeight(120)
        main_layout.addWidget(self.progress_label)

        self.select_folder_button = QPushButton("폴더 선택")
        self.select_folder_button.setVisible(False)
        main_layout.addWidget(self.select_folder_button)

    def load_login_data(self):
        login_data = self.app.settings.load_login_data()
        if login_data:
            self.id_input.setText(login_data.get("id", ""))
            
            year = str(login_data.get("year", ""))
            if year in [self.year_combo.itemText(i) for i in range(self.year_combo.count())]:
                self.year_combo.setCurrentText(year)
            
            hakgi = login_data.get("hakgi", "")
            if hakgi in [self.hakgi_combo.itemText(i) for i in range(self.hakgi_combo.count())]:
                self.hakgi_combo.setCurrentText(hakgi)
