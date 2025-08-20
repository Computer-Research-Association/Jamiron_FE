import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.environ.get('REQUEST_URL')

class LoginRequest:
    def __init__(self):
        self.url = URL + '/api/login'

    def login(self, user_id, password, year, hakgi):
        data = {
            'user_id': user_id,
            'password': password,
            'year': year,
            'semester': hakgi,
        }

        # POST 요청 보내기
        response = requests.post(self.url, json=data)

        # 응답 확인
        if response.status_code == 201:
            data = response.json()
            if data == 200:
                return True
            elif data == 401:
                return False
        else:
            return False