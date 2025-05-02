from fastapi import HTTPException
from services.bot_posts_service import BotPostsService
from schemas.bot_posts_schema import BotPostsRequest

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
