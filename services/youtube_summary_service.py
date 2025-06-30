# #파일을 직접 실행할 때 사용
# import os
# import sys
# # 프로젝트 루트 디렉토리를 파이썬 경로에 추가
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)  # 프로젝트 루트는 한 단계 위
# sys.path.append(project_root)

import logging
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from schemas.youtube_summary_schema import YouTubeSummaryData, YouTubeSummaryResponse
from core.prompt_templates.youtube_summary_prompt import YoutubeSummaryPrompt
from utils.error_handler import InvalidYouTubeUrlError, SubtitlesNotFoundError, UnsupportedSubtitleLanguageError, VideoPrivateError, VideoNotFoundError
import os
from dotenv import load_dotenv
from langfuse import Langfuse
from datetime import datetime
import traceback
from fastapi import HTTPException
from utils.logger import log_inference_to_langfuse # Langfuse 로깅 함수 임포트

class YouTubeSummaryService:
    def __init__(self, app):
        self.logger = logging.getLogger(__name__)
        self.transcript_api = YouTubeTranscriptApi()
        # FastAPI app의 state에서 model 싱글턴 인스턴스를 받아옴
        self.model = app.state.model
        self.mode = self.model.mode
        print(f"MODE : {self.mode}")

        # Langfuse 초기화
        if os.environ.get("LLM_MODE") == "api-prod":
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)

        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST')
        )

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

        # Trace 시작
        trace = self.langfuse.trace(
            name="posts_youtube_service",
            input={"url": url},
            environment=self.mode
        )

        try : 

            # 1. URL 프로토콜 확인 및 보정
            url = self._ensure_url_scheme(url)

            # 2. video_id 추출
            video_id = self._extract_video_id(url)

            # 3. 자막 추출 및 예외 처리
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

            # 4. 자막 텍스트 전처리
            try:
                transcript_text = self._process_transcript(transcript)
                trace.update(input={"transcript_text": transcript_text})
                print(f"[DEBUG] transcript_text: {transcript_text}")
            except Exception as e:
                print(f"[ERROR] transcript 처리 실패: {e}")
                raise Exception(f"transcript 처리 실패: {e}")

            # 5. LLM을 통한 요약 생성
            summary = self._create_summary(transcript_text, trace)

            # 4) 최종 결과 기록 및 종료
            trace.update(output={"summary": summary})

            # Pydantic 모델 생성까지 감싸서 에러 로깅
            try:
                result = YouTubeSummaryResponse(
                    message="YouTube 영상이 요약되었습니다.",
                    data=YouTubeSummaryData(summary=summary)
                )
                return result
            except Exception as e:
                # Pydantic ValidationError 등 모든 예외 스택 출력
                self.logger.error("Response 모델 생성 실패", exc_info=True)
                traceback.print_exc()
                trace.update(status="error", error=str(e))

                # 클라이언트에 좀 더 구체적인 에러 메시지라도 남기려면 HTTPException 사용
                raise HTTPException(status_code=500, detail="Response Validation Error")

        except Exception as e:
            # 기존 예외 핸들러에도 스택 출력 추가
            self.logger.error("create_summary 실행 중 에러 발생", exc_info=True)
            traceback.print_exc()
            trace.update(status="error", error=str(e))
            # 그대로 에러를 올려 FastAPI가 500을 반환하도록 둡니다
            raise
    
    def _ensure_url_scheme(self, url: str) -> str:
        """
        유튜브 URL에서 프로토콜 확인 및 보정
        """
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

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

    def _split_transcript(self, transcript_text: str, chunk_size: int = 6500, overlap: int = 500) -> list:
        """
        긴 자막 텍스트를 chunk_size만큼 분할, 각 청크는 overlap만큼 겹침
        Returns: 청크 리스트
        """
        chunks = []
        start = 0
        length = len(transcript_text)
        while start < length:
            end = min(start + chunk_size, length)
            chunk = transcript_text[start:end]
            chunks.append(chunk)
            if end == length:
                break
            start = end - overlap  # 겹침 적용
        return chunks

    def _get_chunk_position(self, idx: int, total: int) -> str:
        """청크의 위치(시작/중간/끝) 문자열 반환"""
        if idx == 0:
            return "전체 텍스트의 시작 부분"
        elif idx == total - 1:
            return "전체 텍스트의 끝 부분"
        else:
            return "전체 텍스트의 중간 부분"

    def _create_summary(self, transcript_text: str, trace) -> str:
        """
        긴 자막도 청크로 분할하여 순차적으로 요약, 마지막에 통합 요약
        Args:
            transcript_text: 자막 텍스트
        Returns:
            요약 텍스트
        """
        chunk_size = 6500
        overlap = 500
        chunks = self._split_transcript(transcript_text, chunk_size, overlap)
        chunk_summaries = []
        prev_summary = None
        prompt_builder = YoutubeSummaryPrompt(self.mode)

        for idx, chunk in enumerate(chunks):
            position = self._get_chunk_position(idx, len(chunks))
            prompt_client, messages = prompt_builder.create_chunk_messages(chunk, position, prev_summary)
            
            start_time = datetime.now() # Generation 시작 시간
            response = self.model.get_response(
                messages, trace=trace, start_time=start_time, prompt=prompt_client, name="chunk_summary", adapter_type="youtube_summary"
            )
            end_time = datetime.now()

            content = response.get('content', None)

            # Langfuse 로깅 추가
            log_model_parameters = {
                "temperature": self.model.loader.temperature,
                "top_p": self.model.loader.top_p,
                "max_tokens": self.model.loader.max_tokens,
                "stop": self.model.loader.stop,
            }
            log_inference_to_langfuse(
                trace=trace,
                name="youtube_chunk_summary",
                prompt=prompt_client,
                messages=messages,
                content=content,
                model_name=self.model.loader.model_path,
                model_parameters=log_model_parameters,
                input_tokens=None,
                output_tokens=None,
                inference_time=(end_time - start_time).total_seconds(),
                start_time=start_time,
                end_time=end_time,
                error=None
            )

            chunk_summaries.append(content)
            prev_summary = content

        # Langfuse 로깅 추가 (최종 요약)
        log_model_parameters_final = {
            "temperature": self.model.loader.temperature,
            "top_p": self.model.loader.top_p,
            "max_tokens": self.model.loader.max_tokens,
            "stop": self.model.loader.stop,
        }

        # 모든 청크 요약을 다시 통합 요약
        if len(chunk_summaries) == 1:
            final_summary = chunk_summaries[0]

        else:
            # 통합 프롬프트
            prompt_client, messages = prompt_builder.create_final_messages(chunk_summaries)

            start_time = datetime.now() # Generation 시작 시간
            response = self.model.get_response(
                messages, trace=trace, start_time=start_time, prompt=prompt_client, name="final_summary", adapter_type="youtube_summary"
            )
            end_time = datetime.now()
            final_summary = response.get('content', None)

            
        log_inference_to_langfuse(
            trace=trace,
            name="youtube_final_summary",
            prompt=prompt_client,
            messages=messages,
            content=final_summary,
            model_name=self.model.loader.model_path,
            model_parameters=log_model_parameters_final,
            input_tokens=None,
            output_tokens=None,
            inference_time=(end_time - start_time).total_seconds(),
            start_time=start_time,
            end_time=end_time,
            error=None
        )

        return final_summary
    
# #파일을 직접 실행할 때 사용
# async def main():
#     service = YouTubeSummaryService()
#     url = "https://www.youtube.com/watch?v=fnCY6ysVkAg"
#     summary = await service.create_summary(url)
#     print(summary)

# if __name__ == "__main__":
#     asyncio.run(main())