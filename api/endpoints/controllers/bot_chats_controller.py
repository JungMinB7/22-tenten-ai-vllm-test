from fastapi import HTTPException
from services.bot_chats_service import BotChatsService
from schemas.bot_chats_schema import BotChatsRequest

class BotChatsController:
    def __init__(self):
        self.service = BotChatsService()

    async def create_bot_chat(self, request: BotChatsRequest):
        try:
            # 서비스 계층 호출
            result = await self.service.generate_bot_chat(request.chat_room_id, request.messages)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
