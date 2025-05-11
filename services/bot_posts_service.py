import logging
import os
from datetime import datetime
from schemas.bot_posts_schema import BotPostsRequest, BotPostsResponse, BotPostResponseData, UserInfoResponse
from core.prompt_templates.bot_posts_prompt import BotPostsPrompt
from utils.error_handler import InvalidQueryParameterError, InternalServerError

from dotenv import load_dotenv
from langfuse import Langfuse

class BotPostsService:
    def __init__(self, app):
        self.logger = logging.getLogger(__name__)
        # FastAPI app의 state에서 koalpha 싱글턴 인스턴스를 받아옴
        self.koalpha = app.state.koalpha
        self.mode = self.koalpha.mode
        print(f"MODE : {self.mode}")
        
        # Langfuse 초기화
        load_dotenv(override=True)
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST')
        )

    async def generate_bot_post(self, request: BotPostsRequest) -> BotPostsResponse:
        """
        소셜봇 게시글을 생성하는 서비스
        Args:
            posts: 최근 5개의 게시글 정보
        Returns:
            생성된 소셜봇의 게시글
        Raises:
            InvalidQueryParameterError: posts 개수가 5개 미만인 경우
            InternalServerError: AI 서버 호출 실패 등 내부 오류 발생 시
        """
        # Langfuse trace 시작
        trace = self.langfuse.trace(
            name="bot_posts_service",
            metadata={
                "board_type": request.board_type,
                "post_count": len(request.posts)
            },
            input = request.posts
        )
        
        try:
            # 400 error : 게시글 개수 검증
            if len(request.posts) < 5:
                trace.update(
                    status="error",
                    error="Invalid number of posts",
                    metadata={"error_type": "InvalidQueryParameterError"}
                )
                raise InvalidQueryParameterError()

            # 실제 AI 모델을 통한 게시글 생성 로직 구현
            bot_post_prompt = BotPostsPrompt()
            bot_user = bot_post_prompt.get_bot_user_info()
            prompt_client, messages = bot_post_prompt.json_to_messages(request.posts, self.mode)

            # Generation 시작 시간
            start_time = datetime.now()
            model_response = self.koalpha.get_response(messages)
            end_time = datetime.now()

            content = model_response.get("content", "")

            # 응답 구조 생성
            data = BotPostResponseData(
                board_type=request.board_type,
                user=UserInfoResponse(**bot_user),
                content=content
            )

            # Generation 이벤트 기록 – prompt_client 변수로 더 명확히
            trace.generation(
                name="generate_bot_post",
                prompt=prompt_client,
                input={"messages": messages},
                output={"content": content},
                start_time=start_time,
                end_time=end_time
            )

            return BotPostsResponse(
                message="소셜봇이 게시물을 작성했습니다.",
                data=data
            )

        except InvalidQueryParameterError:
            # 400 에러는 그대로 상위로 전달
            raise

        except Exception as e:
            # 그 외 예기치 못한 오류는 500 에러로 래핑
            self.logger.error(f"Error generating bot post: {e}", exc_info=True)
            trace.update(
                status="error",
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "messages": messages if 'messages' in locals() else None
                }
            )
            raise InternalServerError()