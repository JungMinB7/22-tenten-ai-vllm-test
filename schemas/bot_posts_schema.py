from pydantic import BaseModel
from typing import List
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest

# Request Schemas
class PostRequest(BaseMessageRequest):
    pass
    
class BotPostsRequest(BaseModel):
    board_type: str
    posts: List[PostRequest]

# Response Schemas
class UserInfoResponse(BaseModel):
    id: int
    nickname: str
    class_name: str

class BotPostResponseData(BaseModel):
    board_type: str
    user: UserInfoResponse
    content: str

class BotPostsResponse(BaseModel):
    message: str
    data: BotPostResponseData
