import argparse
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.youtube_summary_router import router as youtube_router
from api.endpoints.bot_posts_router import router as bot_post_router
from api.endpoints.bot_recomments_router import router as bot_recomment_router
from api.endpoints.bot_chats_router import router as bot_chat_router

# CLI 인자 파싱 함수 추가
def parse_args():
    parser = argparse.ArgumentParser(description="텐텐 GPU 사용 모드 선택")
    parser.add_argument(
        "--mode",
        choices=["colab", "gcp"],
        default="colab",
        help="LLM inference 모드 선택 (colab: Ngrok/Colab, gcp: GCP 서버 직접 추론)"
    )
    return parser.parse_args()

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="텐텐 AI API",
    description="kakaobase 플랫폼을 위한 AI 기능",
    version="1.0.0"
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

# 라우터 등록
app.include_router(youtube_router, prefix="/posts/youtube", tags=["youtube"])
app.include_router(bot_post_router, prefix="/posts/bot", tags=["bot-posts"])
app.include_router(bot_recomment_router, prefix="/recomments/bot", tags=["bot-recomments"])
app.include_router(bot_chat_router, prefix="/chats/bot", tags=["bot-chats"])

# 서버 구동을 위한 설정
if __name__ == "__main__":
    args = parse_args()
    os.environ["LLM_MODE"] = args.mode
    print(f"실행 모드: {args.mode}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 개발 환경에서만 사용
    )