from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from services.bot_comments_service import BotCommentsService

class UserInfo(BaseModel):
    nickname: str
    class_name: str

class Post(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class Comment(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotCommentsRequest(BaseModel):
    post: Post
    comments: List[Comment]

class BotCommentsController:
    def __init__(self):
        self.service = BotCommentsService()

    async def create_bot_comment(self, request: BotCommentsRequest):
        try:
            # 서비스 계층 호출
            result = await self.service.generate_bot_comment(request.post, request.comments)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
