from pydantic import BaseModel

#bot 관련 schema가 공통으로 사용하는 클래스 분리

class UserInfoRequest(BaseModel):
    nickname : str
    class_name : str

class UserInfoResponse(BaseModel):
    id : int
    nickname : str
    class_name : str

class BaseMessageRequest(BaseModel):
    user : UserInfoRequest
    created_at : str
    content : str

class ErrorResponse(BaseModel):
    error : str
    message : str