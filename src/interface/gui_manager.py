import sys
import os
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QApplication,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from .styles import get_dark_theme, get_light_theme
import subprocess

class UIManager(QObject):
    year_changed = pyqtSignal(str)
    hakgi_changed = pyqtSignal(str)
    current_theme = "light"

    def __init__(self, app, coordinator):
        super().__init__()
        self.app = app
        self.coordinator = coordinator
        self.year = ""
        self.hakgi = ""
        self.selected_classes = []
        self.dialog = None

        if self.is_dark_mode():
            UIManager.current_theme = "dark"
            QApplication.instance().setStyleSheet(get_dark_theme())
        else:
            UIManager.current_theme = "light"
            QApplication.instance().setStyleSheet(get_light_theme())

        self._connect_signals()

        # 초기 학년도 및 학기 값 설정
        login_screen = self.app.main_window.login_screen
        self.set_year(login_screen.year_combo.currentText())
        self.set_hakgi(login_screen.hakgi_combo.currentText())

    def _connect_signals(self):
        # Coordinator -> UI
        self.coordinator.signals.show_screen.connect(self.show_screen)
        self.coordinator.signals.login_result.connect(self.on_login_result)
        self.coordinator.signals.class_selection_required.connect(self.show_class_selection)
        self.coordinator.signals.model_generation_complete.connect(self.on_model_generation_complete)
        self.coordinator.signals.main_menu_status.connect(self.update_main_menu_status)
        self.coordinator.signals.exploration_status.connect(self.update_exploration_status)
        self.coordinator.signals.classification_plan_ready.connect(self.show_classification_confirmation)
        self.coordinator.signals.request_classified_folder_selection.connect(self.prompt_for_classified_output_folder)
        self.coordinator.signals.progress.connect(self.thread_safe_update_progress)

        # UI -> Coordinator
        main_menu = self.app.main_window.main_menu_screen
        main_menu.login_button.clicked.connect(lambda: self.show_screen("login"))
        main_menu.classified_folder_button.clicked.connect(self.prompt_for_classified_output_folder)
        main_menu.unclassified_folder_button.clicked.connect(self.prompt_for_unclassified_input_folder)
        main_menu.explore_button.clicked.connect(self.coordinator.start_file_exploration)
        main_menu.stop_button.clicked.connect(self.coordinator.stop_file_exploration)

        login_screen = self.app.main_window.login_screen
        login_screen.login_button.clicked.connect(self.handle_login)
        login_screen.year_combo.currentTextChanged.connect(self.set_year)
        login_screen.hakgi_combo.currentTextChanged.connect(self.set_hakgi)

        # General UI
        self.app.main_window.theme_button.clicked.connect(self.toggle_theme)
        self.app.main_window.back_button.clicked.connect(lambda: self.show_screen("main_menu"))

    def show_screen(self, screen_name):
        screen_map = {
            "main_menu": 0,
            "login": 1,
            "progress": 2,
        }
        index = screen_map.get(screen_name)
        if index is not None:
            self.app.main_window.stacked_widget.setCurrentIndex(index)
            if screen_name == "main_menu":
                QTimer.singleShot(0, self.coordinator.request_main_menu_status_update)

    def handle_login(self):
        login_screen = self.app.main_window.login_screen
        # 1. 버튼을 즉시 비활성화하여 중복 클릭 방지
        login_screen.login_button.setEnabled(False)
        # 2. 프로그레스바와 메시지를 즉시 표시하여 피드백 제공
        self.update_progress("로그인 중...", 5)

        id_val = login_screen.id_input.text()
        pw_val = login_screen.pw_input.text()
        
        self.coordinator.login_session(id_val, pw_val)
        self.coordinator.login(id_val, pw_val, self.year, self.hakgi)

    def on_login_result(self, success, message):
        login_screen = self.app.main_window.login_screen
        login_screen.login_button.setEnabled(True)
        # 프로그레스바 값은 변경하지 않고 메시지만 업데이트 (-1 전달)
        self.thread_safe_update_progress(message, -1)

    def on_model_generation_complete(self):
        self.coordinator.request_main_menu_status_update()

    def update_main_menu_status(self, status_info):
        main_menu = self.app.main_window.main_menu_screen
        status_text = ""
        status_text += "<font color='green'>로그인 정보 있음</font><br>" if status_info["login_ok"] else "<font color='red'>로그인 정보 없음</font><br>"
        status_text += "<font color='green'>분류된 자료 저장 폴더 설정됨</font><br>" if status_info["classified_folder_ok"] else "<font color='red'>분류된 자료 저장 폴더 설정 안됨</font><br>"
        status_text += "<font color='green'>자료 원본 폴더 설정됨</font><br>" if status_info["unclassified_folder_ok"] else "<font color='red'>자료 원본 폴더 설정 안됨</font><br>"

        main_menu.status_label.setText(status_text)
        all_conditions_met = all(status_info.values())
        main_menu.explore_button.setEnabled(all_conditions_met)

    def update_exploration_status(self, is_running):
        main_menu = self.app.main_window.main_menu_screen
        main_menu.explore_button.setVisible(not is_running)
        main_menu.stop_button.setVisible(is_running)
        main_menu.progress_bar.setVisible(is_running)
        main_menu.progress_label.setVisible(is_running)

    def show_classification_confirmation(self, plan):
        dialog = QDialog(self.app.main_window)
        dialog.setWindowTitle("분류 계획 확인")
        layout = QVBoxLayout()

        tree = QTreeWidget()
        tree.setHeaderLabels(["원본 파일", "이동될 폴더"])
        for source, dest in plan.items():
            item = QTreeWidgetItem([os.path.basename(source), os.path.basename(dest)])
            tree.addTopLevelItem(item)
        layout.addWidget(tree)

        button_box = QDialogButtonBox()
        proceed_button = button_box.addButton("진행", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("취소", QDialogButtonBox.RejectRole)
        layout.addWidget(button_box)

        proceed_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.adjustSize()

        if dialog.exec_() == QDialog.Accepted:
            action = self.show_move_copy_dialog()
            self.coordinator.execute_classification(action)
        else:
            self.coordinator.cancel_classification()

    def set_year(self, year):
        self.year = year
        self.year_changed.emit(year)

    def set_hakgi(self, hakgi):
        if hakgi == 'Summer':
            hakgi = '3'
        elif hakgi == 'Winter':
            hakgi = '4'
        self.hakgi = hakgi
        self.hakgi_changed.emit(hakgi)

    def prompt_for_classified_output_folder(self):
        initial_path = self.app.settings.load_classified_output_folder_path() or "/"
        path = QFileDialog.getExistingDirectory(self.app.main_window, "분류될 파일 저장 폴더 선택", initial_path)
        if path:
            self.coordinator.set_classified_output_folder(path)

    def prompt_for_unclassified_input_folder(self):
        initial_path = self.app.settings.load_unclassified_input_folder_path() or "/"
        path = QFileDialog.getExistingDirectory(self.app.main_window, "분류할 원본 파일 폴더 선택", initial_path)
        if path:
            self.coordinator.set_unclassified_input_folder(path)

    def show_class_selection(self, classes_list):
        self.selected_classes = classes_list
        self.coordinator.confirm_class_selection(self.selected_classes)
        
    def toggle_all_classes(self, checkboxes, state, classes_list, button):
        if state:
            self.selected_classes = classes_list
        else:
            self.selected_classes = []
        
        for checkbox in checkboxes:
            checkbox.setChecked(state)

        button.setText("전체 해제" if state else "전체 선택")

    def toggle_class(self, class_data, state):
        # 전달된 class_data가 리스트인지 확인
        if not isinstance(class_data, list):
            return

        # 리스트(class_data)를 frozenset으로 변환하여 추가/삭제
        item_to_add = class_data
        if state == Qt.Checked:
            self.selected_classes.append(item_to_add)
        else:
            self.selected_classes.remove(item_to_add)
            
    def thread_safe_update_progress(self, msg, percent, label_id="progress_label", bar_id="progress_bar"):
        QTimer.singleShot(0, lambda: self.update_progress(msg, percent, label_id, bar_id))

    def update_progress(self, msg, percent, label_id="progress_label", bar_id="progress_bar"):
        main_window = self.app.main_window
        ui_map = {
            ("progress_label", "main_menu_progress_bar"): (main_window.main_menu_screen.progress_label, main_window.main_menu_screen.progress_bar),
            ("progress_label_new_screen", "progress_bar_new_screen"): (main_window.progress_screen.progress_label, main_window.progress_screen.progress_bar),
            ("progress_label", "progress_bar"): (main_window.login_screen.progress_label, main_window.login_screen.progress_bar),
        }
        label, bar = ui_map.get((label_id, bar_id), (None, None))
        if not label or not bar: return

        label.setText(msg)
        if percent >= 0: bar.setVisible(True)
        QApplication.processEvents()

    def toggle_theme(self):
        if UIManager.current_theme == "light":
            QApplication.instance().setStyleSheet(get_dark_theme())
            UIManager.current_theme = "dark"
        else:
            QApplication.instance().setStyleSheet(get_light_theme())
            UIManager.current_theme = "light"

    def show_move_copy_dialog(self):
        dialog = QDialog(self.app.main_window)
        dialog.setWindowTitle("파일 작업 선택")
        layout = QVBoxLayout()
        label = QLabel("파일을 복사하시겠습니까, 아니면 이동하시겠습니까?")
        layout.addWidget(label)

        button_box = QDialogButtonBox()
        copy_button = button_box.addButton("복사", QDialogButtonBox.AcceptRole)
        move_button = button_box.addButton("이동", QDialogButtonBox.AcceptRole)
        cancel_button = button_box.addButton("취소", QDialogButtonBox.RejectRole)
        layout.addWidget(button_box)

        copy_button.clicked.connect(lambda: dialog.done(1))
        move_button.clicked.connect(lambda: dialog.done(2))
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        result = dialog.exec_()
        if result == 1: return "copy"
        elif result == 2: return "move"
        else: return None

    @staticmethod
    def is_dark_mode():
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0
            except Exception:
                return False
        elif sys.platform == "darwin":
            try:
                result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], capture_output=True, text=True, check=True)
                return "Dark" in result.stdout.strip()
            except Exception:
                return False
        return False