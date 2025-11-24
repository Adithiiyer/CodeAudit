from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Submission(Base):
    """Code submission model"""
    __tablename__ = 'submissions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    gcs_path = Column(String(500), nullable=False)
    status = Column(String(20), default='pending')  # pending, processing, completed, failed
    batch_id = Column(String(36), nullable=True, index=True)
    project_name = Column(String(255), nullable=True)
    user_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ReviewResult(Base):
    """Code review results model"""
    __tablename__ = 'review_results'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String(36), nullable=False, index=True)
    
    # Overall scores
    quality_score = Column(Float)
    security_score = Column(Float)
    maintainability_score = Column(Float)
    overall_score = Column(Float)
    
    # Detailed results (stored as JSON)
    static_analysis = Column(JSON)
    ai_review = Column(JSON)
    security_analysis = Column(JSON)
    refactoring_suggestions = Column(JSON)
    
    # Summary
    summary = Column(Text)
    issues_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    """Project model for organizing submissions"""
    __tablename__ = 'projects'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    user_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CodeMetricsHistory(Base):
    """Historical metrics for trend tracking"""
    __tablename__ = 'code_metrics_history'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True)
    submission_id = Column(String(36), nullable=False)
    
    # Snapshot of metrics at this point in time
    overall_score = Column(Float)
    quality_score = Column(Float)
    security_score = Column(Float)
    maintainability_score = Column(Float)
    total_issues = Column(Integer)
    total_files = Column(Integer)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class CustomRule(Base):
    """Custom code review rules"""
    __tablename__ = 'custom_rules'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    project_id = Column(String(36), nullable=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50))  # 'pattern', 'complexity', 'naming', 'security', 'forbidden'
    language = Column(String(50))  # 'python', 'javascript', 'java', 'all'
    
    # Rule configuration (stored as JSON for flexibility)
    config = Column(JSON)
    pattern = Column(String(500))  # Regex pattern or AST pattern
    severity = Column(String(20))  # 'error', 'warning', 'info'
    message = Column(Text)  # Custom message when rule is violated
    
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
