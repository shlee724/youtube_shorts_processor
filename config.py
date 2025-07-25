import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# ==================== API 설정 ====================
# YouTube Data API v3 키 (Google Cloud Console에서 발급)
# .env 파일에 YOUTUBE_API_KEY=your_api_key_here 형식으로 저장
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise ValueError("❌ YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 설정해주세요.")

# ==================== 경로 설정 ====================
# VideoSubFinder 실행 파일 경로
VIDEOSUBFINDER_PATH = os.getenv('VIDEOSUBFINDER_PATH', 
    r"C:\Users\이승호_\Desktop\video_sub_finder\VideoSubFinderWXW.exe")

# 기본 다운로드 경로
BASE_DOWNLOAD_PATH = os.getenv('BASE_DOWNLOAD_PATH',
    r"D:\youtube\인체백과\쇼츠 레퍼런스 분석\제목 강조형 템플릿")

# ==================== 다운로드 설정 ====================
# yt-dlp 다운로드 형식 (사용자 요청사항 그대로)
YT_DLP_FORMAT = "bestvideo*[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo*+bestaudio/best"

# ==================== VideoSubFinder 설정 ====================
# VideoSubFinder 명령어 옵션
VIDEOSUBFINDER_OPTIONS = ["-c", "-r", "-ccti"]
VIDEOSUBFINDER_THRESHOLD = "0.41"  # -te 옵션 값

# ==================== 기타 설정 ====================
# 디버그 모드
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# 로그 레벨
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# API 요청 간격 (초)
API_REQUEST_DELAY = 0.1

# 최대 재시도 횟수
MAX_RETRY_ATTEMPTS = 3

# 파일명에서 제거할 특수문자 (Windows 금지 문자 + 추가 문제 문자)
INVALID_FILENAME_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

# Windows 경로 길이 제한
MAX_PATH_LENGTH = 260

# Windows에서 금지된 문자 + 추가 문제가 될 수 있는 문자들
FORBIDDEN_CHARS = '<>:"/\\|?*\'\n\r\t'

# 누락된 변수 추가
MAX_RESULTS_PER_REQUEST = 50  # YouTube Data API max: 보통 50이 최대
API_REQUEST_DELAY = 1.0       # 초 단위, 1.0초로 설정(필요에 따라 조정)

def validate_config():
    """설정값 유효성 검사"""
    errors = []

    if not YOUTUBE_API_KEY:
        errors.append("❌ YouTube API 키가 설정되지 않았습니다.")

    if not os.path.exists(os.path.dirname(VIDEOSUBFINDER_PATH)):
        errors.append(f"❌ VideoSubFinder 디렉토리가 존재하지 않습니다: {os.path.dirname(VIDEOSUBFINDER_PATH)}")

    if not os.path.exists(os.path.dirname(BASE_DOWNLOAD_PATH)):
        errors.append(f"❌ 다운로드 기본 경로의 상위 디렉토리가 존재하지 않습니다: {os.path.dirname(BASE_DOWNLOAD_PATH)}")

    if errors:
        raise ValueError("\n".join(errors))

    return True

def get_config_summary():
    """현재 설정 요약 반환"""
    return f"""
🔧 YouTube 쇼츠 프로세서 설정
===================================
📺 YouTube API: {'✅ 설정됨' if YOUTUBE_API_KEY else '❌ 미설정'}
🎬 VideoSubFinder: {VIDEOSUBFINDER_PATH}
📁 다운로드 경로: {BASE_DOWNLOAD_PATH}
🔧 디버그 모드: {DEBUG}
📝 로그 레벨: {LOG_LEVEL}
"""

if __name__ == "__main__":
    try:
        validate_config()
        print("✅ 모든 설정이 유효합니다!")
        print(get_config_summary())
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("\n💡 해결 방법:")
        print("1. .env 파일을 생성하고 필요한 환경 변수를 설정하세요")
        print("2. .env.example 파일을 참고하여 올바른 형식으로 작성하세요")
