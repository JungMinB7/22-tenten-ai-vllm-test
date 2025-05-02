from pydantic import BaseModel
from typing import List
from schemas.bot_posts_schema import UserInfo, Post

class Comment(BaseModel):
    id: int
    user: UserInfo
    created_at: str
    content: str

class BotCommentsRequest(BaseModel):
    post: Post
    comments: List[Comment] 