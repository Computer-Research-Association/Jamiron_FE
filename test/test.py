import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

URL = os.environ.get('REQUEST_URL')
ID = os.environ.get('ID')
PW = os.environ.get('PW')

url = URL + '/api/login'

data = {
    'user_id': ID,
    'password': PW,
}

headers = {
    'Content-Type': 'application/json'
} 

# POST 요청 보내기
response = requests.post(url, json=data)

# 응답 확인
if response.status_code == 200:
    print("요청 성공! (데이터 생성됨)")
    data = response.json()
    print(data)
else:
    print(f"요청 실패. 상태 코드: {response.status_code}")