import logging
from schemas.bot_posts_schema import BotPostsRequest, BotPostsResponse, BotPostResponseData, UserInfoResponse
from core.prompt_templates.bot_posts_prompt import BotPostsPrompt
from models.koalpha_loader import KoalphaLoader
from utils.error_handler import InvalidQueryParameterError, InternalServerError

class BotPostsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
        try:
            # 400 error : 게시글 개수 검증
            if len(request.posts) < 5:
                raise InvalidQueryParameterError()


            # 실제 AI 모델을 통한 게시글 생성 로직 구현
            bot_post_prompt = BotPostsPrompt()
            bot_user = bot_post_prompt.get_bot_user_info()
            messages = bot_post_prompt.json_to_messages(request.posts)

            koalpha=KoalphaLoader()
            model_response = koalpha.get_response(messages)
            content = model_response.get("content", "")

            # 응답 구조 생성
            data = BotPostResponseData(
                board_type=request.board_type,
                user=UserInfoResponse(**bot_user),
                content=content
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
            raise InternalServerError()