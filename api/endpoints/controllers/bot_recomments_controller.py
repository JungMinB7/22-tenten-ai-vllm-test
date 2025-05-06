from fastapi import HTTPException
from services.bot_comments_service import BotCommentsService
from schemas.bot_comments_schema import BotCommentsRequest

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
