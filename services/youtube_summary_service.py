#파일을 직접 실행할 때 사용
import os
import sys
# 프로젝트 루트 디렉토리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 프로젝트 루트는 한 단계 위
sys.path.append(project_root)

from typing import Optional
import logging
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from schemas.youtube_summary_schema import YouTubeSummaryResponse
from core.prompt_templates.youtube_summary_prompt import YoutubeSummaryPrompt
from models.koalpha_loader import KoalphaLoader

class YouTubeSummaryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transcript_api = YouTubeTranscriptApi()

    async def create_summary(self, url: str) -> YouTubeSummaryResponse:
        """
        YouTube 영상의 자막을 추출하고 요약을 생성하는 서비스
        Args:
            url: YouTube 영상 URL
        Returns:
            생성된 요약 정보를 담은 YouTubeSummaryResponse 객체
        """

        video_id = self._extract_video_id(url)
        transcript = self.transcript_api.fetch(video_id, languages=['ko', 'en'])
        transcript_text = self._process_transcript(transcript)
        summary = self._create_summary(transcript_text)
  
        result = YouTubeSummaryResponse(
            video_id=video_id,
            transcript=transcript_text,
            summary=summary
        )
        return result

    def _create_summary(self, transcript_text: str) -> str:
        """
        Koalpha의 응답을 처리하여 요약 텍스트를 생성
        Args:
            transcript_text: 자막 텍스트
        Returns:
            요약 텍스트
        """
        prompt = YoutubeSummaryPrompt()
        messages = prompt.create_messages(transcript_text)
        koalpha = KoalphaLoader()
        response = koalpha.get_response(messages)
        #return response['content']
        return response.get('content', None)
        
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

    def _process_transcript(self, transcript: str) -> str:
        """
        추출된 자막을 처리하여 하나의 텍스트로 변환
        Args:
            transcript: FetchedTranscript 객체
        Returns:
            처리된 자막 텍스트
        """
        # 자막의 텍스트만 추출하여 하나의 문자열로 결합
        return ' '.join([snippet.text for snippet in transcript])
    
#파일을 직접 실행할 때 사용
async def main():
    service = YouTubeSummaryService()
    url = "https://www.youtube.com/watch?v=fnCY6ysVkAg"
    summary = await service.create_summary(url)
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())