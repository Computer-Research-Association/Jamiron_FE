import sys
import os
import json
from PyQt5.QtGui import QFontDatabase, QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from src.interface.gui_manager import UIManager
from src.interface.gui_interface import GUIInterface
from src.config.settings import ProjectSettings
from src.application.workflow_coordinator import WorkflowCoordinator
from src.interface.styles import get_light_theme, get_dark_theme
from src.application.request_controller import SessionRequest


class MainApp:
    def __init__(self):
        # PyQt5 애플리케이션 초기화
        self.app = QApplication(sys.argv)
        
        self.settings = ProjectSettings()
        
        self.session_status = False

        # 1. 스플래시 화면 이미지 설정
        splash_pix = QPixmap("src/asset/splash_img.png")
        
        self.session_path = ''
        
        # 2. QSplashScreen 인스턴스 생성
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.show()
        
        if self.isSession():
            self.session_status = True
        else:
            self.session_status = False
            
        self.settings.manage_session(self.session_status)

        # 폰트 설정
        self._setup_fonts()

        # 핵심 컴포넌트 초기화 (의존성 순서 중요)
        self._initialize_components()
        
        # 테마 설정 및 UI 표시
        self._setup_theme_and_show()

    def _setup_fonts(self):
        font_path = os.path.join("src", "asset", "malgun.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

    def _initialize_components(self):
        # 1. 설정 관리자
        
        self.settings.get_path("session_file")

        # 3. 메인 윈도우 (UI 객체)
        self.main_window = GUIInterface(self)

        self.main_window.activateWindow()
        self.main_window.raise_()

        self.splash.finish(self.main_window)

        self.workflow_coordinator = WorkflowCoordinator(
            self.settings
        )

        # 5. UI 관리자 (UI와 로직 연결)
        self.ui_manager = UIManager(self, self.workflow_coordinator)

    def _load_syllabus_data(self):
        syllabus_json_path = os.path.join("src", "data", "syllabus.json")
        try:
            with open(syllabus_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                return []
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return []

    def _setup_theme_and_show(self):
        if self.ui_manager.is_dark_mode():
            self.app.setStyleSheet(get_dark_theme())
            self.ui_manager.current_theme = "dark"
        else:
            self.app.setStyleSheet(get_light_theme())
            self.ui_manager.current_theme = "light"

        self.main_window.show()

    def run(self):
        self._initialize_app_state()
        self.show_main_menu_screen()
        sys.exit(self.app.exec_())
        
    def isSession(self):
        session_request = SessionRequest()
        self.session_path = self.settings.get_path("session_file")
        if os.path.isfile(self.session_path):
            with open(self.session_path) as f:
                session_id = f.readline()
            if session_request.login(session_id)[1]:
                return True
            else:
                return False
        else:
            return False

    def _initialize_app_state(self):
        try:
            self.workflow_coordinator.request_main_menu_status_update()
        except Exception as e:
            pass

    def show_login_screen(self):
        self.ui_manager.show_screen("login")

    def show_main_menu_screen(self):
        self.ui_manager.show_screen("main_menu")


def run_app():
    try:
        main_app = MainApp()
        main_app.run()
    except Exception as e:
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_app()
