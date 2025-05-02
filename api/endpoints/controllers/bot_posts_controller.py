from fastapi import HTTPException
from services.bot_posts_service import BotPostsService
from schemas.bot_posts_schema import BotPostsRequest

class BotPostsController:
    def __init__(self):
        self.service = BotPostsService()

    async def create_bot_post(self, request: BotPostsRequest):
        try:
            # 서비스 계층 호출
            result = await self.service.generate_bot_post(request.posts)
            
            # loader가 반환한 status_code 검사
            if isinstance(result, dict) and result.get("status_code") != 200:
                # 실제 HTTP 에러로 변환해서 클라이언트에 전달
                raise HTTPException(
                    status_code=result["status_code"],
                    detail=result.get("content", "Unknown error")
                )

            # 3) 정상적인 경우, 실제 컨텐츠만 리턴
            return {"content": result["content"]}

        except HTTPException:
            # 위에서 던진 HTTPException은 그대로 다시 던집니다
            raise
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
