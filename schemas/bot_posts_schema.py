from pydantic import BaseModel
from typing import List

class UserInfo(BaseModel):
    nickname: str
    class_name: str

class Post(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotPostsRequest(BaseModel):
    posts: List[Post] 