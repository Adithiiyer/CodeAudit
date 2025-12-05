from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReviewResultOut(BaseModel):
    id: int
    submission_id: int
    score: int
    summary: str
    issues: str
    llm_analysis: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionOut(BaseModel):
    id: int
    filename: str
    language: str
    status: str
    created_at: datetime
    review_result: Optional[ReviewResultOut]

    class Config:
        from_attributes = True
