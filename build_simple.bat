@echo off
echo ===============================
echo 📦 PyInstaller 간단 빌드...
echo ===============================

REM 간단한 명령어로 빌드 (python -m src.main과 동일하게 실행)
pyinstaller ^
  --name jamiron ^
  --onedir ^
  --clean ^
  --add-data "src;src" ^
  --hidden-import "src" ^
  --hidden-import "src.app_runner" ^
  --collect-all sentence_transformers ^
  --collect-all transformers ^
  --paths . ^
  --paths src ^
  src/main.py

echo.
echo ✅ 빌드 완료! 실행 파일은 dist\jamiron\ 폴더에 생성됩니다.
echo 📁 실행파일 위치: dist\jamiron\jamiron.exe
pause