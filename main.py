#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 쇼츠 다운로드 및 처리 메인 프로그램

사용법:
    python main.py                              # 대화형 모드
    python main.py [채널URL] [기한날짜]           # 배치 모드

예시:
    python main.py "https://www.youtube.com/@채널명" "2024-01-01"
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Optional

# 환경 변수 로드 (가장 먼저)
from dotenv import load_dotenv
load_dotenv()

# 프로젝트 모듈들
import config
from youtube_api import YouTubeAPI
from downloader import VideoDownloader as Downloader
from file_manager import FileManager
from subtitle_extractor import SubtitleExtractor
from image_processor import ImageProcessor

def setup_logging() -> logging.Logger:
    """로깅 설정"""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('youtube_processor.log', encoding='utf-8')
        ]
    )

    return logging.getLogger(__name__)

def validate_environment():
    """환경 설정 유효성 검사"""
    try:
        config.validate_config()
        return True
    except ValueError as e:
        print(f"❌ 환경 설정 오류: {e}")
        print("\n💡 해결 방법:")
        print("1. 프로젝트 루트에 .env 파일을 생성하세요")
        print("2. .env.example 파일을 복사하여 .env로 이름을 바꾸세요")
        print("3. .env 파일에서 실제 API 키와 경로를 설정하세요")
        print("\n📝 .env 파일 예시:")
        print("YOUTUBE_API_KEY=your_youtube_api_key_here")
        print("VIDEOSUBFINDER_PATH=C:\\path\\to\\VideoSubFinderWXW.exe")
        return False

def get_user_input() -> tuple[str, str]:
    """사용자로부터 채널 URL과 기한 날짜 입력받기"""
    print("\n" + "="*60)
    print("🎬 YouTube 쇼츠 다운로드 및 처리 프로그램")
    print("="*60)
    print(config.get_config_summary())

    # 채널 URL 입력
    while True:
        channel_url = input("\n📺 YouTube 채널 URL을 입력하세요: ").strip()
        if channel_url:
            break
        print("❌ 채널 URL을 입력해주세요.")

    # 기한 날짜 입력
    while True:
        date_input = input("📅 기한 날짜를 입력하세요 (YYYY-MM-DD 형식): ").strip()
        try:
            datetime.strptime(date_input, '%Y-%m-%d')
            break
        except ValueError:
            print("❌ 올바른 날짜 형식으로 입력해주세요 (예: 2024-01-01)")

    return channel_url, date_input

def main():
    """메인 실행 함수"""
    logger = setup_logging()

    # 환경 설정 검사
    if not validate_environment():
        sys.exit(1)

    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(
        description='YouTube 쇼츠 다운로드 및 처리 프로그램',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예시:
  %(prog)s                                          # 대화형 모드
  %(prog)s "https://www.youtube.com/@example" "2024-01-01"  # 배치 모드
        '''
    )
    parser.add_argument('channel_url', nargs='?', help='YouTube 채널 URL')
    parser.add_argument('cutoff_date', nargs='?', help='기한 날짜 (YYYY-MM-DD)')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')

    args = parser.parse_args()

    # 디버그 옵션 처리
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("디버그 모드 활성화")

    try:
        # 채널 URL과 날짜 결정
        if args.channel_url and args.cutoff_date:
            channel_url, cutoff_date = args.channel_url, args.cutoff_date
            logger.info("배치 모드로 실행")
        else:
            channel_url, cutoff_date = get_user_input()
            logger.info("대화형 모드로 실행")

        # 각 컴포넌트 초기화
        logger.info("컴포넌트 초기화 중...")
        youtube_api = YouTubeAPI()
        downloader = Downloader(config.BASE_DOWNLOAD_PATH)
        file_manager = FileManager()
        subtitle_extractor = SubtitleExtractor()
        image_processor = ImageProcessor()

        # 1단계: YouTube API를 통한 쇼츠 영상 정보 수집
        logger.info(f"📺 채널 분석 중: {channel_url}")
        print(f"\n🔍 {channel_url} 채널의 쇼츠 영상을 검색 중...")

        videos_info = youtube_api.get_shorts_videos(channel_url, cutoff_date)

        if not videos_info:
            print("❌ 해당 기간에 쇼츠 영상을 찾을 수 없습니다.")
            return

        print(f"✅ {len(videos_info)}개의 쇼츠 영상을 발견했습니다!")

        # 채널 이름 가져오기
        channel_name = youtube_api.get_channel_name(channel_url)
        logger.info(f"채널명: {channel_name}")

        # 2단계: 영상 다운로드
        print(f"\n⬇️ 영상 다운로드 시작...")
        downloaded_videos = []

        for i, video_info in enumerate(videos_info, 1):
            print(f"  📥 [{i}/{len(videos_info)}] {video_info['title'][:50]}...")

            try:
                video_path = downloader.download_video(video_info, channel_name)
                if video_path:
                    downloaded_videos.append({
                        'info': video_info,
                        'path': video_path
                    })
                    logger.info(f"다운로드 완료: {video_info['title']}")
                else:
                    logger.warning(f"다운로드 실패: {video_info['title']}")

            except Exception as e:
                logger.error(f"다운로드 오류 - {video_info['title']}: {e}")

        print(f"✅ {len(downloaded_videos)}개 영상 다운로드 완료!")

        # 3단계: 파일 정리 (각 영상을 개별 폴더로 이동)
        print(f"\n📁 파일 정리 중...")
        organized_videos = []

        for video_data in downloaded_videos:
            try:
                organized_path = file_manager.organize_video_file(
                    video_data['path'], 
                    video_data['info']['title']
                )
                organized_videos.append({
                    'info': video_data['info'],
                    'path': organized_path
                })
                logger.info(f"파일 정리 완료: {video_data['info']['title']}")

            except Exception as e:
                logger.error(f"파일 정리 오류 - {video_data['info']['title']}: {e}")

        print(f"✅ {len(organized_videos)}개 영상 파일 정리 완료!")

        # 4단계: 자막 추출
        print(f"\n🔤 자막 추출 중...")
        subtitle_completed = 0

        for video_data in organized_videos:
            try:
                subtitle_extractor.extract_subtitles(video_data['path'])
                subtitle_completed += 1
                logger.info(f"자막 추출 완료: {video_data['info']['title']}")
                print(f"  ✅ [{subtitle_completed}/{len(organized_videos)}] 자막 추출 완료")

            except Exception as e:
                logger.error(f"자막 추출 오류 - {video_data['info']['title']}: {e}")
                print(f"  ❌ 자막 추출 실패: {video_data['info']['title'][:30]}...")

        # 5단계: 이미지 합성
        print(f"\n🖼️ 이미지 합성 중...")
        image_completed = 0

        for video_data in organized_videos:
            try:
                result_path = image_processor.combine_images(video_data['path'])
                if result_path:
                    image_completed += 1
                    logger.info(f"이미지 합성 완료: {video_data['info']['title']}")
                    print(f"  ✅ [{image_completed}/{len(organized_videos)}] 이미지 합성 완료")
                else:
                    print(f"  ⚠️ 합성할 이미지가 없음: {video_data['info']['title'][:30]}...")

            except Exception as e:
                logger.error(f"이미지 합성 오류 - {video_data['info']['title']}: {e}")
                print(f"  ❌ 이미지 합성 실패: {video_data['info']['title'][:30]}...")

        # 최종 결과 출력
        print("\n" + "="*60)
        print("🎉 모든 작업이 완료되었습니다!")
        print("="*60)
        print(f"📊 처리 결과:")
        print(f"  • 발견된 쇼츠: {len(videos_info)}개")
        print(f"  • 다운로드 완료: {len(downloaded_videos)}개")
        print(f"  • 파일 정리 완료: {len(organized_videos)}개")
        print(f"  • 자막 추출 완료: {subtitle_completed}개")
        print(f"  • 이미지 합성 완료: {image_completed}개")
        print(f"\n📁 결과 저장 위치: {config.BASE_DOWNLOAD_PATH}")

        logger.info("프로그램 실행 완료")

    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 프로그램을 중단했습니다.")
        logger.info("사용자 중단")

    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)

        if config.DEBUG:
            import traceback
            print("\n🐛 디버그 정보:")
            traceback.print_exc()

if __name__ == "__main__":
    main()
