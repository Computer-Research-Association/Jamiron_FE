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
        self.session_status = False

    def load_env_variables(self):
        load_dotenv()

    def init_paths(self):
        base_dir = os.path.join(os.getcwd(), "src")
        self.paths["base_dir"] = base_dir
        self.paths["data_dir"] = os.path.join(base_dir, "data")
        self.paths["config_file"] = os.path.join(
            base_dir, "data", "config.json")
        self.paths["session_file"] = os.path.join(base_dir, "data", "session_file.txt")
        self.paths["key_file"] = os.path.join(
            self.paths["data_dir"], "encryption.key")

        # 경로 폴더 자동 생성
        for key, path in self.paths.items():
            if key.endswith("_dir") and path:
                os.makedirs(path, exist_ok=True)

    def load_config_values(self):
        """
        기타 설정값 (분류 기준, 로깅 수준, 파일 감시 대상 경로 등)
        """
        self.config["allowed_extensions"] = [".pdf", ".ppt", ".pptx"]
        self.config["default_label"] = "미분류"
        self.config["rule_confidence_threshold"] = 0.8
    
    def manage_session(self, status):
        self.session_status = status

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

    def verify_password(self, plain_password, hashed_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def save_classified_output_folder_path(self, path):
        os.makedirs(self.paths["data_dir"], exist_ok=True)
        data = {"classified_output_folder_path": path}
        classified_output_file = os.path.join(
            self.paths["data_dir"], "classified_output_folder_path.json"
        )
        with open(classified_output_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_classified_output_folder_path(self):
        classified_output_file = os.path.join(
            self.paths["data_dir"], "classified_output_folder_path.json"
        )
        if os.path.exists(classified_output_file):
            with open(classified_output_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("classified_output_folder_path", "")
        return ""

    def save_unclassified_input_folder_path(self, path):
        os.makedirs(self.paths["data_dir"], exist_ok=True)
        data = {"unclassified_input_folder_path": path}
        unclassified_input_file = os.path.join(
            self.paths["data_dir"], "unclassified_input_folder_path.json"
        )
        with open(unclassified_input_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_unclassified_input_folder_path(self):
        unclassified_input_file = os.path.join(
            self.paths["data_dir"], "unclassified_input_folder_path.json"
        )
        if os.path.exists(unclassified_input_file):
            with open(unclassified_input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("unclassified_input_folder_path", "")
        return ""

    def get_path(self, key: str) -> str:
        return self.paths.get(key, "")

    def get_config(self, key: str):
        return self.config.get(key)