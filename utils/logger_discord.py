import logging
from utils.logging_discord import DiscordWebhookHandler

def setup_logging(log_path="ai-log.log"):
    # 루트 로거
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 중복 방지: 기존 핸들러 제거
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(console_handler)

    # Discord 핸들러
    discord_handler = DiscordWebhookHandler()
    discord_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(discord_handler)

    # Uvicorn 기본 핸들러 제거 + 루트 로그에 위임
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True  # 루트로 위임
