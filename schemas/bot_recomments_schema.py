from pydantic import BaseModel
from typing import List, Optional
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest

class PostRequest(BaseMessageRequest):
    id: int

class CommentWithRecommentsRequest(BaseMessageRequest):
    id: int
    # recomments 배열이 비어있을 수 있으므로 기본값을 빈 리스트로 설정
    recomments: Optional[List[BaseMessageRequest]] = []

class BotRecommentsRequest(BaseModel):
    board_type: str
    post: PostRequest
    comment: CommentWithRecommentsRequest

class BotRecommentResponseData(BaseModel):
    board_type: str
    post_id: int
    comment_id: int
    user: UserInfoResponse
    content: str

class BotRecommentsResponse(BaseModel):
    message: str
    data: BotRecommentResponseData