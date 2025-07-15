from fastapi import HTTPException
from services.bot_chats_service import BotChatsService
from schemas.bot_chats_schema import BotChatsRequest, BotChatQueueRequest

class BotChatsController:
    def __init__(self, app):
        """
        컨트롤러 생성자.
        [REFACTOR] 새로운 서비스 인스턴스를 생성하는 대신,
        app.state에 저장된 공유 BotChatsService 인스턴스를 사용합니다.
        """
        self.service: BotChatsService = app.state.bot_chats_service

    # --- 아래는 현재 라우터에서 사용되지 않는 레거시 메서드입니다 ---
    # async def create_bot_chat(self, request: BotChatsRequest):
    #     try:
    #         result = await self.service.generate_bot_chat(request)
    #         return result
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    # async def create_bot_chat_stream(self, request: BotChatsRequest):
    #     async for token in self.service.stream_bot_chat(request):
    #         yield token
    # ----------------------------------------------------------------

    async def process_and_stream_chat(self, request: BotChatQueueRequest):
        """
        공유 서비스의 채팅 처리 메서드를 호출합니다.
        """
        await self.service.process_chat_and_broadcast(request)

    def delete_memory(self, stream_id: str):
        """
        공유 서비스의 메모리 삭제 메서드를 호출합니다.
        """
        self.service.delete_memory(stream_id)
