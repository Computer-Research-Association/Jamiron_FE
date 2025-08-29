import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.environ.get('REQUEST_URL')

class SessionRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/session-check'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def login(self, session_id):
        try:
            self.update_progress("로그인 시도 중...", 10)
            params = {
                'session_id': session_id
            }
            
            response = requests.get(self.uri, headers=params)
            response.raise_for_status()

            res_data = response.json()
            
            # msg = res_data.get("msg", "로그인 성공")
            # percent = res_data.get("percent", 100)
            message = res_data.get("message", "")
            print(message)
            # self.update_progress(msg, percent)

            return [res_data.get("status") == 200, message == "세션 있음"]

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생 SessionRequest: {e.response.status_code} - {e.response.text}")
            self.update_progress(f"로그인 실패: {e.response.status_code}", 100)
            return [False, False]
        except requests.exceptions.RequestException as e:
            print(f"서버 연결 오류: {e}")
            self.update_progress("서버에 연결할 수 없습니다.", 100)
            return [False, False]
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            self.update_progress("알 수 없는 오류 발생.", 100)
            return [False, False]
        
class LoginRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/login'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def login(self, user_id, password):
        try:
            self.update_progress("로그인 시도 중...", 10)
            params = {
                'username': user_id,
                'password': password,
            }
            
            response = requests.post(self.uri, json=params)
            response.raise_for_status()

            res_data = response.json()
            
            # msg = res_data.get("msg", "로그인 성공")
            # percent = res_data.get("percent", 100)
            message = res_data.get("message", "")
            session_id = res_data.get("session_id", "")
            # self.update_progress(msg, percent)
            
            print(res_data)

            return [res_data.get("status") == 200, message == "로그인 성공.", session_id]

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생 LoginRequest: {e.response.status_code} - {e.response.text}")
            self.update_progress(f"로그인 실패: {e.response.status_code}", 100)
            return [False, False, ""]
        except requests.exceptions.RequestException as e:
            print(f"서버 연결 오류: {e}")
            self.update_progress("서버에 연결할 수 없습니다.", 100)
            return [False, False, ""]
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            self.update_progress("알 수 없는 오류 발생.", 100)
            return [False, False, ""]
        
class SyllabusRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/login'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def login(self, session_id, user_id, password, year, hakgi):
        try:
            self.update_progress("로그인 시도 중...", 10)
            params = {
                'username': user_id,
                'password': password,
                'year': year,
                'semester': hakgi,
            }
            
            print(params, session_id)
            
            response = requests.post(self.uri, headers={
                'session_id': session_id
            }, json=params)
            response.raise_for_status()

            res_data = response.json()
            
            # msg = res_data.get("msg", "로그인 성공")
            # percent = res_data.get("percent", 100)
            message = res_data.get("message", "")
            syllabuses = res_data.get("syllabuses", "")
            # self.update_progress(msg, percent)

            return [res_data.get("status") == 200, message, syllabuses]

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생 SyllabusRequest: {e.response.status_code} - {e.response.text}")
            self.update_progress(f"로그인 실패: {e.response.status_code}", 100)
            return [False, "", ""]
        except requests.exceptions.RequestException as e:
            print(f"서버 연결 오류: {e}")
            self.update_progress("서버에 연결할 수 없습니다.", 100)
            return [False, "", ""]
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            self.update_progress("알 수 없는 오류 발생.", 100)
            return [False, "", ""]
        
class UserRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/user'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def post_data(self, session_id, user_id, syllabuses_data, year, hakgi):
        try:
            params = {
                'username': user_id,
                'syllabuses': syllabuses_data,
                'year': year,
                'semester': hakgi,
            }
            
            response = requests.post(self.uri, headers={'session_id':session_id}, json=params)
            response.raise_for_status()

            res_data = response.json()
            
            print("rs",res_data)
            
            return res_data.get("status") == 200

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 오류 발생 UserRequest: {e.response.status_code} - {e.response.text}")
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
        self.uri = URL + '/api/classifier/classify'
        self.progress_callback = progress_callback
        
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    def classify(self, session_id, user_id, year, hakgi, file_data_list):
        try:
            self.update_progress("분류 작업 요청 중...", 5)
            
            params = {
                'username': user_id,
                'year': year,
                'semester': hakgi,
            }
            
            # file_data_list = file_data_list[0]
            
            # payload = [{
            #     'file_name': file_data_list['file_name'],
            #     'ml_content': file_data_list['ml_content'],
            #     'rule_based_content':  file_data_list['rule_based_content'],
            #     'label': 'unclassified'
            # }]
            
            payload = file_data_list
            
            # print(payload)
            
            response = requests.post(self.uri, headers={'session_id':session_id},  params=params, json=payload)
            response.raise_for_status()

            res_data = response.json()
            
            # print(res_data)
            
            msg = res_data.get("msg", "분류 완료")
            percent = res_data.get("percent", 100)
            self.update_progress(msg, percent)
            
            # print(res_data.get('file_data_list'))
            
            return res_data.get('file_data_list')

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
