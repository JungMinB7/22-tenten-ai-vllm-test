from fastapi import APIRouter

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/")
async def create_bot_comment(post_id: int):
    """
    소셜봇이 특정 게시글에 댓글을 생성하는 엔드포인트
    """
    # TODO: 소셜봇 댓글 생성 로직 구현
    return {"message": "Bot comment creation endpoint", "post_id": post_id}