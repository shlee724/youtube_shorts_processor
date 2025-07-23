@echo off
chcp 65001 > nul
title YouTube 쇼츠 프로세서 - 보안 설치

echo.
echo ================================================================
echo 🎬 YouTube 쇼츠 다운로드 및 처리 프로그램 - 보안 설치
echo ================================================================
echo.

echo 📦 Python 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 패키지 설치에 실패했습니다.
    echo 💡 Python이 설치되어 있고 pip가 사용 가능한지 확인해주세요.
    pause
    exit /b 1
)

echo.
echo ✅ 패키지 설치 완료!

echo.
echo 🔒 환경 변수 파일 설정 중...

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" > nul
        echo ✅ .env 파일이 생성되었습니다.
        echo.
        echo ⚠️  중요: .env 파일을 열어서 실제 API 키를 설정해주세요!
        echo.
    ) else (
        echo ❌ .env.example 파일을 찾을 수 없습니다.
        echo 💡 프로젝트 파일이 모두 있는지 확인해주세요.
        pause
        exit /b 1
    )
) else (
    echo ℹ️  .env 파일이 이미 존재합니다.
)

echo.
echo 🔧 설정 확인 중...
python config.py
if errorlevel 1 (
    echo.
    echo ❌ 설정에 오류가 있습니다.
    echo.
    echo 💡 다음 단계를 수행해주세요:
    echo    1. .env 파일을 메모장으로 열기
    echo    2. YOUTUBE_API_KEY=your_youtube_api_key_here 부분을 실제 API 키로 변경
    echo    3. VIDEOSUBFINDER_PATH를 실제 VideoSubFinder 경로로 변경
    echo    4. BASE_DOWNLOAD_PATH를 원하는 다운로드 경로로 변경
    echo.
    echo 📖 자세한 설정 방법은 API_KEY_SECURITY_GUIDE.md 파일을 참고하세요.
    echo.
    set /p choice="🔧 지금 .env 파일을 편집하시겠습니까? (y/n): "
    if /i "%choice%"=="y" (
        if exist ".env" (
            start notepad.exe ".env"
            echo.
            echo 📝 .env 파일이 메모장에서 열렸습니다.
            echo    수정 후 저장하고 이 창으로 돌아와서 아무 키나 누르세요.
            pause
            echo.
            echo 🔧 설정 재확인 중...
            python config.py
        )
    )
) else (
    echo ✅ 모든 설정이 완료되었습니다!
    echo.
    echo 🚀 이제 다음 명령어로 프로그램을 실행할 수 있습니다:
    echo    python main.py
    echo.
    echo 📖 사용법:
    echo    • 대화형 모드: python main.py
    echo    • 배치 모드: python main.py "채널URL" "기한날짜"
    echo.
    echo 📋 도움말:
    echo    • API_KEY_SECURITY_GUIDE.md - API 키 보안 설정 가이드
    echo    • README.md - 상세한 사용 설명서
    echo.
)

echo.
echo 🔒 보안 알림:
echo    • .env 파일은 Git에 업로드되지 않습니다 (.gitignore에 포함됨)
echo    • API 키를 다른 사람과 공유하지 마세요
echo    • 정기적으로 API 키를 갱신하는 것을 권장합니다
echo.

echo ================================================================
echo 설치가 완료되었습니다!
echo ================================================================
echo.

set /p choice="🚀 지금 프로그램을 실행하시겠습니까? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 🎬 프로그램을 시작합니다...
    python main.py
) else (
    echo.
    echo 💡 나중에 'python main.py' 명령어로 프로그램을 실행하세요.
)

echo.
pause
