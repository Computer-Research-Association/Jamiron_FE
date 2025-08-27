#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jamiron 애플리케이션 러너
GUI와 모든 기능들을 연결하고 초기화하는 중앙 컨트롤러
"""

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
from src.domain.classification.classifier_manager import ClassifierManager
from src.domain.classification.rule_based_classifier import RuleBasedClassifier
from src.domain.classification.ml_classifier import MLClassifier

from src.application.request_controller import LoginRequest


class MainApp:
    """메인 애플리케이션 클래스 - 모든 컴포넌트를 연결하고 관리"""

    def __init__(self):
        # PyQt5 애플리케이션 초기화
        self.app = QApplication(sys.argv)

        # 1. 스플래시 화면 이미지 설정
        splash_pix = QPixmap("src/asset/splash_img.png")

        # 2. QSplashScreen 인스턴스 생성
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.show()

        # 폰트 설정
        self._setup_fonts()

        # 핵심 컴포넌트 초기화 (의존성 순서 중요)
        self._initialize_components()

        # 컴포넌트 간 연결 설정
        self._connect_components()

        # UI 시그널 연결
        # UIManager에서 처리하므로 별도 호출 필요 없음

        # 테마 설정 및 UI 표시
        self._setup_theme_and_show()

    def _setup_fonts(self):
        """폰트 설정"""
        font_path = os.path.join("src", "asset", "malgun.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

    def _initialize_components(self):
        """핵심 컴포넌트들을 의존성 순서에 맞게 초기화"""
        # 1. 설정 관리자
        self.settings = ProjectSettings()

        # 2. 분류기 및 관리자 설정 (두 번째 코드 블록 로직 통합)
        # syllabus_collector에서 수집한 강의 계획서 데이터 로드
        # syllabus_data_list = self._load_syllabus_data()

        # # 분류기 인스턴스 생성
        # rule_classifier = RuleBasedClassifier(syllabus=syllabus_data_list)
        # ml_classifier = MLClassifier(syllabus=syllabus_data_list)

        # 분류 관리자 생성 (의존성 주입)
        # self.classifier_manager = ClassifierManager(
        #     rule_classifier=rule_classifier,
        #     ml_classifier=ml_classifier,
        #     settings=self.settings,
        # )

        # 3. 메인 윈도우 (UI 객체)
        self.main_window = GUIInterface(self)

        self.main_window.activateWindow()
        self.main_window.raise_()

        self.splash.finish(self.main_window)

        # 4. 워크플로우 코디네이터 (로직) - 수정된 부분
        # 생성된 ClassifierManager를 주입
        self.workflow_coordinator = WorkflowCoordinator(
            self.settings
        )

        # 5. UI 관리자 (UI와 로직 연결)
        self.ui_manager = UIManager(self, self.workflow_coordinator)

    def _load_syllabus_data(self):
        """syllabus.json에서 강의 계획서 데이터를 로드합니다."""
        syllabus_json_path = os.path.join("src", "data", "syllabus.json")
        try:
            with open(syllabus_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data:
                print("syllabus.json 파일이 비어있습니다. 빈 목록으로 시작합니다.")
                return []
            print(f"{syllabus_json_path}에서 {len(data)}개의 강의 계획서 로드 완료")
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"{syllabus_json_path} 로드 실패 ({e}). 빈 목록으로 시작합니다.")
            return []

    def _connect_components(self):
        """컴포넌트 간 참조 연결"""
        # UIManager와 Coordinator의 시그널을 통해 상호작용하므로 직접 연결 불필요
        pass

    def _connect_signals(self):
        """UI 요소의 시그널 연결"""
        # UIManager의 __init__에서 모두 처리
        print("UI 시그널은 UIManager에서 모두 연결됩니다.")

    def _setup_theme_and_show(self):
        """테마 설정 및 메인 윈도우 표시"""
        if self.ui_manager.is_dark_mode():
            self.app.setStyleSheet(get_dark_theme())
            self.ui_manager.current_theme = "dark"
        else:
            self.app.setStyleSheet(get_light_theme())
            self.ui_manager.current_theme = "light"

        self.main_window.show()
        print("메인 윈도우 표시 완료")

    def run(self):
        """애플리케이션 실행"""
        print("Jamiron 애플리케이션 시작")
        self._initialize_app_state()
        self.show_main_menu_screen()
        print("GUI 이벤트 루프 시작")
        sys.exit(self.app.exec_())
        
    def isSession(self):
        login_request = LoginRequest()
        session_path = self.settings.get_path("session_file")
        with open(session_path) as f:
            f.readline()
        login_request.login()

    def _initialize_app_state(self):
        """애플리케이션 초기 상태 설정"""
        try:
            login_data = self.settings.load_login_data()
            if login_data and login_data.get("id"):
                print(f"저장된 로그인 정보 로드: {login_data['id']}")
            self.workflow_coordinator.request_main_menu_status_update()
        except Exception as e:
            print(f"초기 상태 설정 오류: {e}")

    def show_login_screen(self):
        """로그인 화면 표시 요청"""
        self.ui_manager.show_screen("login")

    def show_main_menu_screen(self):
        """메인 메뉴 화면 표시 요청"""
        self.ui_manager.show_screen("main_menu")


def run_app():
    """애플리케이션 실행 함수 - 외부에서 호출되는 진입점"""
    try:
        print("=" * 50)
        print("Jamiron 파일 분류 시스템")
        print("=" * 50)
        main_app = MainApp()
        main_app.run()
    except Exception as e:
        print(f"💥 애플리케이션 실행 중 치명적 오류: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_app()
