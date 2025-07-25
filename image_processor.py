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

    def combine_images(self, video_folder_path: str) -> str:
        """
        video_folder_path : 영상이 정리된 폴더 경로(제목 폴더)
        TXTImages 폴더의 모든 이미지를 세로로 합성, 결과 이미지를 video_folder_path에 저장
        """
        txt_images_path = os.path.join(video_folder_path, 'ResultsDir', 'TXTImages')
        images = []
        for file in sorted(os.listdir(txt_images_path)):
            if file.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                img = Image.open(os.path.join(txt_images_path, file))
                images.append(img)

        if not images:
            self.logger.warning("합성할 이미지가 없음: %s", txt_images_path)
            return None

        # 가장 넓은 이미지 기준으로
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)

        combined_img = Image.new('RGB', (max_width, total_height), (255, 255, 255))

        y_offset = 0
        for img in images:
            combined_img.paste(img, (0, y_offset))
            y_offset += img.height

        result_path = os.path.join(video_folder_path, "combined_result.png")
        combined_img.save(result_path)
        logger.info(f"이미지 합성 및 저장 완료: {result_path}")
        return result_path

    def resize_image_if_needed(self, image: Image.Image, max_width: int = 1920, max_height: int = 10800) -> Image.Image:
        """필요시 이미지 크기 조정"""
        if image.width > max_width or image.height > max_height:
            # 비율 유지하면서 크기 조정
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            logger.info(f"이미지 크기 조정: {image.width}x{image.height}")

        return image
