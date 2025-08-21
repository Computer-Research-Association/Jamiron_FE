import requests
import json
from dotenv import load_dotenv
import os
import websockets
import asyncio

load_dotenv()

URL = os.environ.get('REQUEST_URL')

class LoginRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/login'
        self.progress_callback = progress_callback
    
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    async def login(self, user_id, password, year, hakgi):
        try:
            async with websockets.connect(self.uri) as websocket:
                data = {
                    'user_id': user_id,
                    'password': password,
                    'year': year,
                    'semester': hakgi,
                }
                
                await websocket.send(json.dumps(data))
                
                while True:
                    # POST 요청 보내기
                    response = await websocket.recv()
                    res_data = json.loads(response)
                    
                    msg = res_data.get("msg")
                    percent = res_data.get("percent")

                    # 응답 확인
                    if response.status_code == 201:
                        data = response.json()
                        if data == 200:
                            self.update_progress(msg, percent)
                            return True
                        elif data == 401:
                            return False
                    else:
                        return False
        except ConnectionRefusedError:
            print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return False
        except websockets.exceptions.ConnectionClosed:
            print("서버와의 연결이 끊어졌습니다.")
            return False
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            return False
        
class ClassifierRequest:
    def __init__(self, progress_callback=None):
        self.uri = URL + '/api/classifier'
        self.progress_callback = progress_callback
        
    def update_progress(self, message: str, percent: int):
        if self.progress_callback:
            self.progress_callback(message, percent)

    async def classify(self, file_data_list):
        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(json.dumps(file_data_list))
                while True:
                    # POST 요청 보내기
                    response = await websocket.recv()
                    res_data = json.loads(response)
                    
                    msg = res_data.get("msg")
                    percent = res_data.get("percent")

                    # 응답 확인
                    if response.status_code == 201:
                        data = response.json()
                        if data == 200:
                            self.update_progress(msg, percent)
                            return True
                        elif data == 401:
                            return False
                    else:
                        return False
        except ConnectionRefusedError:
            print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
            return False
        except websockets.exceptions.ConnectionClosed:
            print("서버와의 연결이 끊어졌습니다.")
            return False
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")
            return False