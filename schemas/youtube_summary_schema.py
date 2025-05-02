from pydantic import BaseModel, HttpUrl

class YouTubeSummaryRequest(BaseModel):
    url: HttpUrl

class YouTubeSummaryResponse(BaseModel):
    video_id: str
    transcript: str
    summary: str | None = None 