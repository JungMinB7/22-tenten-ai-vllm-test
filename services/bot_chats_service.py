from typing import List
import logging
from schemas.bot_chats_schema import BotChatsRequest, BotChatsResponse, BotChatResponseData, UserInfoResponse, BotChatQueueRequest
import os
from models.model_loader import ModelLoader
from langchain.memory import ConversationBufferMemory
import json
from datetime import datetime
from core.sse_manager import sse_manager

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

    # ==================================================================================
    # 아래의 generate_bot_chat, stream_bot_chat는 현재 API에서 사용되지 않는 레거시 함수일 수 있습니다.
    # 하지만 명세 통일을 위해 chat_room_id -> stream_id로 수정합니다.
    # ==================================================================================
    async def generate_bot_chat(self, request: BotChatsRequest) -> BotChatsResponse:
        """
        [LEGACY] 소셜봇 채팅 메시지를 생성하는 서비스
        """
        # [FIX] chat_room_id -> stream_id
        stream_id = request.stream_id 
        try:
            messages = request.messages
            for msg in messages:
                self.add_message_to_memory(stream_id, msg.role, msg.content)
            recent_messages = self.get_recent_messages(stream_id)
            model_response = self.model.get_response(
                messages=recent_messages,
                trace=None,
                adapter_type="social_bot"
            )
            ai_content = model_response.get("content", "")
            self.add_message_to_memory(stream_id, "ai", ai_content)
            return {
                "status": "success",
                "message": "Bot chat message generated successfully",
                "data": { "content": ai_content }
            }
        except Exception as e:
            self.logger.error(f"Error generating bot chat message: {str(e)}")
            self.delete_memory(stream_id)
            raise e

    async def stream_bot_chat(self, request: BotChatsRequest):
        """
        [LEGACY] LLM 응답을 토큰/문장 단위로 스트리밍하는 async generator
        """
        # [FIX] chat_room_id -> stream_id
        stream_id = request.stream_id
        messages = request.messages
        for msg in messages:
            self.add_message_to_memory(stream_id, msg.role, msg.content)
        recent_messages = self.get_recent_messages(stream_id)

        if hasattr(self.model, "stream_response"):
            async for token in self.model.stream_response(
                messages=recent_messages, trace=None, adapter_type="social_bot"
            ):
                yield token
        else:
            model_response = self.model.get_response(
                messages=recent_messages, trace=None, adapter_type="social_bot"
            )
            ai_content = model_response.get("content", "")
            self.add_message_to_memory(stream_id, "ai", ai_content)
            for sentence in ai_content.split(". "):
                yield sentence.strip()

    # ==================================================================================
    # 현재 실제 API (POST /chat)에서 사용되는 핵심 함수
    # ==================================================================================
    async def process_chat_and_broadcast(self, request: BotChatQueueRequest):
        """
        채팅을 처리하고, 생성된 응답을 SSEManager를 통해 브로드캐스트
        """
        # [FIX] request 객체의 올바른 필드 사용
        stream_id = request.stream_id
        
        try:
            # [FIX] 'messages'가 아닌 'message' 필드 사용
            self.add_message_to_memory(stream_id, "user", request.message)
            recent_messages = self.get_recent_messages(stream_id)

            model_response = self.model.get_response(
                messages=recent_messages, trace=None, adapter_type="social_bot"
            )
            ai_content = model_response.get("content", "")

            for token in ai_content:
                stream_data = {
                    "stream_id": stream_id,
                    "message": token,
                    "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                }
                await sse_manager.broadcast(f"event: stream\ndata: {json.dumps(stream_data, ensure_ascii=False)}\n\n")

            self.add_message_to_memory(stream_id, "ai", ai_content)
            
            done_data = {
                "stream_id": stream_id,
                "message": None,
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            }
            await sse_manager.broadcast(f"event: done\ndata: {json.dumps(done_data, ensure_ascii=False)}\n\n")

        except Exception as e:
            self.logger.error(f"Error processing chat for stream {stream_id}: {e}")
            self.delete_memory(stream_id)
            error_data = {
                "stream_id": stream_id,
                "message": str(e),
                "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            }
            await sse_manager.broadcast(f"event: error\ndata: {json.dumps(error_data, ensure_ascii=False)}\n\n")
