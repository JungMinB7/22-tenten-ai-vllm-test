from pydantic import BaseModel
from typing import List
from schemas.bot_posts_schema import UserInfo

class Message(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotChatsRequest(BaseModel):
    chat_room_id: int
    messages: List[Message] 