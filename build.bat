@echo off
echo ===============================
echo 📦 PyInstaller 빌드 시작...
echo ===============================

REM spec 파일을 사용한 빌드
pyinstaller --clean jamiron_build.spec

echo.
echo ✅ 빌드 완료! 실행 파일은 dist\jamiron\ 폴더에 생성됩니다.
echo 📁 실행파일 위치: dist\jamiron\jamiron.exe
pause
