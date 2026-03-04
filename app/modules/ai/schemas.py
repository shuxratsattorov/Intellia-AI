from pydantic import BaseModel, Field
from typing import Literal, Optional


CitationStyle = Literal["APA 7", "MLA 9", "Harvard", "GOST", "Chicago Notes"]

class GenerateReportRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    language: str = Field(max_length=8)
    education_level: str = Field(max_length=16)
    citation_style: CitationStyle = "APA 7"
    pages: int = Field(ge=6, le=50)
    total_target_words: Optional[int] = None
