# src/application/setup.py
import os
import json
import re
import shutil

from src.config.settings import ProjectSettings
from src.utils.file_system.file_handler import FileHandler

from src.application.request_controller import SyllabusRequest

class SetupController:
    def __init__(self, settings: ProjectSettings):
        self.settings = settings
        self.file_handler = FileHandler()
        self.login_request = None
        self.collector = None
        self.classes_list = []

    def _cleanup_existing_syllabus(self, progress_callback=None):
        if progress_callback:
            progress_callback("기존 강의 계획서 데이터 정리 중...", 5)
        
        syllabus_dir = self.settings.get_path("syllabus_dir")
        if os.path.exists(syllabus_dir):
            for filename in os.listdir(syllabus_dir):
                file_path = os.path.join(syllabus_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    pass

        syllabus_json_path = self.settings.get_path("syllabus_file")
        if os.path.exists(syllabus_json_path):
            try:
                os.remove(syllabus_json_path)
            except OSError as e:
                pass

    def login_and_collect(self, session_id: str, user_id: str, password: str, year: str, hakgi: str, progress_callback=None):
        try:
            self._cleanup_existing_syllabus(progress_callback)
            
            self.login_request = SyllabusRequest(progress_callback=progress_callback)
            login_response = self.login_request.login(session_id, user_id, password, year, hakgi)
            login_success = login_response[0]
            login_msg = login_response[1]
            self.classes_list = login_response[2]
            # login_success = self.collector.login(user_id, password)
            if not login_success:
                return None

            self.classes_list = [list(d.values()) for d in self.classes_list]
            
            return self.classes_list

        except Exception as e:
            if progress_callback:
                progress_callback(f"오류 발생: {e}", 0)
            return None
        finally:
            if self.collector:
                self.collector.close()
                self.collector = None

    def _update_progress(self, msg, percent):
        self._emit_signal("progress", msg, percent, "progress_label", "progress_bar")

    def generate_model_from_selection(self, selected_indices: list, progress_callback=None):
        try:
            self._cleanup_unselected_syllabuses(selected_indices, progress_callback)
            if progress_callback: progress_callback("모든 처리 완료", 100)

        except Exception as e:
            if progress_callback: progress_callback(f"모델 생성 오류: {e}", 0)

    def _cleanup_unselected_syllabuses(self, selected_indices: list, progress_callback=None):
        if progress_callback: progress_callback("불필요한 강의 계획서 정리 중...", 10)
        syllabus_dir = self.settings.get_path("syllabus_dir")
        if not os.path.exists(syllabus_dir): return

        selected_filepaths = {self.classes_list[i][0] for i in selected_indices}
        all_syllabus_files = [os.path.join(syllabus_dir, f) for f in os.listdir(syllabus_dir) if f.endswith(".json")]

        for f_path in all_syllabus_files:
            if f_path not in selected_filepaths:
                try:
                    os.remove(f_path)
                except OSError as e:
                    pass

        self._update_main_syllabus_json(selected_indices, progress_callback)
        if progress_callback: progress_callback("강의 계획서 파일 정리 완료.", 30)

    def _update_main_syllabus_json(self, selected_indices: list, progress_callback=None):
        if progress_callback: progress_callback("syllabus.json 업데이트 중...", 40)
        syllabus_json_path = self.settings.get_path("syllabus_file")
        if not os.path.exists(syllabus_json_path): return

        with open(syllabus_json_path, "r", encoding="utf-8") as f:
            all_syllabuses = json.load(f)

        selected_titles = {self.classes_list[i][1] for i in selected_indices}
        selected_codes = set()
        for index in selected_indices:
            filepath = self.classes_list[index][0]
            filename = os.path.basename(filepath)
            code_match = re.search(r"[A-Z]{3}\\d{5}", filename)
            if code_match: selected_codes.add(code_match.group())

        filtered_syllabuses = [s for s in all_syllabuses if s.get("class_name") in selected_titles or s.get("class_code") in selected_codes]

        with open(syllabus_json_path, "w", encoding="utf-8") as f:
            json.dump(filtered_syllabuses, f, indent=4, ensure_ascii=False)
        if progress_callback: progress_callback("syllabus.json 업데이트 완료.", 50)

    def _prepare_model_data(self, selected_indices: list, progress_callback=None) -> list:
        if progress_callback: progress_callback("모델 학습 데이터 준비 중...", 60)
        selected_syllabus_data = []
        total_selected = len(selected_indices)

        for i, index in enumerate(selected_indices):
            subject_name = self.classes_list[index][1]
            filepath = self.classes_list[index][0]
            progress = 60 + int((i / total_selected) * 30) if total_selected > 0 else 60
            if progress_callback: progress_callback(f"데이터 처리: {subject_name}", progress)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    syllabus_data = json.load(f)
                content_parts = [
                    syllabus_data.get("class_name", ""), syllabus_data.get("objectives", ""),
                    syllabus_data.get("description", ""), syllabus_data.get("schedule", ""),
                ]
                full_content = " ".join(str(p) for p in content_parts if p).strip()
                # processed_content = self.classifier_manager._preprocess_text(full_content)
                processed_content = full_content
                if processed_content:
                    selected_syllabus_data.append((subject_name, processed_content))
            except Exception as e:
                pass
        return selected_syllabus_data

    def setup_folders(self, selected_indices: list, progress_callback=None):
        if progress_callback: progress_callback("출력 폴더 생성 중...", 98)
        classified_path = self.settings.load_classified_output_folder_path()
        if classified_path:
            self.file_handler.create_empty_class_folders(classified_path, self.classes_list, selected_indices)

    def on_classified_folder_selected_for_setup(self, path, selected_indices):
        self.settings.save_classified_output_folder_path(path)
        self.file_handler.create_empty_class_folders(path, self.classes_list, selected_indices)