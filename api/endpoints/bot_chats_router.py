from fastapi import APIRouter, Request
from api.endpoints.controllers.bot_chats_controller import BotChatsController
from fastapi.responses import StreamingResponse
import asyncio
from schemas.bot_chats_schema import BotChatQueueRequest, BotChatQueueSuccessResponse, BotChatQueueErrorResponse
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks
# [REFACTOR] SSEManager 싱글턴 인스턴스 직접 사용
from core.sse_manager import sse_manager
import json
from datetime import datetime

# APIRouter 인스턴스 생성
router = APIRouter()


@router.get("/chat/stream")
async def stream_chat(request: Request):
    """
    서버 시작 시 AI 서버와 SSE 연결 수립
    """
    client_id = request.client.host
    try:
        queue = await sse_manager.connect(client_id)
        
        # 첫 연결 시 성공 메시지 전송
        initial_data = {"message": "SSE연결 완료"}
        await queue.put(f"data: {json.dumps(initial_data, ensure_ascii=False)}\n\n")

        async def event_generator():
            try:
                while True:
                    message = await queue.get()
                    yield message
            except asyncio.CancelledError:
                sse_manager.disconnect(client_id)

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "SSE연결 실패"}
        )


@router.post("/chat", response_model=BotChatQueueSuccessResponse)
async def process_chat(request: Request, body: BotChatQueueRequest, background_tasks: BackgroundTasks):
    """
    사용자 채팅을 받아 처리를 시작하고, SSE 채널로 스트리밍 전송
    """
    controller = BotChatsController(request.app)
    # 실제 처리는 백그라운드에서 수행
    background_tasks.add_task(controller.process_and_stream_chat, body)
    return {"message": "Stream Queue등록 완료"}


@router.delete("/chat/stream/{streamId}")
async def stop_stream_processing(request: Request, streamId: str):
    """
    스트리밍 종료 요청 엔드포인트
    """
    # TODO: streamId를 기준으로 실제 스트리밍 작업을 중단하는 로직 추가
    controller = BotChatsController(request.app)
    controller.service.delete_memory(streamId)
    return {"message": "Stream 종료 요청 수신 완료"}