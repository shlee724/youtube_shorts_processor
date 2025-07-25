# -*- coding: utf-8 -*-
"""
VideoSubFinderWXW.exe를 사용하여 자막을 추출하는 모듈
"""

import os
import subprocess
import logging
from typing import List, Dict, Optional
from config import VIDEOSUBFINDER_PATH, VIDEOSUBFINDER_OPTIONS, VIDEOSUBFINDER_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubtitleExtractor:
    def __init__(self):
        """자막 추출기 초기화"""
        self.videosubfinder_path = VIDEOSUBFINDER_PATH
        self.check_videosubfinder()

    def check_videosubfinder(self):
        """VideoSubFinder 실행 파일 존재 확인"""
        if not os.path.exists(self.videosubfinder_path):
            logger.warning(f"VideoSubFinder 실행 파일을 찾을 수 없습니다: {self.videosubfinder_path}")
            logger.warning("config.py에서 VIDEOSUBFINDER_PATH를 올바른 경로로 설정해주세요.")

    # ----------------- 내부 공통 메서드 -----------------
    def _run_videosubfinder(self, video_path: str, threshold: str, extra_opts: Optional[List[str]] = None) -> bool:
        """공통 실행 로직 (자막/제목 추출 공용)

        Args:
            video_path (str): 분석할 영상 경로
            threshold (str): -te 값
            extra_opts (List[str] | None): 추가 커맨드 옵션 리스트

        Returns:
            bool: 결과 폴더에 내용이 있으면 True (성공), 아니면 False
        """
        if extra_opts is None:
            extra_opts = []

        video_dir = os.path.dirname(video_path)
        results_dir = os.path.join(video_dir, 'ResultsDir')
        os.makedirs(results_dir, exist_ok=True)

        cmd = [
            self.videosubfinder_path,
            '-c', '-r', '-ccti',
            '-i', video_path,
            '-o', results_dir,
            '-te', threshold,
            *extra_opts
        ]

        logger.info(f"VideoSubFinder 실행: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=False)
            txt_images_dir = os.path.join(results_dir, 'TXTImages')

            if result.returncode != 0:
                logger.warning(f"비정상 종료 코드 {result.returncode} 감지")

            if os.path.exists(txt_images_dir) and os.listdir(txt_images_dir):
                logger.info("추출 결과 존재: 성공")
                return True
            else:
                logger.error("추출 결과가 없어 실패로 처리")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"VideoSubFinder 실행 실패: {video_path}, 오류: {e.returncode}")
            raise e

    # ----------------- 퍼블릭 메서드 -----------------
    def extract_subtitles(self, video_path: str) -> bool:
        """일반 자막 추출"""
        return self._run_videosubfinder(video_path, VIDEOSUBFINDER_THRESHOLD)

    def extract_title(self, video_path: str) -> bool:
        """제목(초반부) 자막만 추출"""
        extra_opts = [
            '-be', '0.7',
            '-s', '0:00:00:000',
            '-e', '0:00:06:000'
        ]
        return self._run_videosubfinder(video_path, '1.0', extra_opts)