from fastapi import APIRouter, Request
from api.endpoints.controllers.bot_recomments_controller import BotRecommentsController, BotRecommentsRequest

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/")
async def create_bot_recomments(request: Request, body: BotRecommentsRequest):
    """
    소셜봇이 새로운 댓글을 생성하는 엔드포인트
    """
    # 요청마다 app 인스턴스를 controller에 전달해 싱글턴 모델을 사용
    controller = BotRecommentsController(request.app)
    return await controller.create_bot_recomments(body)