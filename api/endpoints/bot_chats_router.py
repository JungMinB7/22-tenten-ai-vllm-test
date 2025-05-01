from fastapi import APIRouter
from api.endpoints.controllers.bot_chats_controller import BotChatsController, BotChatsRequest

# APIRouter 인스턴스 생성
router = APIRouter()
controller = BotChatsController()

@router.post("/")
async def create_bot_chat(request: BotChatsRequest):
    """
    소셜봇이 새로운 채팅 메시지를 생성하는 엔드포인트
    """
    return await controller.create_bot_chat(request)