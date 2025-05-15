from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from services.youtube_summary_service import YouTubeSummaryService
from schemas.youtube_summary_schema import YouTubeSummaryRequest, YouTubeSummaryResponse
from utils.error_handler import InvalidYouTubeUrlError, SubtitlesNotFoundError, UnsupportedSubtitleLanguageError, VideoPrivateError, VideoNotFoundError

class YouTubeSummaryController:
    def __init__(self, app):
        # FastAPI app 인스턴스를 받아 서비스에 전달
        self.app = app
        self.service = YouTubeSummaryService(app)

    async def create_summary(self, request: YouTubeSummaryRequest) -> YouTubeSummaryResponse:
        try:
            result = await self.service.create_summary(str(request.url))
            return result
        except InvalidYouTubeUrlError:
            # 잘못된 유튜브 URL 형식
            return JSONResponse(status_code=400, content={
                "error": "invalid_format",
                "message": "YouTube URL 형식이 유효하지 않습니다."
            })
        except SubtitlesNotFoundError:
            # 유튜브 동영상에 자막이 없는 경우
            return JSONResponse(status_code=404, content={
                "error": "subtitles_not_found",
                "message": "해당 YouTube 영상에 자막이 존재하지 않습니다."
            })
        except UnsupportedSubtitleLanguageError:
            # 지원하지 않는 언어(한국어/영어가 아닌 자막)인 경우
            return JSONResponse(status_code=415, content={
                "error": "unsupported_subtitle_language",
                "message": "해당 YouTube 영상의 자막이 지원하는 언어가 한국어 또는 영어가 아닙니다."
            })
        except VideoPrivateError:
            # 비공개 동영상인 경우
            return JSONResponse(status_code=403, content={
                "error": "video_private",
                "message": "해당 YouTube 영상은 비공개 동영상입니다."
            })
        except VideoNotFoundError:
            # 존재하지 않는 동영상인 경우
            return JSONResponse(status_code=404, content={
                "error": "video_not_found",
                "message": "해당 YouTube 영상은 존재하지 않는 동영상입니다."
            })
        except Exception:
            # 서버 내부 오류, LLM 등 기타 예외 상황
            return JSONResponse(status_code=500, content={
                "error": "internal_server_error",
                "message": "AI 서버에 문제가 발생하였습니다."
            })