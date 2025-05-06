from fastapi import HTTPException
from services.bot_recomments_service import BotRecommentsService
from schemas.bot_recomments_schema import BotRecommentsRequest, BotRecommentsResponse
from utils.error_handler import InvalidQueryParameterError, InvalidFormatError, InternalServerError

class BotRecommentsController:
    def __init__(self):
        self.service = BotRecommentsService()

    async def create_bot_recomments(self, request: BotRecommentsRequest) -> BotRecommentsResponse:
        try:
            # 서비스 호출
            return await self.service.generate_bot_recomments(request)

        except InvalidQueryParameterError as e:
            # 400 Bad Request: 필수 필드 누락
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_required_field",
                    "message": e.message if hasattr(e, 'message') else str(e),
                    "field": [e.field] if hasattr(e, 'field') and e.field else []
                }
            )

        except InvalidFormatError as e:
            # 422 Unprocessable Entity: 형식 오류
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "invalid_format",
                    "message": e.message if hasattr(e, 'message') else str(e),
                    "field": [e.field] if hasattr(e, 'field') and e.field else []
                }
            )

        except InternalServerError as e:
            # 500 Internal Server Error
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "internal_server_error",
                    "message": e.message if hasattr(e, 'message') else str(e)
                }
            )
