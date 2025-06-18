import logging
import os
from schemas.bot_recomments_schema import BotRecommentsRequest, BotRecommentsResponse, BotRecommentResponseData, UserInfoResponse
from core.prompt_templates.bot_recomments_prompt import BotRecommentsPrompt
from utils.error_handler import InvalidQueryParameterError, InternalServerError

from datetime import datetime
from dotenv import load_dotenv
from langfuse import Langfuse

import re
from utils.logger import log_inference_to_langfuse

class BotRecommentsService:
    def __init__(self, app):
        self.logger = logging.getLogger(__name__)
        # FastAPI app의 state에서 model 싱글턴 인스턴스를 받아옴
        self.model = app.state.model
        self.mode = self.model.mode
        print(f"MODE : {self.mode}")

        # Langfuse 초기화
        if os.environ.get("LLM_MODE") == "api-prod":
            load_dotenv(dotenv_path='/secrets/env')
        else:
            load_dotenv(override=True)

        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST')
        )
    def clean_response(self, text):
        # Remove everything before the first colon, inclusive
        if ':' in text:
            text = text.split(':', 1)[1]
        # Remove content inside square brackets including the brackets
        text = re.sub(r'\[.*?\]', '', text)
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def generate_bot_recomments(self, request: BotRecommentsRequest) -> BotRecommentsResponse:
        """
        소셜봇 대댓글을 생성하는 서비스
        Args:
            request: BotRecommentsRequest 객체
        Returns:
            BotRecommentsResponse: 생성된 대댓글 응답
        Raises:
            InvalidQueryParameterError: 필수 필드 누락
            InvalidFormatError: 요청 필드 형식 오류
            InternalServerError: 내부 서버 오류
        """
        # Langfuse trace 시작
        trace = self.langfuse.trace(
            name="bot_recomments_service",
            metadata={
                "board_type": request.board_type,
            },
            input = request,
            environment=self.mode
        )
        try:
            # 필수 필드 검증: board_type, post, comment (recomments는 Optional)
            if not request.board_type:
                trace.update(
                    status="error",
                    error="필수 필드 검증",
                    metadata={"error_type": 'InvalidQueryParameterError(field="board_type")'}
                )
                raise InvalidQueryParameterError(field="board_type")
            if not request.post or not request.comment:
                trace.update(
                    status="error",
                    error="필수 필드 검증",
                    metadata={"error_type": 'InvalidQueryParameterError(field="body")'}
                )
                raise InvalidQueryParameterError(field="body")

            # Langfuse 로깅 추가
            log_model_parameters = {
                "temperature": self.model.loader.temperature,
                "top_p": self.model.loader.top_p,
                "max_tokens": self.model.loader.max_tokens,
                "stop": self.model.loader.stop,
            }

            # 프롬프트 생성 및 AI 호출
            prompt = BotRecommentsPrompt()
            prompt_client, messages = prompt.json_to_messages(request, self.mode)

            # Generation 시작 시간
            start_time = datetime.now()
            model_response = self.model.get_response(
                messages, trace=trace, start_time=start_time, prompt=prompt_client, name="generate_bot_recomment"
            )
            end_time = datetime.now()

            original_content = model_response.get("content", "")

            log_inference_to_langfuse(
                trace=trace,
                name="generate_bot_recomment_original",
                prompt=prompt_client,
                messages=messages,
                content=original_content,
                model_name=self.model.loader.model_path,
                model_parameters=log_model_parameters,
                input_tokens=None,
                output_tokens=None,
                inference_time=(end_time - start_time).total_seconds(),
                start_time=start_time,
                end_time=end_time,
                error=None
            )

            print(f"content : {original_content}")
            print(f"inference_time : {(end_time - start_time).total_seconds()}")
            
            start_time = datetime.now()
            content = self.clean_response(original_content)
            end_time = datetime.now()

            log_inference_to_langfuse(
                trace=trace,
                name="generate_bot_recomment_cleaned",
                prompt=prompt_client,
                messages=messages,
                content=content,
                model_name=self.model.loader.model_path,
                model_parameters=log_model_parameters,
                input_tokens=None,
                output_tokens=None,
                inference_time=(end_time - start_time).total_seconds(),
                start_time=start_time,
                end_time=end_time,
                error=None
            )

            print(f"cleaned content : {content}")
            print(f"inference_time : {(end_time - start_time).total_seconds()}")

            # 최종 결과 기록
            trace.update(output=content)

            # 응답 데이터 구성
            bot_user = prompt.get_bot_user_info()
            data = BotRecommentResponseData(
                board_type=request.board_type,
                post_id=request.post.id,
                comment_id=request.comment.id,
                user=UserInfoResponse(**bot_user),
                content=content
            )

            return BotRecommentsResponse(
                message="소셜봇이 대댓글을 작성했습니다.",
                data=data
            )

        except InvalidQueryParameterError:
            # 400 Bad Request
            raise
        
        except Exception as e:
            # 500 Internal Server Error
            self.logger.error(f"Error generating bot recomments: {e}", exc_info=True)
            trace.update(
                status="error",
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "messages": messages if 'messages' in locals() else None,
                    "original_content": original_content if 'original_content' in locals() else None,
                    "cleaned_content": content if 'content' in locals() else None
                }
            )
            raise InternalServerError()
