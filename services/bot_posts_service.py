from typing import List
import logging
from schemas.bot_posts_schema import Post

from core.prompt_templates.bot_posts_prompt import BotPostsPrompt
from models.koalpha_loader import KoalphaLoader

class BotPostsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_bot_post(self, posts: List[Post]) -> dict:
        """
        소셜봇 게시글을 생성하는 서비스
        Args:
            posts: 최근 5개의 게시글 정보
        Returns:
            생성된 소셜봇의 게시글
        """
        try:            
            # 실제 AI 모델을 통한 게시글 생성 로직 구현
            bot_post_prompt = BotPostsPrompt()
            messages = bot_post_prompt.json_to_messages(posts)

            koalpha=KoalphaLoader()
            response = koalpha.get_response(messages)

            # return {
            #     "status_code": response['status_code'],
            #     "message": "소셜봇이 게시물을 작성했습니다.",
            #     "user": {
            #                 "nickname": "roro.bot",
            #                 "class_name": "PANGYO_2"
            #             },
            #     "data": {
            #         "content": response['content']
            #     }
            # }
            return response
        except Exception as e:
            self.logger.error(f"Error generating bot post: {str(e)}")
            raise e
