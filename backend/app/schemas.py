from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReviewResultOut(BaseModel):
    id: int
    submission_id: int
    score: int
    summary: str
    issues: str
    created_at: datetime

    class Config:
        orm_mode = True

class SubmissionOut(BaseModel):
    id: int
    filename: str
    language: str
    status: str
    created_at: datetime
    review_result: Optional[ReviewResultOut]

    class Config:
        orm_mode = True
