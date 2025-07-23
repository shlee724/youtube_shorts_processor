# 🔒 API 키 보안 설정 가이드

## 📋 개요

이 프로젝트는 **환경 변수(.env 파일)**를 사용하여 API 키와 민감한 정보를 안전하게 관리합니다.
Git에 API 키가 노출되지 않도록 보호하는 완전한 보안 시스템입니다.

## 🚀 빠른 시작

### 1단계: 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 2단계: 환경 변수 파일 생성
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# 또는 Windows에서
copy .env.example .env
```

### 3단계: API 키 설정
`.env` 파일을 열고 실제 값으로 수정:

```env
# YouTube API 설정
YOUTUBE_API_KEY=AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY  # 실제 API 키로 변경

# VideoSubFinder 경로 설정  
VIDEOSUBFINDER_PATH=C:\Users\YOUR_USERNAME\Desktop\video_sub_finder\VideoSubFinderWXW.exe

# 다운로드 기본 경로
BASE_DOWNLOAD_PATH=D:\youtube\인체백과\쇼츠 레퍼런스 분석\제목 강조형 템플릿
```

### 4단계: 설정 확인
```bash
python config.py
```

### 5단계: 프로그램 실행
```bash
python main.py
```

---

## 🔑 YouTube API 키 발급 방법

### 1. Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 2. YouTube Data API v3 활성화
1. **API 및 서비스** → **라이브러리** 선택
2. "YouTube Data API v3" 검색
3. **사용 설정** 클릭

### 3. API 키 생성
1. **API 및 서비스** → **사용자 인증 정보** 선택
2. **+ 사용자 인증 정보 만들기** → **API 키** 선택
3. 생성된 API 키를 복사

### 4. API 키 제한 설정 (권장)
1. 생성된 API 키를 클릭
2. **애플리케이션 제한사항**: "HTTP 리퍼러"
3. **API 제한사항**: "YouTube Data API v3"만 선택
4. **저장** 클릭

---

## 🛡️ 보안 핵심 사항

### ✅ 안전한 방법
- `.env` 파일에 API 키 저장 ✅
- `.gitignore`에 `.env` 추가됨 ✅
- 환경 변수로 API 키 읽기 ✅
- `.env.example`로 템플릿 제공 ✅

### ❌ 위험한 방법
- 코드에 직접 API 키 하드코딩 ❌
- API 키를 Git에 커밋 ❌
- API 키를 채팅이나 이메일로 공유 ❌

---

## 📁 파일 구조

```
youtube_shorts_processor/
├── .env                    # 🔒 실제 API 키 (Git에서 제외됨)
├── .env.example           # 📝 환경 변수 템플릿
├── .gitignore             # 🚫 Git 제외 파일 목록
├── config.py              # ⚙️ 환경 변수 설정
├── main.py                # 🚀 메인 실행 파일
├── requirements.txt       # 📦 필요한 패키지 목록
└── README.md             # 📖 사용 설명서
```

---

## 🔧 문제 해결

### "API 키가 설정되지 않았습니다" 오류
```bash
❌ ValueError: YouTube API 키가 설정되지 않았습니다. .env 파일에 YOUTUBE_API_KEY를 설정해주세요.
```

**해결 방법:**
1. `.env` 파일이 존재하는지 확인
2. `.env` 파일에 `YOUTUBE_API_KEY=실제_API_키` 라인이 있는지 확인
3. API 키에 공백이나 특수문자가 잘못 들어가지 않았는지 확인

### "VideoSubFinder 디렉토리가 존재하지 않습니다" 오류
```bash
❌ VideoSubFinder 디렉토리가 존재하지 않습니다
```

**해결 방법:**
1. VideoSubFinderWXW.exe 파일의 실제 경로 확인
2. `.env` 파일의 `VIDEOSUBFINDER_PATH` 경로 수정
3. 경로에서 백슬래시를 이중으로 사용: `C:\\path\\to\\file.exe`

### Git에 .env 파일이 이미 추가된 경우
```bash
# Git 추적에서 .env 파일 제거
git rm --cached .env
git add .
git commit -m "Remove .env from tracking"
git push
```

---

## 🌟 보안 베스트 프랙티스

### 1. 정기적인 API 키 갱신
- 3-6개월마다 API 키를 새로 발급받아 교체

### 2. API 키 제한 설정
- Google Cloud Console에서 API 키 사용을 특정 API로만 제한

### 3. 접근 권한 최소화
- 필요한 최소한의 권한만 부여

### 4. 모니터링
- Google Cloud Console에서 API 사용량 정기 확인

### 5. 팀 작업 시
- API 키를 직접 공유하지 말고, 각자 발급받아 사용
- `.env.example` 파일로 필요한 환경 변수 안내

---

## 📞 지원

문제가 발생하면:
1. `python config.py` 명령어로 설정 상태 확인
2. 로그 파일(`youtube_processor.log`) 확인
3. 디버그 모드로 실행: `python main.py --debug`

---

## 🎉 완료!

이제 API 키가 안전하게 보호된 상태로 프로그램을 사용할 수 있습니다!

**다음 명령어로 프로그램을 시작하세요:**
```bash
python main.py
```
