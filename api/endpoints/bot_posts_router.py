from fastapi import APIRouter
from api.endpoints.controllers.bot_posts_controller import BotPostsController, BotPostsRequest

# APIRouter 인스턴스 생성
router = APIRouter()
controller = BotPostsController()

# 엔드포인트 예시
@router.post("/")
async def create_bot_post(request: BotPostsRequest):
    """
    소셜봇이 새로운 게시글을 생성하는 엔드포인트
    """
    return await controller.create_bot_post(request)
