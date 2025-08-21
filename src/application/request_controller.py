import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.environ.get('REQUEST_URL')

class LoginRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/login'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def login(self, user_id, password, year, hakgi):
        try:
            self.update_progress("로그인 시도 중...", 10)
            params = {
                'user_id': user_id,
                'password': password,
                'year': year,
                'semester': hakgi,
            }
            
            response = requests.post(self.uri, json=params, timeout=30)
            response.raise_for_status()

            res_data = response.json()
            
            msg = res_data.get("msg", "로그인 성공")
            percent = res_data.get("percent", 100)
            self.update_progress(msg, percent)

            return res_data.get("status") == 200

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
            self.update_progress(f"로그인 실패: {e.response.status_code}", 100)
            return False
        except requests.exceptions.RequestException as e:
            print(f"서버 연결 오류: {e}")
            self.update_progress("서버에 연결할 수 없습니다.", 100)
            return False
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            self.update_progress("알 수 없는 오류 발생.", 100)
            return False
        
class ClassifierRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/classifier'
        self.progress_callback = progress_callback
        
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def classify(self, file_data_list):
        try:
            self.update_progress("분류 작업 요청 중...", 5)
            
            # Assuming the server can handle the full list as a JSON body
            response = requests.post(self.uri, json=file_data_list, timeout=120)
            response.raise_for_status()

            res_data = response.json()

            # Since this is not a websocket, we can't get progress updates.
            # We'll just reflect the final state from the server's response.
            msg = res_data.get("msg", "분류 완료")
            percent = res_data.get("percent", 100)
            self.update_progress(msg, percent)
            
            # You might need to return the classified data from the response
            return res_data

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
            self.update_progress(f"분류 실패: {e.response.status_code}", 100)
            return None
        except requests.exceptions.RequestException as e:
            print(f"서버 연결 오류: {e}")
            self.update_progress("서버에 연결할 수 없습니다.", 100)
            return None
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            self.update_progress("알 수 없는 오류 발생.", 100)
            return None
