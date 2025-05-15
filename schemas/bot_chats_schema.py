from pydantic import BaseModel
from typing import List
from schemas.bot_common_schema import UserInfoResponse, BaseMessageRequest
# Request Schemas

class BotChatsRequest(BaseModel):
    chat_room_id : str
    messages : List[BaseMessageRequest]

class BotChatResponseData(BaseModel):
    chat_room_id : int
    user : UserInfoResponse
    content : str


class BotChatsResponse(BaseModel):
    message : str
    data : BotChatResponseData