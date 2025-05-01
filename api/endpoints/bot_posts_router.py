from fastapi import APIRouter

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/")
async def create_bot_post():
    """
    소셜봇이 새로운 게시글을 생성하는 엔드포인트
    """
    # TODO: 소셜봇 게시글 생성 로직 구현
    return {"message": "Bot post creation endpoint"}
