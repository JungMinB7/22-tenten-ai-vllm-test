from fastapi import status
from fastapi.responses import JSONResponse
from services.bot_posts_service import BotPostsService
from schemas.bot_posts_schema import BotPostsRequest, BotPostsResponse
from utils.error_handler import InvalidQueryParameterError, InternalServerError

class BotPostsController:
    def __init__(self, app):
        # FastAPI app 인스턴스를 받아 서비스에 전달
        self.app = app
        self.service = BotPostsService(app)

    async def create_bot_post(self, request: BotPostsRequest) -> BotPostsResponse:
        """
        BotPostsRequest를 받아 소셜봇 게시글 생성 서비스 호출 후,
        BotPostsResponse 형태로 반환.
        """
        try:
            # 서비스 계층 호출
            bot_response = await self.service.generate_bot_post(request)
            return bot_response

        except InvalidQueryParameterError as e:
            # 400 Bad Request: posts 개수 검증 실패
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "invalid_query_parameter",
                    "message": "전달받은 게시글이 5개 미만입니다."
                }
            )

        except InternalServerError as e:
            # 500 Internal Server Error: AI 서버 내부 오류
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "message": "AI 서버에 문제가 발생하였습니다."
                }
            )