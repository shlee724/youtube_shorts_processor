# -*- coding: utf-8 -*-
"""
VideoSubFinderWXW.exe를 사용하여 자막을 추출하는 모듈
"""

import os
import subprocess
import logging
from typing import List, Dict
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

    def extract_subtitles(self, video_path: str):
        """
        VideoSubFinderWXW.exe를 호출해 해당 영상에서 자막 추출 수행
        - video_path : 분석할 영상 파일 경로
        """
        import subprocess
        import os
        import logging

        logger = logging.getLogger(__name__)
        
        exe_path = 'C:\\Users\\이승호_\\Desktop\\video_sub_finder\\VideoSubFinderWXW.exe'  # config에서 관리하는게 더 좋음
        video_dir = os.path.dirname(video_path)
        video_name = os.path.basename(video_path)
        video_title, _ = os.path.splitext(video_name)

        results_dir = os.path.join(video_dir, 'ResultsDir')

        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)

        cmd = [
            exe_path,
            '-c',
            '-r',
            '-ccti',
            '-i', video_path,
            '-o', results_dir,
            '-te', '0.41'
        ]

        logger.info(f"VideoSubFinder 실행: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=False)
            results_dir = os.path.join(os.path.dirname(video_path), "ResultsDir\TXTImages")
            
            if result.returncode != 0:
                logger.warning(f"비정상 종료 코드 {result.returncode} 감지")
            
            if os.path.exists(results_dir) and os.listdir(results_dir):
                logger.info("자막 추출 결과 폴더 및 파일 있음, 성공 처리")
            else:
                logger.error("자막 추출 결과가 없어 실패로 처리")
        except subprocess.CalledProcessError as e:
            logger.error(f"자막 추출 실패: {video_path}, 오류: {e.returncode}")
            raise e
