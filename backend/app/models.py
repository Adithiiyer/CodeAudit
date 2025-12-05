from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    storage_path = Column(String)
    language = Column(String)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    review_result = relationship("ReviewResult", back_populates="submission", uselist=False)


class ReviewResult(Base):
    __tablename__ = "review_results"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), unique=True)
    score = Column(Integer)
    summary = Column(Text)
    issues = Column(Text)
    llm_analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="review_result")
