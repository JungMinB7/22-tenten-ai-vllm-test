from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import status
import asyncio
from schemas.bot_chats_schema import BotChatQueueRequest
from core.sse_manager import sse_manager
import json
from datetime import datetime
from api.endpoints.controllers.bot_chats_controller import BotChatsController # 컨트롤러 임포트

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

# [REFACTOR] 컨트롤러를 사용하도록 로직 복구
@router.post("/chat", status_code=status.HTTP_202_ACCEPTED)
async def stream_queue(
    request: Request,
    queue_request: BotChatQueueRequest,
    background_tasks: BackgroundTasks,
):
    """
    채팅 메시지를 받아 컨트롤러를 통해 백그라운드 처리를 위해 큐에 등록
    """
    controller = BotChatsController(request.app)
    background_tasks.add_task(controller.process_and_stream_chat, queue_request)

    return {"message": "Stream Queue등록 완료"}


@router.delete("/chat/stream/{streamId}")
async def stop_stream_processing(request: Request, streamId: str):
    """
    스트리밍 종료 및 메모리 삭제 요청 엔드포인트
    """
    controller = BotChatsController(request.app)
    controller.delete_memory(streamId)
    
    # TODO: streamId를 기준으로 실제 스트리밍 작업을 중단하는 로직 추가
    return {"message": f"Stream({streamId}) 종료 및 메모리 삭제 완료"}