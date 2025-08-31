import os
import sys
import shutil
import json


def get_resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, "asset", relative_path)


class FileHandler:
    def load_json(self, file_path: str, create_if_not_exist: bool = False) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            if create_if_not_exist:
                self.save_json({}, file_path)
                return {}
            return {}
        except json.JSONDecodeError:
            return {}

    def save_json(self, data: dict, file_path: str):
        try:
            self.create_directory_if_not_exists(os.path.dirname(file_path))
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass
        
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
            raise FileNotFoundError(f"파일 찾을 수 없음: {source_path}")

        self.create_directory_if_not_exists(destination_folder)
        filename = os.path.basename(source_path)
        destination_path = self._get_unique_path(destination_folder, filename)

        shutil.move(source_path, destination_path)
        return destination_path

    def copy_file(self, source_path: str, destination_folder: str) -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"파일 찾을 수 없음: {source_path}")

        self.create_directory_if_not_exists(destination_folder)
        filename = os.path.basename(source_path)
        destination_path = self._get_unique_path(destination_folder, filename)

        shutil.copy2(source_path, destination_path)
        return destination_path

    def create_directory_if_not_exists(self, dir_path: str):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

    def delete_file(self, file_path: str):
        try:
            os.remove(file_path)

        except OSError as e:
            pass
        
    def get_classes_list_from_json(self, syllabus_dir: str):
        if not os.path.exists(syllabus_dir):
            return []
        files = [f for f in os.listdir(syllabus_dir) if f.endswith(".json")]
        # 파일 수정 시간 순으로 정렬 (나중에 저장된 파일이 뒤로)
        files.sort(key=lambda f: os.path.getmtime(os.path.join(syllabus_dir, f)))

        result = []
        seen_subjects = set()
        for f in files:
            try:
                if "_" in f:
                    subject_name = f.split("_", 1)[1][:-5]
                else:
                    subject_name = f[
                        :-5
                    ]
                
                if subject_name not in seen_subjects:
                    result.append([os.path.join(syllabus_dir, f), subject_name])
                    seen_subjects.add(subject_name)

            except IndexError:
                if f[:-5] not in seen_subjects:
                    result.append([os.path.join(syllabus_dir, f), f[:-5]])
                    seen_subjects.add(f[:-5])

        return result

    def create_empty_class_folders(self, base_path, all_classes, selected_indices):
        selected_classes_to_create_folder = [
            all_classes[i] for i in range(len(all_classes)) if i in selected_indices
        ]
        for _, subject in selected_classes_to_create_folder:
            folder_path = os.path.join(base_path, subject)
            self.create_directory_if_not_exists(folder_path)