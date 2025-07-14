from pydantic import BaseModel
from typing import List
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest
# Request Schemas

class BotChatsRequest(BaseModel):
    stream_id : str
    messages : List[BaseMessageRequest]

class BotChatResponseData(BaseModel):
    chat_room_id : int
    user : UserInfoResponse
    content : str


class BotChatsResponse(BaseModel):
    message : str
    data : BotChatResponseData

class BotChatQueueRequest(BaseModel):
    stream_id: str
    user_id: int
    nickname: str
    class_name: str
    message: str
    timestamp: str  # yyyy-MM-dd'T'HH:mm:ss

class BotChatQueueSuccessResponse(BaseModel):
    message: str

class BotChatQueueErrorResponse(BaseModel):
    error: str
    message: str