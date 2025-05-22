import logging
import requests
import traceback
import tempfile
import re
import os
from dotenv import load_dotenv

load_dotenv(override=True)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

class DiscordWebhookHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record).lower()

            if os.getenv("SEND_DISCORD_LOG", "False").lower() != "true":
                return

            # STARTUP/SHUTDOWN 및 기타 무시할 로그 제외
            if (
                any(skip in log_entry for skip in [
                    "application startup",
                    "application shutdown",
                    "started server process",
                    "finished server process",
                    "waiting for application shutdown",
                    "shutting down",
                    "changes detected"])
                    or re.search(r"\b\d+\s+changes?\s+detected\b", log_entry)
                ): return
                

            # 4xx 상태코드 포함 또는 ERROR 이상인 경우에만 전송
            if re.search(r"\b4\d{2}\b", log_entry) or record.levelno >= logging.ERROR:
                traceback_text = ""
                if record.exc_info:
                    traceback_text = ''.join(traceback.format_exception(*record.exc_info))
                full_log = f"{log_entry}\n\n{traceback_text}"

                if hasattr(record, 'request_info'):
                    full_log = f"[REQUEST INFO]\n{record.request_info}\n\n" + full_log

                with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt", encoding='utf-8') as temp_file:
                    temp_file.write(full_log)
                    temp_file.flush()
                    temp_file.seek(0)

                    files = {"file": (f"error_{record.created}.txt", temp_file)}
                    payload = {
                        "content": "🚨 에러 로그 발생: `{}`\n📎 첨부 로그 파일 확인".format(record.levelname)
                    }
                    requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)

        except Exception as e:
            print(f"⚠️ Discord 전송 실패: {e}")