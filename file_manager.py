# -*- coding: utf-8 -*-
"""
파일 및 폴더 관리를 담당하는 모듈
"""

import os
import shutil
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        """파일 매니저 초기화"""
        pass

    def sanitize_filename(self, filename: str) -> str:
        """Windows 파일명에 사용할 수 없는 문자 제거"""
        from config import FORBIDDEN_CHARS

        # 금지된 문자 제거
        for char in FORBIDDEN_CHARS:
            filename = filename.replace(char, '_')

        # 길이 제한
        if len(filename) > 100:
            filename = filename[:97] + "..."

        # 앞뒤 공백 제거
        filename = filename.strip()

        # 빈 문자열 방지
        if not filename:
            filename = "untitled"

        return filename

    def organize_video_file(self, file_path: str, video_title: str) -> str:
        """
        다운로드된 영상을 개별 폴더로 이동 및 정리하는 메서드
        - file_path : 기존 영상 파일 경로
        - video_title : 영상 제목 (새 폴더명)
        반환값 : 정리된 영상 파일 경로
        """
        import os
        import shutil

        # 디렉토리 및 새 경로 생성
        directory = os.path.dirname(file_path)
        new_folder = os.path.join(directory, video_title)
        os.makedirs(new_folder, exist_ok=True)

        # 새 파일 경로 설정
        filename = os.path.basename(file_path)
        new_path = os.path.join(new_folder, filename)

        # 파일 이동
        shutil.move(file_path, new_path)

        return new_path
