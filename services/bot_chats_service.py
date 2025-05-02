from typing import List
import logging
from schemas.bot_chats_schema import Message

class BotChatsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_bot_chat(self, chat_room_id: int, messages: List[Message]) -> dict:
        """
        소셜봇 채팅 메시지를 생성하는 서비스
        Args:
            chat_room_id: 채팅방 ID
            messages: 채팅방의 메시지 기록
        Returns:
            생성된 소셜봇의 채팅 메시지
        """
        try:
            # 채팅 기록 분석
            context = self._analyze_chat_history(chat_room_id, messages)
            
            # TODO: 여기에 실제 AI 모델을 통한 채팅 메시지 생성 로직 구현
            # 현재는 임시 응답 반환
            return {
                "status": "success",
                "message": "Bot chat message generated successfully",
                "data": {
                    "content": "임시 소셜봇 채팅 메시지입니다."
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating bot chat message: {str(e)}")
            raise e

    def _analyze_chat_history(self, chat_room_id: int, messages: List[Message]) -> dict:
        """
        채팅 기록을 분석하여 컨텍스트를 추출하는 내부 메서드
        Args:
            chat_room_id: 채팅방 ID
            messages: 분석할 메시지 리스트
        Returns:
            분석된 컨텍스트 정보
        """
        return {
            "chat_room_id": chat_room_id,
            "messages_count": len(messages),
            "latest_message_time": messages[-1].created_at if messages else None,
            "participants": list(set(message.user.nickname for message in messages)),
            "last_user_message": messages[-1].content if messages else None
        }
