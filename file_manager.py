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
        import re

        # 금지된 문자 제거
        for char in FORBIDDEN_CHARS:
            filename = filename.replace(char, '_')

        # 연속된 언더스코어를 하나로 줄임
        filename = re.sub(r'_+', '_', filename)
        
        # 마침표로 끝나는 경우 문제가 될 수 있으므로 제거
        filename = filename.rstrip('.')
        
        # 앞뒤 공백과 언더스코어 제거
        filename = filename.strip(' _')

        # 길이 제한
        if len(filename) > 100:
            filename = filename[:97] + "..."

        # 빈 문자열 방지
        if not filename:
            filename = "untitled"

        return filename

    def organize_video_file(self, file_path: str, video_title: str = None) -> str:
        """
        다운로드된 영상을 개별 폴더로 이동 및 정리하는 메서드
        - file_path : 기존 영상 파일 경로
        - video_title : 영상 제목 (새 폴더명, 선택사항)
        반환값 : 정리된 영상 파일 경로
        """
        import os
        import shutil
        from config import MAX_PATH_LENGTH

        # 디렉토리 및 파일 정보 가져오기
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        # 디버깅: 실제 파일 상황 로깅
        logger.info(f"==== 파일 정리 디버깅 ====")
        logger.info(f"입력된 파일 경로: {file_path}")
        logger.info(f"파일 존재 여부: {os.path.exists(file_path)}")
        logger.info(f"디렉토리: {directory}")
        logger.info(f"파일명: {filename}")
        
        # 디렉토리의 모든 파일 나열 (디버깅)
        if os.path.exists(directory):
            all_files = os.listdir(directory)
            logger.info(f"디렉토리 내 모든 파일: {all_files}")
            # 비슷한 파일명 찾기
            base_name = os.path.splitext(filename)[0]
            similar_files = [f for f in all_files if base_name in f]
            logger.info(f"유사한 파일명: {similar_files}")
        
        # 파일이 존재하는지 확인
        if not os.path.exists(file_path):
            logger.error(f"원본 파일을 찾을 수 없습니다: {file_path}")
            
            # 비슷한 파일이 있는지 찾아보기
            if os.path.exists(directory):
                all_files = os.listdir(directory)
                base_name = os.path.splitext(filename)[0]
                # 확장자 제외하고 비슷한 파일 찾기
                potential_files = [f for f in all_files if f.startswith(base_name) and f.endswith('.mp4')]
                if potential_files:
                    logger.info(f"발견된 유사 파일들: {potential_files}")
                    # 가장 유사한 파일 사용
                    actual_file = potential_files[0]
                    actual_path = os.path.join(directory, actual_file)
                    logger.info(f"대신 사용할 파일: {actual_path}")
                    file_path = actual_path
                    filename = actual_file
                else:
                    raise FileNotFoundError(f"원본 파일을 찾을 수 없습니다: {file_path}")
            else:
                raise FileNotFoundError(f"디렉토리가 존재하지 않습니다: {directory}")

        # 실제 파일명에서 확장자를 제거하여 폴더명으로 사용 (이미 sanitized된 상태)
        # 더 정확한 디버깅을 위한 파일명 분석
        logger.info(f"파일명 상세 분석:")
        logger.info(f"  파일명: '{filename}'")
        logger.info(f"  파일명 길이: {len(filename)}")
        logger.info(f"  파일명 바이트: {filename.encode('utf-8')}")
        logger.info(f"  마지막 10글자: '{filename[-10:]}'")
        
        # 더 강력한 확장자 제거 로직
        video_extensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv', '.wmv']
        folder_name = filename
        
        # 각 확장자를 확인하여 제거
        for ext in video_extensions:
            if filename.lower().endswith(ext.lower()):
                folder_name = filename[:-len(ext)]
                logger.info(f"확장자 '{ext}' (길이: {len(ext)}) 제거:")
                logger.info(f"  원본: '{filename}' (길이: {len(filename)})")
                logger.info(f"  결과: '{folder_name}' (길이: {len(folder_name)})")
                logger.info(f"  마지막 10글자 비교: '{filename[-10:]}' vs '{folder_name[-10:]}'")
                break
        else:
            # 어떤 확장자도 매치되지 않으면 splitext 사용 (백업)
            folder_name = os.path.splitext(filename)[0]
            logger.warning(f"알 수 없는 확장자, splitext 사용: '{filename}' → '{folder_name}'")

        # Windows는 폴더명이 마침표(.)나 공백으로 끝나는 것을 허용하지 않음
        folder_name = folder_name.rstrip('. ').rstrip('\u3002')  # 한글 마침표 포함

        # 빈 문자열 방지
        if not folder_name:
            folder_name = 'untitled'

        # video_title이 제공된 경우 원본 제목도 함께 고려 (로깅용)
        if video_title:
            logger.info(f"원본 제목: {video_title}")
            logger.info(f"실제 파일명 기반 폴더명: {folder_name}")

        sanitized_title = folder_name  # 이미 downloader에서 sanitized됨
        
        # 경로 길이 체크 및 조정
        potential_new_folder = os.path.join(directory, sanitized_title)
        filename = os.path.basename(file_path)
        potential_new_path = os.path.join(potential_new_folder, filename)
        
        # Windows 경로 길이 제한 체크 (260자)
        if len(potential_new_path) > MAX_PATH_LENGTH - 10:  # 여유분 10자
            # 폴더명을 더 짧게 줄임
            max_folder_length = MAX_PATH_LENGTH - len(directory) - len(filename) - 20  # 여유분
            if max_folder_length < 20:
                max_folder_length = 20  # 최소 20자는 보장
            sanitized_title = sanitized_title[:max_folder_length] + "..."
            logger.warning(f"경로가 너무 길어 폴더명을 단축했습니다: {sanitized_title}")

        new_folder = os.path.join(directory, sanitized_title)
        
        try:
            # 새 폴더 생성
            os.makedirs(new_folder, exist_ok=True)
            logger.info(f"폴더 생성: {new_folder}")

            # 새 파일 경로 설정
            new_path = os.path.join(new_folder, filename)

            # 파일 이동
            shutil.move(file_path, new_path)
            logger.info(f"파일 이동 완료: {file_path} -> {new_path}")

            return new_path

        except Exception as e:
            logger.error(f"파일 정리 중 오류 발생: {e}")
            # 폴더가 생성되었지만 파일 이동에 실패한 경우, 빈 폴더 정리
            if os.path.exists(new_folder) and not os.listdir(new_folder):
                try:
                    os.rmdir(new_folder)
                    logger.info(f"빈 폴더 삭제: {new_folder}")
                except:
                    pass
            raise
