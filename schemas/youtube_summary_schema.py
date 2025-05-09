from pydantic import BaseModel, HttpUrl
from typing import Optional

class YouTubeSummaryRequest(BaseModel):
    url: str

class YouTubeSummaryData(BaseModel):
    summary: Optional[str] = None

class YouTubeSummaryResponse(BaseModel):
    message: str
    data: YouTubeSummaryData 