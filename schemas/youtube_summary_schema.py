from pydantic import BaseModel, HttpUrl
from typing import Optional

class YouTubeSummaryRequest(BaseModel):
    url: HttpUrl

class YouTubeSummaryData(BaseModel):
    summary: Optional[str] = None

class YouTubeSummaryResponse(BaseModel):
    message: str
    data: YouTubeSummaryData 