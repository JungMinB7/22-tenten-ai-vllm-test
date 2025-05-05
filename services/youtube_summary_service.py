# #파일을 직접 실행할 때 사용
# import os
# import sys
# # 프로젝트 루트 디렉토리를 파이썬 경로에 추가
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)  # 프로젝트 루트는 한 단계 위
# sys.path.append(project_root)

from typing import Optional
import logging
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from schemas.youtube_summary_schema import YouTubeSummaryData, YouTubeSummaryResponse
from core.prompt_templates.youtube_summary_prompt import YoutubeSummaryPrompt
from models.koalpha_loader import KoalphaLoader
from utils.error_handler import InvalidYouTubeUrlError, SubtitlesNotFoundError, UnsupportedSubtitleLanguageError, VideoPrivateError, VideoNotFoundError

class YouTubeSummaryService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transcript_api = YouTubeTranscriptApi()

    async def create_summary(self, url: str) -> YouTubeSummaryResponse:
        """
        유튜브 영상의 자막을 추출하고, LLM을 통해 요약을 생성하는 서비스 함수
        Args:
            url: YouTube 영상 URL
        Returns:
            YouTubeSummaryResponse 객체 (message, data(summary))
        Raises:
            커스텀 예외 (InvalidYouTubeUrlError, SubtitlesNotFoundError, UnsupportedSubtitleLanguageError, VideoPrivateError, VideoNotFoundError)
        """
        # 1. video_id 추출
        video_id = self._extract_video_id(url)

        # 2. 자막 추출 및 예외 처리
        try:
            transcript = self.transcript_api.fetch(video_id, languages=['ko', 'en'])
            if not transcript:
                # 자막이 아예 없는 경우
                raise SubtitlesNotFoundError()
        except SubtitlesNotFoundError:
            raise
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG][youtube_transcript_api Exception] error_msg: {error_msg}")  # 개발/테스트용 에러 메시지 출력
            if 'Subtitles are disabled' in error_msg:
                # 유튜브 동영상에 자막이 없는 경우
                raise SubtitlesNotFoundError()
            elif """No transcripts were found for any of the requested language codes: ['ko', 'en']""" in error_msg:
                # 지원하지 않는 언어(한국어/영어가 아닌 자막)인 경우
                raise UnsupportedSubtitleLanguageError()
            elif 'The video is unplayable for the following reason: No reason specified!' in error_msg:
                # 비공개 동영상인 경우
                raise VideoPrivateError()
            elif 'The video is no longer available' in error_msg:
                # 존재하지 않는 동영상인 경우
                raise VideoNotFoundError()
            else:
                print(f"[ERROR] transcript 추출 실패: {e}")
                raise Exception(f"transcript 추출 실패: {e}")

        # 3. 자막 텍스트 전처리
        try:
            transcript_text = self._process_transcript(transcript)
        except Exception as e:
            print(f"[ERROR] transcript 처리 실패: {e}")
            raise Exception(f"transcript 처리 실패: {e}")

        # 4. LLM을 통한 요약 생성
        summary = self._create_summary(transcript_text)

        # 5. 결과 반환
        result = YouTubeSummaryResponse(
            message="YouTube 영상이 요약되었습니다.",
            data=YouTubeSummaryData(summary=summary)
        )
        return result

    def _extract_video_id(self, url: str) -> str:
        """
        유튜브 URL에서 video_id를 추출
        - 일반 영상: https://www.youtube.com/watch?v=video_id
        - 쇼츠: https://www.youtube.com/shorts/video_id
        - 단축 URL: https://youtu.be/video_id
        Raises:
            InvalidYouTubeUrlError: 유효하지 않은 URL인 경우
        """
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            # 쇼츠 링크 처리
            if parsed_url.path.startswith('/shorts/'):
                # youtube.com/shorts/video_id
                return parsed_url.path.split('/')[2]
            try:
                return parse_qs(parsed_url.query)['v'][0]
            except Exception:
                raise InvalidYouTubeUrlError()
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        else:
            raise InvalidYouTubeUrlError()

    def _process_transcript(self, transcript) -> str:
        """
        자막 리스트를 하나의 텍스트로 합침
        Args:
            transcript: FetchedTranscript 객체(리스트)
        Returns:
            처리된 자막 텍스트
        """
        return ' '.join([snippet.text for snippet in transcript])

    def _create_summary(self, transcript_text: str) -> str:
        """
        LLM(Koalpha)을 호출해 요약 텍스트를 생성
        Args:
            transcript_text: 자막 텍스트
        Returns:
            요약 텍스트
        """
        prompt = YoutubeSummaryPrompt()
        messages = prompt.create_messages(transcript_text)
        koalpha = KoalphaLoader()
        response = koalpha.get_response(messages)
        return response.get('content', None)
    
# #파일을 직접 실행할 때 사용
# async def main():
#     service = YouTubeSummaryService()
#     url = "https://www.youtube.com/watch?v=fnCY6ysVkAg"
#     summary = await service.create_summary(url)
#     print(summary)

# if __name__ == "__main__":
#     asyncio.run(main())