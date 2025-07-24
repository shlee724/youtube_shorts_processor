# -*- coding: utf-8 -*-
"""
YouTube API를 사용하여 쇼츠 영상 정보를 수집하는 모듈
"""

import re
import logging
import time
import urllib.parse
from datetime import datetime, timezone
from typing import List, Dict, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import YOUTUBE_API_KEY, MAX_RESULTS_PER_REQUEST, API_REQUEST_DELAY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeAPI:
    def __init__(self):
        """YouTube API 클라이언트 초기화"""
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def extract_channel_id(self, url: str) -> Optional[str]:
        """YouTube 채널 URL에서 채널 ID 추출"""

        # URL 디코딩
        url = urllib.parse.unquote(url).strip("/")

        # 채널 ID 직접 추출 시도
        if "/channel/" in url:
            channel_id = url.split("/channel/")[-1]
            logger.info(f"채널 ID 직접 추출 성공: {channel_id}")
            return channel_id

        if "/user/" in url:
            username = url.split("/user/")[-1]
            logger.info(f"user형 URL 감지, 사용자명: {username}")
            return self.get_channel_id_by_username(username)

        username = None
        if "/@" in url:
            username = url.split("/@")[-1]
            logger.info(f"@형 URL 감지, 사용자명: {username}")
        else:
            # 닉네임 또는 기타 포맷에서 마지막 경로 추출
            username = url.split("/")[-1]
            logger.info(f"일반 URL 또는 닉네임 추출, 값: {username}")

        # @ 없애기
        if username.startswith("@"):
            username = username[1:]

        if username:
            return self.get_channel_id_by_username(username)

        logger.error("채널 ID 또는 사용자명 추출 실패")
        return None

    def get_channel_id_by_username(self, username: str) -> Optional[str]:
        """사용자명으로 채널 ID 조회"""
        try:
            # search() API 사용 → 닉네임 또는 채널명 검색 후 채널 ID 반환
            search_request = self.youtube.search().list(
                part="snippet",
                q=username,
                type="channel",
                maxResults=1,
            )
            response = search_request.execute()
            items = response.get("items", [])
            if items:
                channel_id = items[0]["snippet"]["channelId"]
                logger.info(f"채널 ID 검색 성공: {channel_id} (사용자명: {username})")
                return channel_id
            else:
                logger.warning(f"채널 ID 검색 결과 없음: {username}")
        except HttpError as e:
            logger.error(f"채널 ID 조회 중 오류: {e}")
        return None

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """채널 기본 정보 조회"""
        try:
            request = self.youtube.channels().list(part="snippet", id=channel_id)
            response = request.execute()
            items = response.get("items", [])
            if items:
                return items[0]["snippet"]
        except HttpError as e:
            logger.error(f"채널 정보 조회 중 오류: {e}")
        return None

    def get_shorts_videos(self, channel_id: str, since_date: str) -> List[Dict]:
        """특정 날짜 이후의 쇼츠 영상 목록 조회"""
        videos = []
        next_page_token = None

        # 날짜 형식 변환 및 ISO8601 UTC 포맷으로 변환
        since_datetime = datetime.strptime(since_date, "%Y-%m-%d")
        since_iso = since_datetime.replace(tzinfo=timezone.utc).isoformat()

        logger.info(f"채널 {channel_id}에서 {since_date} 이후의 쇼츠 영상 검색 중...")

        while True:
            try:
                search_request = self.youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    publishedAfter=since_iso,
                    maxResults=MAX_RESULTS_PER_REQUEST,
                    pageToken=next_page_token,
                )
                search_response = search_request.execute()
                items = search_response.get("items", [])
                if not items:
                    break

                video_ids = [item["id"]["videoId"] for item in items]

                videos_request = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(video_ids),
                )
                videos_response = videos_request.execute()

                for video in videos_response.get("items", []):
                    if self.is_shorts_video(video):
                        video_info = {
                            "video_id": video["id"],
                            "url": f"https://www.youtube.com/watch?v={video['id']}",
                            "title": video["snippet"]["title"],
                            "upload_date": video["snippet"]["publishedAt"],
                            "view_count": int(video["statistics"].get("viewCount", 0)),
                            "like_count": int(video["statistics"].get("likeCount", 0)),
                            "comment_count": int(video["statistics"].get("commentCount", 0)),
                            "duration": video["contentDetails"]["duration"],
                        }
                        videos.append(video_info)
                        logger.info(f"쇼츠 영상 발견: {video_info['title']}")

                next_page_token = search_response.get("nextPageToken")
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
        duration = video["contentDetails"]["duration"]
        if self.parse_duration_seconds(duration) > 60:
            return False

        title = video["snippet"]["title"].lower()
        description = video["snippet"]["description"].lower()

        if "#shorts" in title or "#shorts" in description or "shorts" in title:
            return True

        # 60초 이하면서 세로형 비율일 가능성(단순 판단) → 쇼츠로 간주
        return True

    def parse_duration_seconds(self, duration: str) -> int:
        """ISO 8601 duration을 초로 변환"""
        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds
    
    def get_channel_name(self, url: str) -> str:
        """
        채널 URL 또는 사용자명으로부터 채널 이름(제목) 얻기
        """
        channel_id = self.extract_channel_id(url)
        if not channel_id:
            return "UnknownChannel"
        
        try:
            request = self.youtube.channels().list(
                part="snippet",
                id=channel_id
            )
            response = request.execute()
            items = response.get("items", [])
            if items:
                return items[0]["snippet"]["title"]
        except Exception as e:
            logger.error(f"채널 이름 조회 중 오류: {e}")
        
        return "UnknownChannel"

