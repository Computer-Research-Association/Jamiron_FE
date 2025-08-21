import os
import sys
import shutil
import json


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Fallback for development environment
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, "asset", relative_path)


class FileHandler:
    def load_json(self, file_path: str, create_if_not_exist: bool = False) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            if create_if_not_exist:
                print(
                    f"[정보] '{os.path.basename(file_path)}' 파일을 찾을 수 없어 새로 생성합니다."
                )
                self.save_json({}, file_path)
                return {}
            print(f"[오류] JSON 파일을 찾을 수 없습니다: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"[오류] JSON 파일의 형식이 올바르지 않습니다: {file_path}")
            return {}

    def save_json(self, data: dict, file_path: str):
        try:
            self.create_directory_if_not_exists(os.path.dirname(file_path))
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[오류] JSON 파일 저장 실패: {file_path} - {e}")

    def _get_unique_path(self, destination_folder: str, filename: str) -> str:
        destination_path = os.path.join(destination_folder, filename)
        if not os.path.exists(destination_path):
            return destination_path

        name, ext = os.path.splitext(filename)
        count = 1
        while True:
            new_filename = f"{name}_{count}{ext}"
            new_destination_path = os.path.join(destination_folder, new_filename)
            if not os.path.exists(new_destination_path):
                return new_destination_path
            count += 1

    def move_file(self, source_path: str, destination_folder: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        self.create_directory_if_not_exists(destination_folder)
        filename = os.path.basename(source_path)
        destination_path = self._get_unique_path(destination_folder, filename)

        shutil.move(source_path, destination_path)
        print(f"파일 이동: {source_path} -> {destination_path}")
        return destination_path

    def copy_file(self, source_path: str, destination_folder: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        self.create_directory_if_not_exists(destination_folder)
        filename = os.path.basename(source_path)
        destination_path = self._get_unique_path(destination_folder, filename)

        shutil.copy2(source_path, destination_path)
        print(f"파일 복사: {source_path} -> {destination_path}")
        return destination_path

    def create_directory_if_not_exists(self, dir_path: str):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            print(f"디렉토리 생성: {dir_path}")

    def delete_file(self, file_path: str):
        try:
            os.remove(file_path)
            print(f"파일 삭제: {file_path}")
        except OSError as e:
            print(f"파일 삭제 오류: {e}")

    def get_classes_list_from_json(self, syllabus_dir: str):
        """data/syllabus 디렉토리에서 ".json"로 끝나는 파일 필터링"""
        if not os.path.exists(syllabus_dir):
            return []
        files = [f for f in os.listdir(syllabus_dir) if f.endswith(".json")]
        # 파일 수정 시간 순으로 정렬 (나중에 저장된 파일이 뒤로)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(syllabus_dir, f)))

        result = []
        seen_subjects = set()
        for f in files:
            try:
                # 파일명에서 과목명 추출: "25-1_과목명.json" -> "과목명"
                if "_" in f:
                    subject_name = f.split("_", 1)[1][:-5]  # .json 확장자 제거
                else:
                    subject_name = f[
                        :-5
                    ]  # 언더스코어가 없으면 전체 파일명에서 .json만 제거
                
                if subject_name not in seen_subjects:
                    result.append([os.path.join(syllabus_dir, f), subject_name])
                    seen_subjects.add(subject_name)

            except IndexError:
                # 파싱 실패 시 파일명 그대로 사용
                print(f"파일명 파싱 실패: {f}")
                if f[:-5] not in seen_subjects:
                    result.append([os.path.join(syllabus_dir, f), f[:-5]])
                    seen_subjects.add(f[:-5])

        return result

    def create_empty_class_folders(self, base_path, all_classes, selected_indices):
        """사용자가 선택한 과목의 폴더를 지정된 경로에 생성합니다."""
        selected_classes_to_create_folder = [
            all_classes[i] for i in range(len(all_classes)) if i in selected_indices
        ]
        for _, subject in selected_classes_to_create_folder:
            folder_path = os.path.join(base_path, subject)
            self.create_directory_if_not_exists(folder_path)