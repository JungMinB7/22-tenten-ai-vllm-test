from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from services.bot_chats_service import BotChatsService

class UserInfo(BaseModel):
    nickname: str
    class_name: str

class Message(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotChatsRequest(BaseModel):
    chat_room_id: int
    messages: List[Message]

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
