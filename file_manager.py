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

    def organize_videos(self, downloaded_videos: List[Dict]) -> List[Dict]:
        """각 영상을 제목별 개별 폴더로 정리"""
        organized_videos = []

        for video in downloaded_videos:
            try:
                organized_video = self.move_video_to_folder(video)
                if organized_video:
                    organized_videos.append(organized_video)
            except Exception as e:
                logger.error(f"영상 정리 실패 - {video['title']}: {e}")
                continue

        logger.info(f"총 {len(organized_videos)}개 영상 정리 완료")
        return organized_videos

    def move_video_to_folder(self, video: Dict) -> Dict:
        """영상을 제목 이름의 폴더로 이동"""
        try:
            # 원본 파일 경로
            original_path = video['downloaded_path']

            if not os.path.exists(original_path):
                logger.error(f"원본 파일이 존재하지 않음: {original_path}")
                return None

            # 새 폴더 경로 생성
            video_title = self.sanitize_filename(video['title'])
            video_folder = os.path.join(video['channel_path'], video_title)

            # 폴더 생성
            if not os.path.exists(video_folder):
                os.makedirs(video_folder, exist_ok=True)
                logger.info(f"영상 폴더 생성: {video_folder}")

            # 새 파일 경로
            file_extension = os.path.splitext(original_path)[1]
            new_file_path = os.path.join(video_folder, f"{video_title}{file_extension}")

            # 파일 이동
            shutil.move(original_path, new_file_path)
            logger.info(f"파일 이동: {original_path} -> {new_file_path}")

            # 업데이트된 정보 반환
            updated_video = video.copy()
            updated_video['video_folder'] = video_folder
            updated_video['video_file_path'] = new_file_path
            updated_video['video_filename'] = f"{video_title}{file_extension}"

            return updated_video

        except Exception as e:
            logger.error(f"파일 이동 중 오류 - {video['title']}: {e}")
            return None

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

    def create_results_directory(self, video_folder: str) -> str:
        """ResultsDir 폴더 생성"""
        results_dir = os.path.join(video_folder, "ResultsDir")
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)
            logger.info(f"ResultsDir 생성: {results_dir}")
        return results_dir

    def get_txt_images_directory(self, video_folder: str) -> str:
        """TXTImages 디렉토리 경로 반환"""
        return os.path.join(video_folder, "ResultsDir", "TXTImages")

    def cleanup_temp_files(self, directory: str):
        """임시 파일 정리"""
        try:
            temp_extensions = ['.tmp', '.temp', '.part']

            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if any(file.endswith(ext) for ext in temp_extensions):
                        temp_file = os.path.join(directory, file)
                        os.remove(temp_file)
                        logger.info(f"임시 파일 삭제: {temp_file}")
        except Exception as e:
            logger.error(f"임시 파일 정리 중 오류: {e}")
    
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
