from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.bot_posts_service import BotPostsService

class UserInfo(BaseModel):
    nickname: str
    class_name: str

class Post(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotPostsRequest(BaseModel):
    posts: List[Post]

class BotPostsController:
    def __init__(self):
        self.service = BotPostsService()

    async def create_bot_post(self, request: BotPostsRequest):
        try:
            # 서비스 계층 호출
            result = await self.service.generate_bot_post(request.posts)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
