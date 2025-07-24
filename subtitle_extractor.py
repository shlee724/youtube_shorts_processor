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

    def extract_subtitles_from_videos(self, organized_videos: List[Dict]) -> List[Dict]:
        """모든 영상에서 자막 추출"""
        processed_videos = []

        for video in organized_videos:
            try:
                result = self.extract_subtitle_from_video(video)
                if result:
                    processed_videos.append(result)
            except Exception as e:
                logger.error(f"자막 추출 실패 - {video['title']}: {e}")
                continue

        logger.info(f"총 {len(processed_videos)}개 영상 자막 추출 완료")
        return processed_videos

    def extract_subtitle_from_video(self, video: Dict) -> Dict:
        """단일 영상에서 자막 추출"""
        try:
            video_file_path = video['video_file_path']
            video_folder = video['video_folder']

            # ResultsDir 경로 생성
            results_dir = os.path.join(video_folder, "ResultsDir")
            if not os.path.exists(results_dir):
                os.makedirs(results_dir, exist_ok=True)

            # VideoSubFinder 명령어 구성
            # 사용자 요청 형식: C:\Users\이승호_\Desktop\video_sub_finder\VideoSubFinderWXW.exe -c -r -ccti -i "input_path" -o "output_path" -te 0.41
            cmd = [
                self.videosubfinder_path,
                *VIDEOSUBFINDER_OPTIONS,  # ['-c', '-r', '-ccti']
                '-i', video_file_path,
                '-o', results_dir,
                '-te', VIDEOSUBFINDER_THRESHOLD
            ]

            logger.info(f"자막 추출 시작: {video['title']}")
            logger.info(f"명령어: {' '.join(cmd)}")

            # VideoSubFinder 실행
            if os.path.exists(self.videosubfinder_path):
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=300  # 5분 타임아웃
                )

                if result.returncode == 0:
                    logger.info(f"자막 추출 완료: {video['title']}")

                    # TXTImages 디렉토리 확인
                    txt_images_dir = os.path.join(results_dir, "TXTImages")
                    if os.path.exists(txt_images_dir):
                        image_count = len([f for f in os.listdir(txt_images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                        logger.info(f"추출된 자막 이미지: {image_count}개")

                    # 업데이트된 정보 반환
                    updated_video = video.copy()
                    updated_video['results_dir'] = results_dir
                    updated_video['txt_images_dir'] = txt_images_dir
                    updated_video['subtitle_extracted'] = True

                    return updated_video
                else:
                    logger.error(f"VideoSubFinder 실행 실패: {result.stderr}")
                    return None
            else:
                logger.error(f"VideoSubFinder 실행 파일이 존재하지 않습니다: {self.videosubfinder_path}")

                # VideoSubFinder가 없어도 더미 디렉토리 생성 (테스트용)
                txt_images_dir = os.path.join(results_dir, "TXTImages")
                if not os.path.exists(txt_images_dir):
                    os.makedirs(txt_images_dir, exist_ok=True)

                updated_video = video.copy()
                updated_video['results_dir'] = results_dir
                updated_video['txt_images_dir'] = txt_images_dir
                updated_video['subtitle_extracted'] = False

                return updated_video

        except subprocess.TimeoutExpired:
            logger.error(f"자막 추출 타임아웃 - {video['title']}")
            return None
        except Exception as e:
            logger.error(f"자막 추출 중 오류 - {video['title']}: {e}")
            return None

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

    def verify_extraction_results(self, video: Dict) -> bool:
        """자막 추출 결과 확인"""
        if not video.get('txt_images_dir'):
            return False

        txt_images_dir = video['txt_images_dir']
        if not os.path.exists(txt_images_dir):
            return False

        # 이미지 파일 개수 확인
        image_files = [f for f in os.listdir(txt_images_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        return len(image_files) > 0
