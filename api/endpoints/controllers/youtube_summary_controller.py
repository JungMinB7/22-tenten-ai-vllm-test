from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from services.youtube_summary_service import YouTubeSummaryService

class YouTubeSummaryRequest(BaseModel):
    url: HttpUrl

class YouTubeSummaryController:
    def __init__(self):
        self.service = YouTubeSummaryService()

    async def create_summary(self, request: YouTubeSummaryRequest):
        try:
            # 서비스 계층 호출
            summary = await self.service.create_summary(str(request.url))
            return summary
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
