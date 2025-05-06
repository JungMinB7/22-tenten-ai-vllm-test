from fastapi import APIRouter
from schemas.bot_recomments_schema import BotRecommentsRequest, BotRecommentsResponse
from api.endpoints.controllers.bot_recomments_controller import BotRecommentsController

# APIRouter 인스턴스 생성
router = APIRouter()
controller = BotRecommentsController()

# 엔드포인트 예시
@router.post(
        "/",
        response_model=BotRecommentsResponse,
        summary="소셜봇 대댓글 작성",
        description="POST recomments/bot 으로 대댓글 생성 요청"
        )
async def create_bot_recomments(request: BotRecommentsRequest):
    """
    소셜봇이 새로운 댓글을 생성하는 엔드포인트
    """
    return await controller.create_bot_recomments(request)