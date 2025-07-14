from typing import List
import logging
from schemas.bot_chats_schema import BotChatsRequest, BotChatsResponse, BotChatResponseData, UserInfoResponse
import os
from models.model_loader import ModelLoader
from langchain.memory import ConversationBufferMemory

class BotChatsService:
    def __init__(self, app):
        self.logger = logging.getLogger(__name__)
        # FastAPI app의 state에서 model 싱글턴 인스턴스를 받아옴
        self.model = app.state.model

        # 각 stream_id별로 ConversationBufferMemory(k=5) 인스턴스를 관리
        self.memory_dict = {}  # key: stream_id, value: ConversationBufferMemory
        self.memory_k = 5  # 최근 5개 대화만 유지

    def get_memory(self, stream_id: str):
        """
        stream_id별 ConversationBufferMemory 인스턴스를 반환하거나 새로 생성
        """
        if stream_id not in self.memory_dict:
            self.memory_dict[stream_id] = ConversationBufferMemory(k=self.memory_k, return_messages=True)
        return self.memory_dict[stream_id]

    def add_message_to_memory(self, stream_id: str, role: str, content: str):
        """
        stream_id별 메모리에 메시지를 추가
        Args:
            stream_id (str): 대화 스트림 ID
            role (str): 'user' 또는 'ai' 등 역할
            content (str): 메시지 내용
        """
        memory = self.get_memory(stream_id)
        memory.save_context({"role": role}, {"content": content})

    def get_recent_messages(self, stream_id: str):
        """
        stream_id별 최근 대화 기록(최대 5개)을 반환
        Returns:
            List[dict]: [{role, content}, ...]
        """
        memory = self.get_memory(stream_id)
        # ConversationBufferMemory의 chat_memory.messages는 Message 객체 리스트
        # Message 객체는 .type (role), .content 속성 보유
        return [
            {"role": m.type, "content": m.content}
            for m in memory.chat_memory.messages
        ]

    async def generate_bot_chat(self, request: BotChatsRequest) -> BotChatsResponse:
        """
        소셜봇 채팅 메시지를 생성하는 서비스
        """
        try:
            # 채팅 기록 분석
            # context = self._analyze_chat_history(chat_room_id, messages)
            
            # TODO: 여기에 실제 AI 모델을 통한 채팅 메시지 생성 로직 구현
            # 현재는 임시 응답 반환
            
            # model_response = self.model.get_response(messages)
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
