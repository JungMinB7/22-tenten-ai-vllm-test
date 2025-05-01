from fastapi import APIRouter

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/summary")
async def create_youtube_summary(url: str):
    """
    YouTube 영상 URL을 받아서 요약본을 반환하는 엔드포인트
    """
    # TODO: YouTube 요약 로직 구현
    return {"message": "YouTube summary endpoint", "url": url}