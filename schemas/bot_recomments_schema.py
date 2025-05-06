from pydantic import BaseModel
from typing import List
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest
 

class BotRecommentsRequest(BaseModel):
    board_type: str
    post: BaseMessageRequest
    parent_comment_id: int
    comments: List[BaseMessageRequest]

class BotRecommentResponseData(BaseModel):
    board_type: str
    parent_comment_id: int
    user: UserInfoResponse
    content: str

class BotRecommentsResponse(BaseModel):
    message: str
    data: BotRecommentResponseData