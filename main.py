import argparse
import os
from dotenv import load_dotenv # dotenv 임포트

# [FIX] 애플리케이션 시작 시점에 환경 변수를 가장 먼저 로드
load_dotenv(override=True)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.youtube_summary_router import router as youtube_router
from api.endpoints.bot_posts_router import router as bot_post_router
from api.endpoints.bot_recomments_router import router as bot_recomment_router
from api.endpoints.bot_chats_router import router as bot_chat_router
from models.model_loader import ModelLoader 

from api.endpoints.discord_webhook_router import router as discord_router ## for Discord Webhook
from utils.logger_discord import setup_logging
from utils.exception_handler import register_exception_handlers
import json
from datetime import datetime
from contextlib import asynccontextmanager
from core.sse_manager import sse_manager
from services.bot_chats_service import BotChatsService # BotChatsService 임포트

# CLI 인자 파싱 함수 추가
def parse_args():
    parser = argparse.ArgumentParser(description="텐텐 GPU 사용 모드 선택")
    parser.add_argument(
        "--mode",
        choices=["colab", "gcp-dev", "gcp-prod", "api-dev", "api-prod"],
        default="colab",
        help="LLM inference 모드 선택 (colab: Ngrok/Colab, gcp-dev: 배포용 GCP 서버, gcp-prod: 개발용 GCP 서버, api-dev: gemini 2.0 flash api 사용 및 로컬 환경변수 사용, api-prod: gemini 2.0 flash api 사용 및 GCP 환경변수 사용)"
    )
    return parser.parse_args()

# [REFACTOR] Lifespan 이벤트를 사용하여 모델 로딩 시점 제어
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 실행
    print("서버 시작: 모델, SSEManager, BotChatsService 로딩을 시작합니다.")
    llm_mode = os.environ.get("LLM_MODE", "colab")
    app.state.model = ModelLoader(mode=llm_mode)
    app.state.sse_manager = sse_manager
    app.state.bot_chats_service = BotChatsService(app) # BotChatsService 인스턴스 생성 및 상태 저장
    print("서버 시작: 모델, SSEManager, BotChatsService 로딩 완료.")
    yield
    # 서버 종료 시 실행 (필요 시 리소스 정리)
    print("서버 종료.")


# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="텐텐 AI API",
    description="kakaobase 플랫폼을 위한 AI 기능",
    version="1.0.0",
    lifespan=lifespan  # Lifespan 관리자 등록
)

# origins 설정
origins = [
    "http://www.kakaobase.com",
    "https://www.kakaobase.com",
    "http://localhost:8080",
    "http://localhost:3000"
]

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 디스코드 웹훅 로깅 설정: 파일 + 콘솔 + Discord
setup_logging("ai-log.log")
# 디스코드 웹훅 예외 핸들러 등록
register_exception_handlers(app)


# 라우터 등록
app.include_router(youtube_router, prefix="/posts/youtube", tags=["youtube"])
app.include_router(bot_post_router, prefix="/posts/bot", tags=["bot-posts"])
app.include_router(bot_recomment_router, prefix="/recomments/bot", tags=["bot-recomments"])
# [REFACTOR] API 명세에 맞게 prefix 제거, 태그 수정
app.include_router(bot_chat_router, prefix="", tags=["Bot Chats (Streaming)"])
app.include_router(discord_router, prefix="/error_log", tags=["discord-webhook"]) # Discord Webhook router

# 서버 구동을 위한 설정
if __name__ == "__main__":
    args = parse_args()
    os.environ["LLM_MODE"] = args.mode

    reload_flag = True
    if os.environ["LLM_MODE"] in ["gcp-dev", "gcp-prod", "api-dev", "api-prod"]:
        reload_flag = False

    print(f"실행 모드: {args.mode}, reload : {reload_flag}")
    

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_flag   # 개발 환경에서만 사용
    )