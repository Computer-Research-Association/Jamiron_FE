#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller 엔트리 포인트
python -m src.main과 동일하게 작동
"""

import sys
import os

# 현재 실행 파일의 디렉토리를 sys.path에 추가
if getattr(sys, "frozen", False):
    # PyInstaller로 빌드된 실행파일인 경우
    base_path = sys._MEIPASS
else:
    # 개발 환경에서 실행하는 경우
    base_path = os.path.dirname(os.path.abspath(__file__))

# src 모듈을 찾을 수 있도록 경로 추가
sys.path.insert(0, base_path)

# src.app_runner 모듈을 직접 import하고 실행
try:
    from src.app_runner import run_app

    if __name__ == "__main__":
        run_app()
except ImportError as e:
    print(f"Error importing src.app_runner: {e}")
    # 대안으로 src.main 직접 실행 시도
    try:
        import src.main
    except ImportError as e2:
        print(f"Error importing src.main: {e2}")
        sys.exit(1)
