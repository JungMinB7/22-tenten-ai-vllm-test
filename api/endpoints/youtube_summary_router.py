from fastapi import APIRouter
from api.endpoints.controllers.youtube_summary_controller import YouTubeSummaryController, YouTubeSummaryRequest

# APIRouter 인스턴스 생성
router = APIRouter()
controller = YouTubeSummaryController()

# 엔드포인트 예시
@router.post("/summary")
async def create_youtube_summary(request: YouTubeSummaryRequest):
    """
    YouTube 영상 URL을 받아서 요약본을 반환하는 엔드포인트
    """
    return await controller.create_summary(request)