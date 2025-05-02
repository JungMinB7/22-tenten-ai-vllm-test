from typing import Dict, Any, Optional
import logging
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YouTubeSummaryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transcript_api = YouTubeTranscriptApi()

    async def create_summary(self, url: str) -> dict:
        """
        YouTube 영상의 자막을 추출하고 요약을 생성하는 서비스
        Args:
            url: YouTube 영상 URL
        Returns:
            생성된 요약 정보를 담은 딕셔너리
        """
        try:
            # URL에서 video_id 추출
            video_id = self._extract_video_id(url)
            
            # 자막 추출 (기본값: 영어)
            transcript = self.transcript_api.fetch(video_id, languages=['ko', 'en'])
            
            # 자막 텍스트 추출 및 전처리
            transcript_text = self._process_transcript(transcript)
            
            # TODO: LLM을 통한 요약 생성 로직 구현
            
            return {
                "status": "success",
                "message": "Transcript extracted successfully",
                "data": {
                    "video_id": video_id,
                    "transcript": transcript_text,
                    # TODO: summary 필드는 LLM 요약 후 추가
                }
            }
        except Exception as e:
            self.logger.error(f"Error in create_summary: {str(e)}")
            raise e

    def _extract_video_id(self, url: str) -> str:
        """
        YouTube URL에서 video_id를 추출
        Args:
            url: YouTube 영상 URL
        Returns:
            video_id: 추출된 비디오 ID
        """
        parsed_url = urlparse(url)
        
        # youtube.com/watch?v=<video_id> 형식
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query)['v'][0]
        # youtu.be/<video_id> 형식
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        else:
            raise ValueError("Invalid YouTube URL")

    def _process_transcript(self, transcript) -> str:
        """
        추출된 자막을 처리하여 하나의 텍스트로 변환
        Args:
            transcript: FetchedTranscript 객체
        Returns:
            처리된 자막 텍스트
        """
        # 자막의 텍스트만 추출하여 하나의 문자열로 결합
        return ' '.join([snippet.text for snippet in transcript])
    
async def main():
    service = YouTubeSummaryService()
    url = "https://www.youtube.com/watch?v=fnCY6ysVkAg"
    summary = await service.create_summary(url)
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())