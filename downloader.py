# -*- coding: utf-8 -*-
"""
yt-dlp를 사용하여 YouTube 영상을 다운로드하는 모듈
"""

import os
import logging
from typing import List, Dict
import yt_dlp
from config import YT_DLP_FORMAT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self, download_path: str):
        """다운로더 초기화"""
        self.download_path = download_path
        self.setup_download_path()

    def setup_download_path(self):
        """다운로드 경로 생성"""
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path, exist_ok=True)
            logger.info(f"다운로드 경로 생성: {self.download_path}")

    def download_videos(self, videos: List[Dict], channel_name: str) -> List[Dict]:
        """영상 목록 다운로드"""
        successful_downloads = []

        # 채널별 다운로드 경로
        channel_path = os.path.join(self.download_path, self.sanitize_filename(channel_name))
        if not os.path.exists(channel_path):
            os.makedirs(channel_path, exist_ok=True)

        for video in videos:
            try:
                result = self.download_single_video(video, channel_path)
                if result:
                    successful_downloads.append(result)
            except Exception as e:
                logger.error(f"영상 다운로드 실패 - {video['title']}: {e}")
                continue

        logger.info(f"총 {len(successful_downloads)}개 영상 다운로드 완료")
        return successful_downloads

    def download_single_video(self, video: Dict, channel_path: str) -> Dict:
        """단일 영상 다운로드"""
        video_title = self.sanitize_filename(video['title'])

        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': YT_DLP_FORMAT,
            'outtmpl': os.path.join(channel_path, f'{video_title}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"다운로드 시작: {video['title']}")
                ydl.download([video['url']])

                # 실제 다운로드된 파일 경로 찾기
                downloaded_file = self.find_downloaded_file(channel_path, video_title)

                if downloaded_file:
                    video_info = video.copy()
                    video_info['downloaded_path'] = downloaded_file
                    video_info['channel_path'] = channel_path
                    logger.info(f"다운로드 완료: {downloaded_file}")
                    return video_info
                else:
                    logger.error(f"다운로드된 파일을 찾을 수 없음: {video_title}")
                    return None

        except Exception as e:
            logger.error(f"다운로드 오류 - {video['title']}: {e}")
            return None

    def find_downloaded_file(self, channel_path: str, video_title: str) -> str:
        """다운로드된 파일 경로 찾기"""
        possible_extensions = ['.mp4', '.webm', '.mkv']

        for ext in possible_extensions:
            file_path = os.path.join(channel_path, f"{video_title}{ext}")
            if os.path.exists(file_path):
                return file_path

        # 파일명이 약간 다를 수 있으므로 디렉토리에서 검색
        if os.path.exists(channel_path):
            for file in os.listdir(channel_path):
                if video_title in file and any(file.endswith(ext) for ext in possible_extensions):
                    return os.path.join(channel_path, file)

        return None

    def sanitize_filename(self, filename: str) -> str:
        """Windows 파일명에 사용할 수 없는 문자 제거"""
        from config import FORBIDDEN_CHARS, MAX_PATH_LENGTH

        # 금지된 문자 제거
        for char in FORBIDDEN_CHARS:
            filename = filename.replace(char, '_')

        # 길이 제한
        if len(filename) > 100:  # 파일명만 100자로 제한
            filename = filename[:97] + "..."

        # 앞뒤 공백 제거
        filename = filename.strip()

        # 빈 문자열 방지
        if not filename:
            filename = "untitled"

        return filename
