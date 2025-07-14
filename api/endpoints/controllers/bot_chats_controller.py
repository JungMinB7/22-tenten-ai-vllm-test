from fastapi import HTTPException
from services.bot_chats_service import BotChatsService
from schemas.bot_chats_schema import BotChatsRequest

class BotChatsController:
    def __init__(self, app):
        # FastAPI app 인스턴스를 받아 서비스에 전달
        self.app = app
        self.service = BotChatsService(app)

    async def create_bot_chat(self, request: BotChatsRequest):
        try:
            # 서비스 계층 호출 (request 전체를 넘김)
            result = await self.service.generate_bot_chat(request)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
