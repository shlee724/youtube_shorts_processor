# -*- coding: utf-8 -*-
"""
yt-dlp를 사용하여 YouTube 영상을 다운로드하는 모듈
"""

import os
import logging
from typing import List, Dict
import yt_dlp

from config import YT_DLP_FORMAT, FORBIDDEN_CHARS, MAX_PATH_LENGTH

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

    def download_single_video(self, video: Dict, channel_path: str) -> Dict:
        """단일 영상 다운로드"""
        video_title = self.sanitize_filename(video['title'])

        ydl_opts = {
            'format': YT_DLP_FORMAT,
            'outtmpl': os.path.join(channel_path, f'{video_title}.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'noplaylist': True,
            'overwrites': False,  # 덮어쓰기 강제 지정
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"다운로드 시작: {video['title']}")
                info_dict = ydl.extract_info(video['url'], download=True)
                downloaded_file = ydl.prepare_filename(info_dict)

                if os.path.exists(downloaded_file):
                    video_info = video.copy()
                    video_info['downloaded_path'] = downloaded_file
                    video_info['channel_path'] = channel_path
                    logger.info(f"다운로드 완료: {downloaded_file}")
                    return downloaded_file
                else:
                    logger.error(f"다운로드된 파일을 찾을 수 없음: {downloaded_file}")
                    return None

        except Exception as e:
            logger.error(f"다운로드 오류 - {video['title']}: {e}")
            return None

    def sanitize_filename(self, filename: str) -> str:
        """Windows 파일명에 사용할 수 없는 문자 제거"""

        # 금지된 문자 제거
        for char in FORBIDDEN_CHARS:
            filename = filename.replace(char, '_')

        # 길이 제한 (여기서 100자는 안전한 편)
        if len(filename) > 100:
            filename = filename[:97] + "..."

        # 앞뒤 공백 제거
        filename = filename.strip()

        # 빈 문자열 방지
        if not filename:
            filename = "untitled"

        return filename
