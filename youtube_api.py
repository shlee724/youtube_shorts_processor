# -*- coding: utf-8 -*-
"""
YouTube API를 사용하여 쇼츠 영상 정보를 수집하는 모듈
"""

import re
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

from config import YOUTUBE_API_KEY, MAX_RESULTS_PER_REQUEST, API_REQUEST_DELAY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self):
        """YouTube API 클라이언트 초기화"""
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    def extract_channel_id(self, url: str) -> Optional[str]:
        """YouTube 채널 URL에서 채널 ID 추출"""
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_.-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username_or_id = match.group(1)

                # @ 형식이나 사용자명인 경우 채널 ID로 변환
                if '/channel/' not in url:
                    return self.get_channel_id_by_username(username_or_id)
                else:
                    return username_or_id

        return None

    def get_channel_id_by_username(self, username: str) -> Optional[str]:
        """사용자명으로 채널 ID 조회"""
        try:
            # @ 형식 처리
            if username.startswith('@'):
                username = username[1:]

            # forUsername으로 먼저 시도
            request = self.youtube.channels().list(
                part='id',
                forUsername=username
            )
            response = request.execute()

            if response['items']:
                return response['items'][0]['id']

            # 검색으로 시도
            search_request = self.youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=1
            )
            search_response = search_request.execute()

            if search_response['items']:
                return search_response['items'][0]['snippet']['channelId']

        except HttpError as e:
            logger.error(f"채널 ID 조회 중 오류: {e}")

        return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """채널 기본 정보 조회"""
        try:
            request = self.youtube.channels().list(
                part='snippet',
                id=channel_id
            )
            response = request.execute()

            if response['items']:
                return response['items'][0]['snippet']
        except HttpError as e:
            logger.error(f"채널 정보 조회 중 오류: {e}")

        return None

    def get_shorts_videos(self, channel_id: str, since_date: str) -> List[Dict]:
        """특정 날짜 이후의 쇼츠 영상 목록 조회"""
        videos = []
        next_page_token = None

        # 날짜 형식 변환
        since_datetime = datetime.strptime(since_date, '%Y-%m-%d')
        since_iso = since_datetime.replace(tzinfo=timezone.utc).isoformat()

        logger.info(f"채널 {channel_id}에서 {since_date} 이후의 쇼츠 영상 검색 중...")

        while True:
            try:
                # 채널의 최신 영상 검색
                search_request = self.youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    type='video',
                    order='date',
                    publishedAfter=since_iso,
                    maxResults=MAX_RESULTS_PER_REQUEST,
                    pageToken=next_page_token
                )
                search_response = search_request.execute()

                if not search_response['items']:
                    break

                # 영상 ID 목록 추출
                video_ids = [item['id']['videoId'] for item in search_response['items']]

                # 영상 상세 정보 조회
                videos_request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()

                # 쇼츠 영상 필터링
                for video in videos_response['items']:
                    if self.is_shorts_video(video):
                        video_info = {
                            'video_id': video['id'],
                            'url': f"https://www.youtube.com/watch?v={video['id']}",
                            'title': video['snippet']['title'],
                            'upload_date': video['snippet']['publishedAt'],
                            'view_count': int(video['statistics'].get('viewCount', 0)),
                            'like_count': int(video['statistics'].get('likeCount', 0)),
                            'comment_count': int(video['statistics'].get('commentCount', 0)),
                            'duration': video['contentDetails']['duration']
                        }
                        videos.append(video_info)
                        logger.info(f"쇼츠 영상 발견: {video_info['title']}")

                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    break

                time.sleep(API_REQUEST_DELAY)

            except HttpError as e:
                logger.error(f"영상 검색 중 오류: {e}")
                break

        logger.info(f"총 {len(videos)}개의 쇼츠 영상을 찾았습니다.")
        return videos

    def is_shorts_video(self, video: Dict) -> bool:
        """영상이 쇼츠인지 판단"""
        # 1. duration이 60초 이하인지 확인
        duration = video['contentDetails']['duration']
        if self.parse_duration_seconds(duration) > 60:
            return False

        # 2. 제목이나 설명에 #shorts가 있는지 확인
        title = video['snippet']['title'].lower()
        description = video['snippet']['description'].lower()

        if '#shorts' in title or '#shorts' in description or 'shorts' in title:
            return True

        # 3. 60초 이하면서 세로형 비율일 가능성이 높으므로 쇼츠로 간주
        return True

    def parse_duration_seconds(self, duration: str) -> int:
        """ISO 8601 duration을 초로 변환"""
        # PT1M30S -> 90 seconds
        import re

        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds
