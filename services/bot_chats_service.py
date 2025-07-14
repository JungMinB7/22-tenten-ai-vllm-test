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
