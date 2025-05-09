from fastapi import APIRouter, Request
from api.endpoints.controllers.youtube_summary_controller import YouTubeSummaryController, YouTubeSummaryRequest

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/summary")
async def create_youtube_summary(request: Request, body: YouTubeSummaryRequest):
    """
    YouTube 영상 URL을 받아서 요약본을 반환하는 엔드포인트
    """
    # 요청마다 app 인스턴스를 controller에 전달해 싱글턴 모델을 사용
    controller = YouTubeSummaryController(request.app)
    return await controller.create_summary(body)