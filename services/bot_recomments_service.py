import logging
from schemas.bot_recomments_schema import BotRecommentsRequest, BotRecommentsResponse, BotRecommentResponseData, UserInfoResponse
from core.prompt_templates.bot_recomments_prompt import BotRecommentsPrompt
from models.koalpha_loader import KoalphaLoader
from utils.error_handler import InvalidQueryParameterError, InternalServerError


class BotRecommentsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_bot_comments(self, request: BotRecommentsRequest) -> BotRecommentsResponse:
        """
        소셜봇 대댓글을 생성하는 서비스
        Args:
            request: BotCommentsRequest 객체
        Returns:
            BotCommentsResponse: 생성된 대댓글 응답
        Raises:
            InvalidQueryParameterError: 필수 필드 누락 또는 형식 오류
            InternalServerError: AI 서버 호출 실패 등 내부 오류 발생 시
        """
        try:

            bot_comments_prompt = BotRecommentsPrompt()
            bot_user = bot_comments_prompt.get_bot_user_info()


            # 400 error : 소셜봇이 게시한 글에 달린 댓글이 아닌 경우?
            if not request.post.user.nickname == bot_user.nickname:
                raise InvalidQueryParameterError()

            # 모델을 통한 대댓글 생성 로직
            messages = bot_comments_prompt.json_to_messages(request.posts)
            koalpha = KoalphaLoader()
            model_response = koalpha.get_response(messages)
            content = model_response.get("content", "")

            # 응답 구조 생성
            data = BotRecommentResponseData(
                board_type=request.board_type,
                parent_comment_id=request.parent_comment_id,
                user=UserInfoResponse(**bot_user),
                content=content
            )

            return BotRecommentsResponse(
                message="소셜봇이 대댓글을 작성했습니다.",
                data=data
            )

        except InvalidQueryParameterError:
            # 400 에러는 그대로 상위로 전달
            raise

        except Exception as e:
            # 그 외 예기치 못한 오류는 500 에러로 래핑
            self.logger.error(f"Error generating bot comment: {e}", exc_info=True)
            raise InternalServerError()
