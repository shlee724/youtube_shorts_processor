# -*- coding: utf-8 -*-
"""
TXTImages의 이미지들을 세로로 합치는 모듈
"""

import os
import logging
from typing import List, Dict, Tuple
from PIL import Image, ImageOps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        """이미지 처리기 초기화"""
        pass

    def process_all_videos(self, processed_videos: List[Dict]) -> List[Dict]:
        """모든 영상의 자막 이미지 합성"""
        final_videos = []

        for video in processed_videos:
            try:
                result = self.combine_images_for_video(video)
                if result:
                    final_videos.append(result)
            except Exception as e:
                logger.error(f"이미지 합성 실패 - {video['title']}: {e}")
                continue

        logger.info(f"총 {len(final_videos)}개 영상 이미지 합성 완료")
        return final_videos

    def combine_images_for_video(self, video: Dict) -> Dict:
        """단일 영상의 TXTImages를 세로로 합성"""
        try:
            txt_images_dir = video.get('txt_images_dir')
            video_folder = video['video_folder']
            video_title = os.path.basename(video_folder)

            if not txt_images_dir or not os.path.exists(txt_images_dir):
                logger.warning(f"TXTImages 디렉토리가 없습니다: {video['title']}")
                return video

            # 이미지 파일 목록 가져오기
            image_files = self.get_image_files(txt_images_dir)

            if not image_files:
                logger.warning(f"합성할 이미지가 없습니다: {video['title']}")
                return video

            logger.info(f"이미지 합성 시작: {video['title']} ({len(image_files)}개 이미지)")

            # 이미지 합성
            combined_image = self.combine_images_vertically(image_files)

            if combined_image:
                # 결과 저장
                output_path = os.path.join(video_folder, f"{video_title}_combined.png")
                combined_image.save(output_path, 'PNG', quality=95)
                logger.info(f"합성 이미지 저장: {output_path}")

                # 업데이트된 정보 반환
                updated_video = video.copy()
                updated_video['combined_image_path'] = output_path
                updated_video['image_combined'] = True

                return updated_video
            else:
                logger.error(f"이미지 합성 실패: {video['title']}")
                return video

        except Exception as e:
            logger.error(f"이미지 합성 중 오류 - {video['title']}: {e}")
            return video

    def get_image_files(self, directory: str) -> List[str]:
        """디렉토리에서 이미지 파일 목록 가져오기"""
        if not os.path.exists(directory):
            return []

        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
        image_files = []

        for file in os.listdir(directory):
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(directory, file))

        # 파일명으로 정렬 (자막 순서 유지)
        image_files.sort()

        logger.info(f"발견된 이미지 파일: {len(image_files)}개")
        return image_files

    def combine_images_vertically(self, image_paths: List[str]) -> Image.Image:
        """이미지들을 세로로 합성"""
        if not image_paths:
            return None

        try:
            # 모든 이미지 로드 및 크기 확인
            images = []
            max_width = 0
            total_height = 0

            for image_path in image_paths:
                try:
                    img = Image.open(image_path)
                    # RGBA로 변환 (투명도 지원)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')

                    images.append(img)
                    max_width = max(max_width, img.width)
                    total_height += img.height

                except Exception as e:
                    logger.warning(f"이미지 로드 실패: {image_path} - {e}")
                    continue

            if not images:
                logger.error("로드된 이미지가 없습니다")
                return None

            # 합성할 캔버스 생성
            combined_image = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))

            # 이미지들을 세로로 배치
            current_y = 0
            for img in images:
                # 중앙 정렬을 위한 x 좌표 계산
                x_offset = (max_width - img.width) // 2

                # 이미지 붙여넣기
                combined_image.paste(img, (x_offset, current_y), img if img.mode == 'RGBA' else None)
                current_y += img.height

            # RGB로 변환 (PNG 저장을 위해)
            if combined_image.mode == 'RGBA':
                # 흰색 배경 생성
                background = Image.new('RGB', combined_image.size, (255, 255, 255))
                background.paste(combined_image, mask=combined_image.split()[-1])  # 알파 채널을 마스크로 사용
                combined_image = background

            logger.info(f"이미지 합성 완료: {max_width}x{total_height} pixels")
            return combined_image

        except Exception as e:
            logger.error(f"이미지 합성 중 오류: {e}")
            return None

    def resize_image_if_needed(self, image: Image.Image, max_width: int = 1920, max_height: int = 10800) -> Image.Image:
        """필요시 이미지 크기 조정"""
        if image.width > max_width or image.height > max_height:
            # 비율 유지하면서 크기 조정
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            logger.info(f"이미지 크기 조정: {image.width}x{image.height}")

        return image
