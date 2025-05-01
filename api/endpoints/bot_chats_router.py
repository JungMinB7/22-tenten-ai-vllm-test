from fastapi import APIRouter

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("/")
async def create_bot_chat_message(user_message: str):
    """
    사용자의 메시지를 받아 소셜봇이 응답하는 엔드포인트
    """
    # TODO: 소셜봇 채팅 응답 로직 구현
    return {"message": "Bot chat response endpoint", "user_message": user_message}