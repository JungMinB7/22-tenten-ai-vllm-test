from fastapi import APIRouter
from api.endpoints.controllers.bot_comments_controller import BotCommentsController, BotCommentsRequest

# APIRouter 인스턴스 생성
router = APIRouter()
controller = BotCommentsController()

# 엔드포인트 예시
@router.post("/")
async def create_bot_recomment(request: BotCommentsRequest):
    """
    소셜봇이 새로운 댓글을 생성하는 엔드포인트
    """
    return await controller.create_bot_comment(request)