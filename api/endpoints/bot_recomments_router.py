from fastapi import APIRouter
from api.endpoints.controllers.bot_recomments_controller import BotRecommentsController, BotRecommentsRequest

# APIRouter 인스턴스 생성
router = APIRouter()
controller = BotRecommentsController()

# 엔드포인트 예시
@router.post("/")
async def create_bot_recomment(request: BotRecommentsRequest):
    """
    소셜봇이 새로운 댓글을 생성하는 엔드포인트
    """
    return await controller.create_bot_recomment(request)