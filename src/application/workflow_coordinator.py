# src/application/workflow_coordinator.py

import os
import threading
import math
import json
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool

from src.application.setup import SetupController
from src.application.workers import Worker
from src.config.settings import ProjectSettings
from src.domain.classification.classifier_manager import ClassifierManager
from src.utils.file_system.file_handler import FileHandler
from src.utils.file_system.file_extractor import FileExtractor
from src.utils.file_process.translator import TextTranslator
from src.utils.file_process.preprocessor import Preprocessor


class CoordinatorSignals(QObject):
    """WorkflowCoordinator와 UI 계층 간의 통신을 위한 시그널 집합"""
    # --- To UI ---
    show_screen = pyqtSignal(str)  # "login", "main_menu", "progress"
    login_result = pyqtSignal(bool, str)  # success, message
    class_selection_required = pyqtSignal(list)
    model_generation_complete = pyqtSignal()
    main_menu_status = pyqtSignal(dict)
    exploration_status = pyqtSignal(bool)  # is_running
    classification_plan_ready = pyqtSignal(dict)
    request_classified_folder_selection = pyqtSignal()
    syllabus_update_complete = pyqtSignal(bool, str) # success, message

    # --- Shared ---
    progress = pyqtSignal(str, int, str, str)

    # --- From SetupController to Coordinator ---
    login_finished_signal = pyqtSignal(bool)
    class_selection_required_signal = pyqtSignal(list)
    model_generation_finished_signal = pyqtSignal()


class WorkflowCoordinator(QObject):
    # __init__ 메서드 시그니처 수정
    def __init__(self, settings: ProjectSettings, classifier_manager: ClassifierManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.threadpool = QThreadPool()
        self.signals = CoordinatorSignals()

        self.file_handler = FileHandler()
        self.file_extractor = FileExtractor()
        self.preprocessor = Preprocessor()
        
        self.classifier_manager = classifier_manager

        self.setup_controller = SetupController(self.settings, self.classifier_manager)

        self.stop_event = threading.Event()
        self.processed_steps = 0

        self._connect_internal_signals()

    def _connect_internal_signals(self):
        self.signals.login_finished_signal.connect(self.on_login_finished)
        self.signals.class_selection_required_signal.connect(self.on_classes_received)

    def login(self, id_val, pw_val, year_val, hakgi_val):
        """사용자 로그인 시작"""
        if not all([id_val, pw_val, year_val, hakgi_val]):
            self.signals.login_result.emit(False, "모든 필드를 입력해주세요.")
            return

        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label", "progress_bar")

        worker = Worker(self.setup_controller.login_and_collect, id_val, pw_val, year_val, hakgi_val, progress_callback=progress_callback)
        
        worker.signals.result.connect(self.on_login_finished)
        worker.signals.error.connect(self.on_login_error)
        
        self.threadpool.start(worker)

    def on_login_finished(self, classes_list):
        """로그인 및 데이터 수집 성공 시 호출"""
        if classes_list:
            self.signals.login_result.emit(True, "로그인 성공. 강의 목록을 가져옵니다.")
            
            # Update classifiers with the new data
            syllabus_json_path = self.settings.get_path("syllabus_file")
            try:
                with open(syllabus_json_path, 'r', encoding='utf-8') as f:
                    new_syllabus_data = json.load(f)
                
                if not new_syllabus_data:
                    raise ValueError("수집된 강의 계획서 데이터가 비어있습니다.")

                self.classifier_manager.update_syllabus_data(new_syllabus_data)
                
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                error_msg = f"업데이트된 강의 계획서 파일을 불러오는 중 오류 발생: {e}"
                print(f"{error_msg}")

            self.signals.class_selection_required.emit(classes_list)
        else:
            self.signals.login_result.emit(False, "로그인에 실패했거나, 수집할 강의가 없습니다.")

    def on_login_error(self, error_tuple):
        print(f"로그인 오류: {error_tuple}")
        self.signals.login_result.emit(False, "로그인 중 오류가 발생했습니다.")

    def on_classes_received(self, classes_list):
        self.signals.class_selection_required.emit(classes_list)

    def confirm_class_selection(self, selected_indices):
        self.signals.show_screen.emit("progress")

        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label_new_screen", "progress_bar_new_screen")

        worker = Worker(self.setup_controller.generate_model_from_selection, selected_indices, progress_callback=progress_callback)
        worker.signals.finished.connect(lambda: self.on_model_generation_finished(selected_indices))
        self.threadpool.start(worker)

    def on_model_generation_finished(self, selected_indices):
        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label_new_screen", "progress_bar_new_screen")

        self.setup_controller.setup_folders(selected_indices, progress_callback=progress_callback)
        
        # Reload the pruned syllabus data and update the classifiers
        syllabus_json_path = self.settings.get_path("syllabus_file")
        try:
            with open(syllabus_json_path, 'r', encoding='utf-8') as f:
                pruned_syllabus_data = json.load(f)
            self.classifier_manager.update_syllabus_data(pruned_syllabus_data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERROR: {e}")

        self.signals.model_generation_complete.emit()

        classified_path = self.settings.load_classified_output_folder_path()
        if not classified_path:
            self.signals.request_classified_folder_selection.emit()
        else:
            self.signals.show_screen.emit("main_menu")

    def start_file_exploration(self):
        if not (self.classifier_manager and self.classifier_manager.rule_classifier and self.classifier_manager.ml_classifier):
            self.signals.progress.emit("오류: 분류 모델을 찾을 수 없습니다. 로그인부터 다시 진행해주세요.", 100, "progress_label", "main_menu_progress_bar")
            self.signals.exploration_status.emit(False)
            return

        unclassified_folder_path = self.settings.load_unclassified_input_folder_path()
        if not unclassified_folder_path:
            return

        self.signals.exploration_status.emit(True)
        self.stop_event.clear()
        scan_thread = threading.Thread(target=self._scan_and_classify, args=(unclassified_folder_path,))
        scan_thread.start()

    def stop_file_exploration(self):
        self.stop_event.set()

    def on_scan_finished(self):
        file_data_list = []
        material_file_path = self.settings.get_path("material_file")
        if os.path.exists(material_file_path):
            with open(material_file_path, 'r', encoding='utf-8') as f:
                file_data_list = json.load(f)

        if not file_data_list:
             self.signals.progress.emit("분류할 파일이 없거나 작업이 중단되었습니다.", 100, "progress_label", "main_menu_progress_bar")
             self.signals.exploration_status.emit(False)
             return

        classified_list = self.classifier_manager.run_pipeline(file_data_list)

        # 분류 결과 다시 저장 (필요하면)
        self.file_handler.save_json(classified_list, material_file_path)

        # 분류 계획 UI로 전달
        plan = self.classifier_manager.get_classification_plan()
        if not plan:
            self.signals.progress.emit("분류할 파일이 없거나 작업이 중단되었습니다.", 100, "progress_label", "main_menu_progress_bar")
            self.signals.exploration_status.emit(False)
            return
        self.signals.classification_plan_ready.emit(plan)

    def execute_classification(self, action):
        """UI로부터 받은 action으로 분류 계획을 실행"""
        if action:
            plan = self.classifier_manager.get_classification_plan()
            for source_path, dest_folder in plan.items():
                try:
                    if action == "move":
                        self.file_handler.move_file(source_path, dest_folder)
                    elif action == "copy":
                        self.file_handler.copy_file(source_path, dest_folder)
                except Exception as e:
                    print(f"파일 처리 오류: {source_path} -> {e}")
        else: # 작업 취소
            if hasattr(self.classifier_manager, 'clear_plan'):
                self.classifier_manager.clear_plan()
            self.signals.progress.emit("작업이 취소되었습니다.", 0, "progress_label", "main_menu_progress_bar")
        self.signals.exploration_status.emit(False)

    def cancel_classification(self):
        if hasattr(self.classifier_manager, 'clear_plan'):
            self.classifier_manager.clear_plan()
        self.signals.progress.emit("작업이 취소되었습니다.", 0, "progress_label", "main_menu_progress_bar")
        self.signals.exploration_status.emit(False)

    def _scan_and_classify(self, folder_path):
        def scan_files():
            for root, _, files in os.walk(folder_path):
                for file in files:
                    yield os.path.join(root, file)

        file_list = list(scan_files())
        total_files = len(file_list)
        self.classifier_manager.set_total_files(total_files)
        self.processed_steps = 0
        all_materials = []

        for file_path in file_list:
            if self.stop_event.is_set():
                break
            material_data = self._process_single_file(file_path)
            if material_data:
                all_materials.append(material_data)

        if not self.stop_event.is_set():
            material_file_path = self.settings.get_path("material_file")
            self.file_handler.save_json(all_materials, material_file_path)
            self.classifier_manager.classified_files = all_materials
            print(f"총 {len(all_materials)}개의 파일 정보를 material.json에 저장했습니다.")
            self.on_scan_finished()
        else:
            self.signals.exploration_status.emit(False)

    def _process_single_file(self, file_path):
        if self.stop_event.is_set():
            return None

        self.processed_steps += 1
        self._emit_progress(f"탐색: {os.path.basename(file_path)}")

        metadata = self.file_extractor.extract_metadata(file_path)
        full_content, first_content, translated_content = "", "", ""

        try:
            full_content = self.file_extractor.extract_text(file_path)
            if not isinstance(full_content, str):
                full_content = str(full_content)
            
            first_content = full_content[:500]

            if full_content and full_content.strip():
                translator = TextTranslator()
                translated_content = translator.translate_long_text(full_content)
            
        except Exception as e:
            print(f"ERROR: File processing error for {file_path}: {e}")
            
        material_data = {
            "file_path": file_path,
            "label": "unclassified",
            "all_content": translated_content,
            "first_content": first_content,
            "metadata": {
                "title": metadata.get("title"),
                "author": metadata.get("author")
            }
        }
        return material_data

    def _emit_progress(self, message):
        total_steps = self.classifier_manager.total_files
        percent = (self.processed_steps / total_steps) * 100 if total_steps > 0 else 0
        display_percent = math.ceil(percent)
        detailed_message = f"[{self.processed_steps}/{total_steps}] {message}"
        self.signals.progress.emit(
            detailed_message, display_percent, "progress_label", "main_menu_progress_bar"
        )

    def get_main_menu_status(self):
        login_data = self.settings.load_login_data()
        login_ok = bool(login_data and login_data.get("id"))
        classified_folder_path = self.settings.load_classified_output_folder_path()
        classified_folder_ok = bool(classified_folder_path)
        unclassified_folder_path = self.settings.load_unclassified_input_folder_path()
        unclassified_folder_ok = bool(unclassified_folder_path)
        return {
            "login_ok": login_ok,
            "classified_folder_ok": classified_folder_ok,
            "unclassified_folder_ok": unclassified_folder_ok,
        }

    def request_main_menu_status_update(self):
        """UI가 메인 메뉴 상태 업데이트를 요청할 때 호출"""
        status = self.get_main_menu_status()
        self.signals.main_menu_status.emit(status)

    def set_classified_output_folder(self, path):
        self.settings.save_classified_output_folder_path(path)
        self.request_main_menu_status_update()
        self.signals.show_screen.emit("main_menu")

    def set_unclassified_input_folder(self, path):
        self.settings.save_unclassified_input_folder_path(path)
        self.request_main_menu_status_update()