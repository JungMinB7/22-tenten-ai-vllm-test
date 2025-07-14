from typing import List
import logging
from schemas.bot_chats_schema import BotChatsRequest, BotChatsResponse, BotChatResponseData, UserInfoResponse
import os
from models.model_loader import ModelLoader
from langchain.memory import ConversationBufferMemory

class BotChatsService:
    def __init__(self, app):
        """
        BotChatsService 생성자
        - FastAPI app의 state에서 모델 싱글턴 인스턴스를 받아옴
        - stream_id별 대화 메모리(ConversationBufferMemory) 딕셔너리 초기화
        """
        self.logger = logging.getLogger(__name__)
        self.model = app.state.model
        self.memory_dict = {}  # key: stream_id, value: ConversationBufferMemory
        self.memory_k = 5  # 최근 5개 대화만 유지

    def get_memory(self, stream_id: str):
        """
        stream_id별 ConversationBufferMemory 인스턴스를 반환하거나 새로 생성
        Args:
            stream_id (str): 대화 스트림 ID
        Returns:
            ConversationBufferMemory: 해당 stream_id의 메모리 인스턴스
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

    def delete_memory(self, stream_id: str):
        """
        stream_id별 ConversationBufferMemory 인스턴스를 메모리에서 삭제 (중단/파기)
        Args:
            stream_id (str): 대화 스트림 ID
        """
        if stream_id in self.memory_dict:
            del self.memory_dict[stream_id]

    def reset_memory(self, stream_id: str):
        """
        stream_id별 ConversationBufferMemory 인스턴스를 완전히 초기화(리셋)
        Args:
            stream_id (str): 대화 스트림 ID
        """
        if stream_id in self.memory_dict:
            self.memory_dict[stream_id] = ConversationBufferMemory(k=self.memory_k, return_messages=True)

    async def generate_bot_chat(self, request: BotChatsRequest) -> BotChatsResponse:
        """
        소셜봇 채팅 메시지를 생성하는 서비스
        1. stream_id별 대화 기록을 불러온다.
        2. 유저 메시지를 메모리에 추가한다.
        3. 최근 대화 맥락을 LLM 프롬프트로 활용하여 AI 응답을 생성한다.
        4. 생성된 AI 응답도 메모리에 추가한다.
        5. 예외 발생 시 해당 stream_id의 메모리를 삭제한다.

        
        Args:
            request (BotChatsRequest): 채팅 요청 객체
        Returns:
            BotChatsResponse: 생성된 채팅 응답
        Raises:
            Exception: LLM 호출 등 처리 중 에러 발생 시
        """
        stream_id = request.chat_room_id
        try:
            messages = request.messages
            # 1. 유저 메시지(가장 최근 메시지)를 메모리에 추가
            for msg in messages:
                self.add_message_to_memory(stream_id, msg.role, msg.content)
            # 2. 최근 대화 맥락을 LLM 프롬프트로 활용
            recent_messages = self.get_recent_messages(stream_id)
            # 3. LLM 호출 (social_bot 어댑터 사용)
            model_response = self.model.get_response(
                messages=recent_messages,
                trace=None,
                adapter_type="social_bot"
            )
            ai_content = model_response.get("content", "")
            # 4. AI 응답도 메모리에 추가
            self.add_message_to_memory(stream_id, "ai", ai_content)
            return {
                "status": "success",
                "message": "Bot chat message generated successfully",
                "data": {
                    "content": ai_content
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating bot chat message: {str(e)}")
            # 5. 예외 발생 시 해당 stream_id의 메모리를 삭제
            self.delete_memory(stream_id)
            raise e
