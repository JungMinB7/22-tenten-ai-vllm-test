from fastapi import HTTPException
from services.bot_recomments_service import BotRecommentsService
from schemas.bot_recomments_schema import BotRecommentsRequest

class BotRecommentsController:
    def __init__(self):
        self.service = BotRecommentsService()

    async def create_bot_comment(self, request: BotRecommentsRequest):
        try:
            # 서비스 계층 호출
            result = await self.service.generate_bot_comment(request.post, request.comments)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
