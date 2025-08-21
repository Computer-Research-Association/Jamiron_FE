@echo off
echo ===============================
echo 📦 PyInstaller 직접 빌드...
echo ===============================

REM 직접 명령어로 빌드 (더 안전한 방법)
pyinstaller ^
  --name jamiron ^
  --onedir ^
  --clean ^
  --add-data "src;src" ^
  --hidden-import "src" ^
  --hidden-import "src.main" ^
  --hidden-import "src.app_runner" ^
  --collect-all sentence_transformers ^
  --collect-all transformers ^
  --collect-all torch ^
  --paths . ^
  --paths src ^
  --console ^
  main_entry.py

echo.
echo ✅ 빌드 완료! 실행 파일은 dist\jamiron\ 폴더에 생성됩니다.
echo 📁 실행파일 위치: dist\jamiron\jamiron.exe
pause