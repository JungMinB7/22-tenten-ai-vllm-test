import logging
import os
from pydantic import ValidationError
from schemas.bot_recomments_schema import BotRecommentsRequest, BotRecommentsResponse, BotRecommentResponseData
from schemas.bot_common_schema import UserInfoResponse
from core.prompt_templates.bot_recomments_prompt import BotRecommentsPrompt
from models.koalpha_loader import KoalphaLoader
from utils.error_handler import InvalidQueryParameterError, InvalidFormatError, InternalServerError

class BotRecommentsService:
    def __init__(self, app):
        self.logger = logging.getLogger(__name__)
        # FastAPI app의 state에서 koalpha 싱글턴 인스턴스를 받아옴
        self.koalpha = app.state.koalpha

    async def generate_bot_recomments(self, request: BotRecommentsRequest) -> BotRecommentsResponse:
        """
        소셜봇 대댓글을 생성하는 서비스
        Args:
            request: BotRecommentsRequest 객체
        Returns:
            BotRecommentsResponse: 생성된 대댓글 응답
        Raises:
            InvalidQueryParameterError: 필수 필드 누락
            InvalidFormatError: 요청 필드 형식 오류
            InternalServerError: 내부 서버 오류
        """
        try:
            # 필수 필드 검증: board_type, post, comment (recomments는 Optional)
            if not request.board_type:
                raise InvalidQueryParameterError(field="board_type")
            if not request.post or not request.comment:
                raise InvalidQueryParameterError(field="body")

            # 프롬프트 생성 및 AI 호출
            prompt = BotRecommentsPrompt()
            messages = prompt.json_to_messages(request)

            model_response = self.koalpha.get_response(messages)

            content = model_response.get("content", "")

            # 응답 데이터 구성
            bot_user = prompt.get_bot_user_info()
            data = BotRecommentResponseData(
                board_type=request.board_type,
                post_id=request.post.id,
                comment_id=request.comment.id,
                user=UserInfoResponse(**bot_user),
                content=content
            )

            return BotRecommentsResponse(
                message="소셜봇이 대댓글을 작성했습니다.",
                data=data
            )

        except InvalidQueryParameterError:
            # 400 Bad Request
            raise
          
        #fastapi에서는 필드 누락이랑 타입 불일치를 동일하게 422로 반환
        except ValidationError as ve:
            # Pydantic 검증 오류: 필드 누락과 타입 불일치 구분
            for err in ve.errors():
                # 필수 필드 누락(value_error.missing)
                if err.get('type') == 'value_error.missing':
                    # 누락된 필드 위치 추출
                    field = err.get('loc')[-1]
                    raise InvalidQueryParameterError(field=str(field))
            # 그 외 형식 오류는 422
            raise InvalidFormatError()
        except Exception as e:
            # 500 Internal Server Error
            self.logger.error(f"Error generating bot recomments: {e}", exc_info=True)
            raise InternalServerError()
