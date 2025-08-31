import os
import threading
import math
import json
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool

from src.application.setup import SetupController
from src.application.workers import Worker
from src.application.request_controller import ClassifierRequest
from src.config.settings import ProjectSettings
from src.utils.file_system.file_handler import FileHandler
from src.utils.file_system.file_extractor import FileExtractor
from src.utils.file_process.translator import TextTranslator
from src.utils.file_process.preprocessor import Preprocessor

from src.application.request_controller import UserRequest
from src.application.request_controller import LoginRequest


class CoordinatorSignals(QObject):
    show_screen = pyqtSignal(str)  # "login", "main_menu", "progress"
    login_result = pyqtSignal(bool, str)  # success, message
    class_selection_required = pyqtSignal(list)
    semester_selection_required = pyqtSignal(list)
    model_generation_complete = pyqtSignal()
    main_menu_status = pyqtSignal(dict)
    exploration_status = pyqtSignal(bool)  # is_running
    classification_plan_ready = pyqtSignal(dict)
    request_classified_folder_selection = pyqtSignal()
    syllabus_update_complete = pyqtSignal(bool, str) # success, message

    progress = pyqtSignal(str, int, str, str)

    login_finished_signal = pyqtSignal(bool)
    class_selection_required_signal = pyqtSignal(list)
    semester_selection_required_signal = pyqtSignal(list)
    model_generation_finished_signal = pyqtSignal()


class WorkflowCoordinator(QObject):
    def __init__(self, settings: ProjectSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.threadpool = QThreadPool()
        self.signals = CoordinatorSignals()

        self.file_handler = FileHandler()
        self.file_extractor = FileExtractor()
        self.preprocessor = Preprocessor()
        self.classifier_request = None
        
        self.setup_controller = SetupController(self.settings)

        self.stop_event = threading.Event()
        self.processed_steps = 0
        
        self.login_request = LoginRequest()
        
        self.user_id = ''
        self.year = ''
        self.hakgi = ''
        self.session_id = ''
        
        self.isLogin = False
        
        self.classified_list = []

        self._connect_internal_signals()
        
    def login_session(self, user_id, password):
        if self.get_session_id() and self.settings.session_status:
            pass
        else:
            session_response = self.login_request.login(user_id, password)
            if session_response[0] and session_response[1]:
                session_path = self.settings.get_path("session_file")
                with open(session_path, "w") as f:            
                    f.write(session_response[2])
            else:
                print("오류")
        
    def get_session_id(self):
        self.session_path = self.settings.get_path("session_file")
        if os.path.isfile(self.session_path):
            return self.file_extractor.extract_one_page(self.session_path)
        else:
            return ""
        
    def get_classification_plan(self, classified_files):
        plan = {}
            
        def get_output_folder_for_label(label):
            base_path = self.settings.load_classified_output_folder_path()
            if not base_path:
                base_path = "classified"
            return os.path.join(base_path, label)
            
        for file_data in classified_files:
            label = file_data.get('label')
            if label and label != 'unclassified':
                plan[file_data['file_name']] = get_output_folder_for_label(label)
        return plan

    def clear_plan(self):
        self.classified_files = []

    def _connect_internal_signals(self):
        self.signals.login_finished_signal.connect(self.on_login_finished)
        self.signals.class_selection_required_signal.connect(self.on_classes_received)

    def login(self, id_val, pw_val, year_val, hakgi_val):
        if not all([id_val, pw_val, year_val, hakgi_val]):
            self.signals.login_result.emit(False, "모든 필드를 입력해주세요.")
            return

        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label", "progress_bar")
        
        self.user_id = id_val
        self.year = year_val
        self.hakgi = hakgi_val
        self.session_id = self.get_session_id()
        
        worker = Worker(self.setup_controller.login_and_collect, self.session_id, id_val, pw_val, year_val, hakgi_val, progress_callback=progress_callback)
        
        worker.signals.result.connect(self.on_login_finished)
        worker.signals.error.connect(self.on_login_error)
        
        self.threadpool.start(worker)
        self.request_main_menu_login_status()

    def on_login_finished(self, classes_list):
        if classes_list:
            self.signals.login_result.emit(True, "로그인 성공. 강의 목록을 가져옵니다.")
            
            classes_list = [list(d) for d in classes_list]

            self.signals.class_selection_required.emit(classes_list)
        else:
            self.signals.login_result.emit(False, "로그인에 실패했거나, 수집할 강의가 없습니다.")

    def on_login_error(self, error_tuple):
        self.signals.login_result.emit(False, "로그인 중 오류가 발생했습니다.")

    def on_classes_received(self, classes_list):
        self.signals.class_selection_required.emit(classes_list)

    def confirm_class_selection(self, selected_indices):
        syllabuses_data = {}
        
        for item in selected_indices:
            class_list = list(item)
            syllabus_dict = {class_list[0] : class_list[1]}
            
            syllabuses_data.update(syllabus_dict)
        
        self.signals.show_screen.emit("progress")

        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label_new_screen", "progress_bar_new_screen")
        
        self.user_request = UserRequest(progress_callback=progress_callback)
        
        self.session_id = self.get_session_id()
        
        user_response = self.user_request.post_data(self.session_id, self.user_id, syllabuses_data, self.year, self.hakgi)
        
        if not user_response:
            return None
        
        worker = Worker(self.setup_controller.generate_model_from_selection, selected_indices, progress_callback=progress_callback)
        
        worker.signals.finished.connect(lambda: self.on_class_selection_finised(selected_indices))

        self.threadpool.start(worker)

    def on_class_selection_finised(self, selected_indices):
        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label_new_screen", "progress_bar_new_screen")

        self.setup_controller.setup_folders(selected_indices, progress_callback=progress_callback)
        

        self.signals.model_generation_complete.emit()

        classified_path = self.settings.load_classified_output_folder_path()
        if not classified_path:
            self.signals.request_classified_folder_selection.emit()
        else:
            self.signals.show_screen.emit("main_menu")

    def start_file_exploration(self):
        unclassified_folder_path = self.settings.load_unclassified_input_folder_path()
        if not unclassified_folder_path:
            return

        self.signals.exploration_status.emit(True)
        self.stop_event.clear()
        scan_thread = threading.Thread(target=self._scan_and_classify, args=(unclassified_folder_path,))
        scan_thread.start()

    def stop_file_exploration(self):
        self.stop_event.set()

    def on_scan_finished(self, file_data, progress_callback=None):
        file_data_list = file_data
        
        if not file_data_list:
             self.signals.progress.emit("분류할 파일이 없거나 작업이 중단되었습니다.", 100, "progress_label", "main_menu_progress_bar")
             self.signals.exploration_status.emit(False)
             return
        self.classifier_request = ClassifierRequest(progress_callback=progress_callback)
        
        self.session_id = self.get_session_id()
        classified_list = self.classifier_request.classify(self.session_id, self.user_id, self.year, self.hakgi, file_data_list)
        
        if classified_list == False:
            return
        
        self.classified_list = classified_list
        
        # 분류 계획 UI로 전달 
        plan = self.get_classification_plan(self.classified_list)
        if not plan:
            self.signals.progress.emit("분류할 파일이 없거나 작업이 중단되었습니다.", 100, "progress_label", "main_menu_progress_bar")
            self.signals.exploration_status.emit(False)
            return
        self.signals.classification_plan_ready.emit(plan)

    def execute_classification(self, action):
        if action:
            plan = self.get_classification_plan(self.classified_list)
            data_path = self.settings.load_unclassified_input_folder_path()
            for source_path, dest_folder in plan.items():
                try:
                    if action == "move":
                        self.file_handler.move_file(data_path+'/'+source_path, dest_folder)
                    elif action == "copy":
                        self.file_handler.copy_file(data_path+'/'+source_path, dest_folder)
                except Exception as e:
                    pass
        else:
            self.clear_plan()
            self.signals.progress.emit("작업이 취소되었습니다.", 0, "progress_label", "main_menu_progress_bar")
        self.signals.exploration_status.emit(False)

    def cancel_classification(self):
        self.clear_plan()
        self.signals.progress.emit("작업이 취소되었습니다.", 0, "progress_label", "main_menu_progress_bar")
        self.signals.exploration_status.emit(False)

    def _scan_and_classify(self, folder_path):
        def progress_callback(msg, percent):
            self.signals.progress.emit(msg, percent, "progress_label", "progress_bar")
            
        def scan_files():
            for root, _, files in os.walk(folder_path):
                for file in files:
                    yield os.path.join(root, file)

        file_list = list(scan_files())
        self.processed_steps = 0
        all_materials = []

        for file_path in file_list:
            if self.stop_event.is_set():
                break
            material_data = self._process_single_file(file_path)
            if material_data:
                all_materials.append(material_data)
        if not self.stop_event.is_set():
            file_data = all_materials
            
            self.on_scan_finished(file_data, progress_callback=progress_callback)
        else:
            self.signals.exploration_status.emit(False)

    def _process_single_file(self, file_path):
        if self.stop_event.is_set():
            return None

        self.processed_steps += 1

        full_content, first_content, translated_content = "", "", ""

        try:
            full_content = self.file_extractor.extract_text(file_path)
            if not isinstance(full_content, str):
                full_content = str(full_content)
            
            first_content = full_content[:500]

            if full_content and full_content.strip():
                translator = TextTranslator()
                translated_content = translator.translate_long_text(full_content)
                preprocessed_content = self.preprocessor.preprocess_text(translated_content)
            
        except Exception as e:
            pass
            
        material_data = {
            "file_name": os.path.basename(file_path),
            "label": "unclassified",
            "ml_content": preprocessed_content,
            "rule_based_content": first_content,
        }
        return material_data

    def get_main_menu_status(self, isLogin):
        login_ok = isLogin
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
        status = self.get_main_menu_status(self.isLogin)
        self.signals.main_menu_status.emit(status)
        
    def request_main_menu_login_status(self):
        self.isLogin = True
        status = self.get_main_menu_status(self.isLogin)
        self.request_main_menu_status_update()
        self.signals.main_menu_status.emit(status)

    def set_classified_output_folder(self, path):
        self.settings.save_classified_output_folder_path(path)
        self.request_main_menu_status_update()
        self.signals.show_screen.emit("main_menu")

    def set_unclassified_input_folder(self, path):
        self.settings.save_unclassified_input_folder_path(path)
        self.request_main_menu_status_update()