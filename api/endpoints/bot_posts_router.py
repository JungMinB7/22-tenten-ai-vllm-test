from fastapi import APIRouter, Request
from api.endpoints.controllers.bot_posts_controller import BotPostsController, BotPostsRequest

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("")
async def create_bot_post(request: Request, body: BotPostsRequest):
    """
    소셜봇이 새로운 게시글을 생성하는 엔드포인트
    """
    # 요청마다 app 인스턴스를 controller에 전달해 싱글턴 모델을 사용
    controller = BotPostsController(request.app)
    return await controller.create_bot_post(body)