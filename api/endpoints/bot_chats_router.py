from fastapi import APIRouter, Request
from api.endpoints.controllers.bot_chats_controller import BotChatsController, BotChatsRequest
from fastapi.responses import StreamingResponse
import asyncio

# APIRouter 인스턴스 생성
router = APIRouter()

# 엔드포인트 예시
@router.post("")
async def create_bot_chat(request: Request, body: BotChatsRequest):
    """
    소셜봇이 새로운 채팅 메시지를 생성하는 엔드포인트
    """
    # 요청마다 app 인스턴스를 controller에 전달해 싱글턴 모델을 사용
    controller = BotChatsController(request.app)
    return await controller.create_bot_chat(body)

@router.get("/stream")
async def stream_bot_chat(request: Request, chat_room_id: str):
    """
    SSE 기반 소셜봇 채팅 스트리밍 엔드포인트
    - 클라이언트가 이 엔드포인트에 접속하면, AI 응답을 스트리밍 방식으로 전송
    """
    controller = BotChatsController(request.app)

    async def event_generator():
        # 실제로는 generate_bot_chat에서 스트리밍 토큰/문장 단위로 yield해야 함
        # 여기서는 예시로 한 번에 전체 응답을 전송
        body = type('obj', (object,), {"chat_room_id": chat_room_id, "messages": []})()  # 더미 메시지
        result = await controller.create_bot_chat(body)
        content = result["data"]["content"]
        # 실제 구현에서는 content를 토큰/문장 단위로 쪼개서 yield
        yield f"data: {content}\n\n"
        # 스트리밍 종료 이벤트
        yield "event: done\ndata: null\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.delete("/stream/{streamId}")
async def stop_stream(request: Request, streamId: str):
    """
    스트리밍 종료 요청 엔드포인트
    - streamId 기준으로 스트림/메모리/큐를 정리
    """
    controller = BotChatsController(request.app)
    # BotChatsService의 delete_memory 등 활용
    controller.service.delete_memory(streamId)
    return {"message": "Stream 종료 요청 수신 완료"}