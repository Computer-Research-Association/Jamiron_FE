import json
import os
from cryptography.fernet import Fernet
import bcrypt
from dotenv import load_dotenv


class ProjectSettings:
    def __init__(self):
        self.paths = {}
        self.config = {}
        self.load_env_variables()
        self.init_paths()
        self.load_config_values()
        self.key = self.manage_key()
        self.fernet = Fernet(self.key)

    def load_env_variables(self):
        """
        .env 파일을 불러와 환경 변수로 등록
        """
        load_dotenv()

    def init_paths(self):
        """
        주요 경로 설정 (data, models, logs 등)
        """
        base_dir = os.path.join(os.getcwd(), "src")
        self.paths["base_dir"] = base_dir
        self.paths["data_dir"] = os.path.join(base_dir, "data")
        self.paths["config_file"] = os.path.join(
            base_dir, "data", "config.json")
        self.paths["syllabus_dir"] = os.path.join(base_dir, "data", "syllabus")
        self.paths["model_dir"] = os.path.join(base_dir, "models")
        self.paths["log_dir"] = os.path.join(base_dir, "logs")
        self.paths["syllabus_file"] = os.path.join(
            base_dir, "data", "syllabus.json")
        self.paths["session_file"] = os.path.join(base_dir, "data", "session_file.txt")
        self.paths["key_file"] = os.path.join(
            self.paths["data_dir"], "encryption.key")
        self.paths["material_file"] = os.path.join(
            self.paths["data_dir"], "material.json")

        # 경로 폴더 자동 생성
        for key, path in self.paths.items():
            if key.endswith("_dir") and path:  # Only create non-empty directory paths
                os.makedirs(path, exist_ok=True)

    def load_config_values(self):
        """
        기타 설정값 (분류 기준, 로깅 수준, 파일 감시 대상 경로 등)
        """
        self.config["allowed_extensions"] = [".pdf", ".ppt", ".pptx"]
        self.config["default_label"] = "미분류"
        self.config["rule_confidence_threshold"] = 0.8

        # 번역 관련 설정
        self.config["translation_settings"] = {
            "save_results": True,  # 번역 결과 저장 여부
            "save_format": "both",  # "txt", "html", "both"
            "save_full_content": False,  # 전체 내용 저장 여부 (False면 1000자만)
            "chunk_size": 5000,  # 긴 텍스트 분할 기준 (문자 수)
            "chunk_delay": 0.5,  # 청크 간 대기 시간 (초)
            "max_retries": 3,  # 번역 실패 시 재시도 횟수
            "cleanup_on_start": True,  # 시작 시 이전 번역 결과 정리
        }

    def manage_key(self):
        key_file_path = self.paths["key_file"]
        if os.path.exists(key_file_path):
            with open(key_file_path, "rb") as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(key_file_path, "wb") as key_file:
                key_file.write(key)
        return key

    def save_login_data(self, id_val, pw_val, year_val, hakgi_val):
        """
        ID는 암호화하고 비밀번호는 해싱하여 로그인 데이터를 저장함.
        """
        # 1. ID 암호화
        encrypted_id = self.fernet.encrypt(
            id_val.encode("utf-8")).decode("utf-8")

        data = {
            "id": encrypted_id,
            "pw": "",  # 해싱된 비밀번호 저장
            "year": year_val,
            "hakgi": hakgi_val,
        }

        login_data_file = os.path.join(
            self.paths["data_dir"], "login_data.json")
        with open(login_data_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_login_data(self):
        """
        저장된 로그인 데이터를 로드하고 ID는 복호화하여 반환함.
        """
        login_data_file = os.path.join(
            self.paths["data_dir"], "login_data.json")
        if os.path.exists(login_data_file):
            try:
                with open(login_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # 1. ID 복호화
                    decrypted_id = self.fernet.decrypt(
                        data.get("id").encode("utf-8")
                    ).decode("utf-8")
                    return {
                        "id": decrypted_id,
                        "pw_hash": data.get("pw", ""),  # 해싱된 비밀번호 반환
                        "year": data.get("year", ""),
                        "hakgi": data.get("hakgi", ""),
                    }
            except Exception as e:
                print(f"로그인 데이터 로드 오류: {e}")
                return None
        return None

    def verify_password(self, plain_password, hashed_password):
        """
        평문 비밀번호와 해싱된 비밀번호를 비교하여 일치하는지 확인.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def save_classified_output_folder_path(self, path):
        """분류된 자료 저장 폴더 경로를 저장"""
        os.makedirs(self.paths["data_dir"], exist_ok=True)
        data = {"classified_output_folder_path": path}
        classified_output_file = os.path.join(
            self.paths["data_dir"], "classified_output_folder_path.json"
        )
        with open(classified_output_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_classified_output_folder_path(self):
        """분류된 자료 저장 폴더 경로를 로드"""
        classified_output_file = os.path.join(
            self.paths["data_dir"], "classified_output_folder_path.json"
        )
        if os.path.exists(classified_output_file):
            with open(classified_output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("classified_output_folder_path", "")
        return ""

    def save_unclassified_input_folder_path(self, path):
        """분류되지 않은 자료 입력 폴더 경로를 저장"""
        os.makedirs(self.paths["data_dir"], exist_ok=True)
        data = {"unclassified_input_folder_path": path}
        unclassified_input_file = os.path.join(
            self.paths["data_dir"], "unclassified_input_folder_path.json"
        )
        with open(unclassified_input_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_unclassified_input_folder_path(self):
        """분류되지 않은 자료 입력 폴더 경로를 로드"""
        unclassified_input_file = os.path.join(
            self.paths["data_dir"], "unclassified_input_folder_path.json"
        )
        if os.path.exists(unclassified_input_file):
            with open(unclassified_input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("unclassified_input_folder_path", "")
        return ""

    def save_ToBeSorted_path(self, path):
        os.makedirs(self.paths["data"], exist_ok=True)
        self.paths["ToBeSorted_dir"] = path
        data = {"ToBeSorted": path}
        with open(self.paths["config_file"], "w", encoding="utf-8") as f:
            json.dump(data, f)

    def save_ouput_path(self, path):
        os.makedirs(self.paths["data"], exist_ok=True)
        data = {"output_dir": path}
        with open(self.paths["config_file"], "w", encoding="utf-8") as f:
            json.dump(data, f)

    def get_path(self, key: str) -> str:
        return self.paths.get(key, "")

    def get_config(self, key: str):
        return self.config.get(key)

    def save_translation_settings(self, settings):
        """번역 설정을 저장"""
        os.makedirs(self.paths["data_dir"], exist_ok=True)
        translation_settings_file = os.path.join(
            self.paths["data_dir"], "translation_settings.json"
        )
        with open(translation_settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def load_translation_settings(self):
        """번역 설정을 로드"""
        translation_settings_file = os.path.join(
            self.paths["data_dir"], "translation_settings.json"
        )
        if os.path.exists(translation_settings_file):
            try:
                with open(translation_settings_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    # 기본 설정과 병합
                    default_settings = self.config["translation_settings"]
                    default_settings.update(saved_settings)
                    return default_settings
            except Exception as e:
                print(f"번역 설정 로드 오류: {e}")
        return self.config["translation_settings"]

    def get_translation_setting(self, key, default=None):
        """특정 번역 설정값을 반환"""
        settings = self.load_translation_settings()
        return settings.get(key, default)
