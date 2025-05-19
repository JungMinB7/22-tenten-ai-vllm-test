from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

def register_exception_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        extra = {'request_info': f"{request.method} {request.url} (status: {exc.status_code})"}
        logging.error(f"HTTP 예외 발생: {exc.detail}", exc_info=True, extra=extra)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        extra = {'request_info': f"{request.method} {request.url} (status: 422)"}
        logging.error("요청 유효성 검증 실패", exc_info=True, extra=extra)
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        extra = {'request_info': f"{request.method} {request.url} (status: 500)"}
        logging.exception("알 수 없는 서버 예외 발생", extra=extra)
        return JSONResponse(status_code=500, content={"detail": "서버 내부 오류가 발생했습니다"})