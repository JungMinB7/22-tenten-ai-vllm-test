from pydantic import BaseModel
from typing import List
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest
 

class BotCommentsRequest(BaseModel):
    board_type: str
    post: BaseMessageRequest
    parent_comment_id: int
    comments: List[BaseMessageRequest]

class BotCommentResponseData(BaseModel):
    board_type: str
    parent_comment_id: int
    user: UserInfoResponse
    content: str

class BotCommentsResponse(BaseModel):
    message: str
    data: BotCommentResponseData