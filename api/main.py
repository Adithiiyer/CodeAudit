import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from database.connection import SessionLocal, get_db, create_tables
from database.models import Submission, ReviewResult, Project, CodeMetricsHistory, CustomRule
from api.storage import get_storage_client
from api.pubsub import get_pubsub_client
from agents.chat_agent import FeedbackChatAgent

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CodeAudit API",
    description="AI-Powered Code Review Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
storage_client = get_storage_client()
pubsub_client = get_pubsub_client()

# Chat sessions storage (in production, use Redis)
chat_sessions = {}

# Pydantic models
class SubmissionResponse(BaseModel):
    submission_id: str
    status: str
    message: str
    gcs_url: Optional[str] = None

class BatchSubmissionResponse(BaseModel):
    batch_id: str
    project_name: str
    total_files: int
    submission_ids: List[str]
    status: str
    message: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CustomRuleCreate(BaseModel):
    name: str
    description: str
    rule_type: str
    language: str
    pattern: str
    severity: str
    message: str
    user_id: str
    project_id: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        create_tables()
        print("✓ Database initialized")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

# Health check
@app.get("/")
async def root():
    return {
        "message": "CodeAudit API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Helper functions
def detect_language(extension: str) -> str:
    """Detect programming language from file extension"""
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rb': 'ruby',
        '.php': 'php'
    }
    return language_map.get(extension.lower(), 'unknown')

# ==================== SUBMISSION ENDPOINTS ====================

@app.post("/api/v1/submit", response_model=SubmissionResponse)
async def submit_code(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    user_id: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """
    Submit a single code file for review
    """
    # Generate unique submission ID
    submission_id = str(uuid.uuid4())
    
    # Validate file type
    allowed_extensions = {'.py', '.js', '.java', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.go'}
    file_ext = '.' + file.filename.split('.')[-1] if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # Detect language
    if not language:
        language = detect_language(file_ext)
    
    # Upload to GCS
    file_path = f"submissions/{submission_id}/{file.filename}"
    gcs_url = storage_client.upload_file(file.file, file_path)
    
    # Save to database
    submission = Submission(
        id=submission_id,
        filename=file.filename,
        language=language,
        gcs_path=gcs_url,
        status='pending',
        user_id=user_id
    )
    
    db.add(submission)
    db.commit()
    
    # Publish to Pub/Sub
    pubsub_client.publish_job(submission_id, file_path, language)
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message="Code submitted successfully",
        gcs_url=gcs_url
    )

@app.post("/api/v1/submit-batch", response_model=BatchSubmissionResponse)
async def submit_batch(
    file: UploadFile = File(...),
    project_name: Optional[str] = None,
    user_id: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """
    Upload a zip file containing multiple code files for batch review
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")
    
    batch_id = str(uuid.uuid4())
    project_name = project_name or f"batch_{batch_id[:8]}"
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded zip
        zip_path = Path(temp_dir) / file.filename
        with open(zip_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find all code files
        code_files = []
        supported_extensions = {'.py', '.js', '.java', '.ts', '.jsx', '.tsx', '.cpp', '.c', '.go'}
        
        for ext in supported_extensions:
            code_files.extend(Path(temp_dir).rglob(f'*{ext}'))
        
        if not code_files:
            raise HTTPException(
                status_code=400, 
                detail="No supported code files found in zip"
            )
        
        # Process each file
        submission_ids = []
        for code_file in code_files:
            submission_id = str(uuid.uuid4())
            
            # Determine relative path within project
            relative_path = code_file.relative_to(temp_dir)
            
            # Upload to GCS
            gcs_path = f"batches/{batch_id}/{relative_path}"
            with open(code_file, 'rb') as f:
                storage_client.upload_file(f, gcs_path)
            
            # Detect language
            language = detect_language(code_file.suffix)
            
            # Save to database
            submission = Submission(
                id=submission_id,
                filename=str(relative_path),
                language=language,
                gcs_path=f"gs://{storage_client.bucket_name}/{gcs_path}",
                batch_id=batch_id,
                project_name=project_name,
                status='pending',
                user_id=user_id
            )
            db.add(submission)
            
            # Publish to Pub/Sub
            pubsub_client.publish_job(submission_id, gcs_path, language)
            
            submission_ids.append(submission_id)
        
        db.commit()
    
    return BatchSubmissionResponse(
        batch_id=batch_id,
        project_name=project_name,
        total_files=len(submission_ids),
        submission_ids=submission_ids,
        status="processing",
        message=f"Batch of {len(submission_ids)} files submitted successfully"
    )

# Continue in next file due to length...
# Additional endpoints for api/main.py
# Add these to the main.py file after the batch submission endpoint

# ==================== RESULTS ENDPOINTS ====================

@app.get("/api/v1/results/{submission_id}")
async def get_submission_results(submission_id: str, db: SessionLocal = Depends(get_db)):
    """
    Get detailed results for a submission
    """
    result = db.query(ReviewResult).filter(
        ReviewResult.submission_id == submission_id
    ).first()
    
    if not result:
        # Check if submission exists but not yet processed
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if submission:
            return {
                "submission_id": submission_id,
                "status": submission.status,
                "message": "Review in progress" if submission.status == "processing" else "Not yet reviewed"
            }
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return {
        "submission_id": submission_id,
        "overall_score": result.overall_score,
        "quality_score": result.quality_score,
        "security_score": result.security_score,
        "maintainability_score": result.maintainability_score,
        "issues_count": result.issues_count,
        "ai_review": result.ai_review,
        "security_analysis": result.security_analysis,
        "static_analysis": result.static_analysis,
        "refactoring_suggestions": result.refactoring_suggestions,
        "summary": result.summary,
        "created_at": result.created_at.isoformat() if result.created_at else None
    }

@app.get("/api/v1/batch/{batch_id}/status")
async def get_batch_status(batch_id: str, db: SessionLocal = Depends(get_db)):
    """
    Get status of all files in a batch
    """
    submissions = db.query(Submission).filter(
        Submission.batch_id == batch_id
    ).all()
    
    if not submissions:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    total = len(submissions)
    completed = sum(1 for s in submissions if s.status == 'completed')
    failed = sum(1 for s in submissions if s.status == 'failed')
    processing = sum(1 for s in submissions if s.status == 'processing')
    
    # Get average scores for completed files
    completed_submissions = [s for s in submissions if s.status == 'completed']
    avg_score = None
    if completed_submissions:
        results = db.query(ReviewResult).filter(
            ReviewResult.submission_id.in_([s.id for s in completed_submissions])
        ).all()
        
        if results:
            avg_score = sum(r.overall_score for r in results) / len(results)
    
    return {
        "batch_id": batch_id,
        "project_name": submissions[0].project_name,
        "total_files": total,
        "completed": completed,
        "processing": processing,
        "failed": failed,
        "progress_percentage": (completed / total) * 100,
        "average_score": round(avg_score, 2) if avg_score else None,
        "files": [
            {
                "filename": s.filename,
                "status": s.status,
                "submission_id": s.id
            }
            for s in submissions
        ]
    }

@app.get("/api/v1/batch/{batch_id}/report")
async def get_batch_report(batch_id: str, db: SessionLocal = Depends(get_db)):
    """
    Generate comprehensive batch report with aggregated metrics
    """
    submissions = db.query(Submission).filter(
        Submission.batch_id == batch_id
    ).all()
    
    if not submissions:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Get all results
    submission_ids = [s.id for s in submissions]
    results = db.query(ReviewResult).filter(
        ReviewResult.submission_id.in_(submission_ids)
    ).all()
    
    if not results:
        return {
            "batch_id": batch_id,
            "project_name": submissions[0].project_name,
            "summary": {"message": "No reviews completed yet"}
        }
    
    # Aggregate metrics
    total_issues = sum(r.issues_count for r in results)
    avg_quality = sum(r.quality_score for r in results) / len(results)
    avg_security = sum(r.security_score for r in results) / len(results)
    avg_maintainability = sum(r.maintainability_score for r in results) / len(results)
    
    # Group by language
    language_stats = {}
    for submission in submissions:
        lang = submission.language
        if lang not in language_stats:
            language_stats[lang] = {"count": 0, "avg_score": 0}
        
        result = next((r for r in results if r.submission_id == submission.id), None)
        if result:
            language_stats[lang]["count"] += 1
            language_stats[lang]["avg_score"] += result.overall_score
    
    # Calculate averages
    for lang in language_stats:
        if language_stats[lang]["count"] > 0:
            language_stats[lang]["avg_score"] /= language_stats[lang]["count"]
            language_stats[lang]["avg_score"] = round(language_stats[lang]["avg_score"], 2)
    
    # Find files with most issues
    top_issues = sorted(results, key=lambda r: r.issues_count, reverse=True)[:5]
    
    return {
        "batch_id": batch_id,
        "project_name": submissions[0].project_name,
        "summary": {
            "total_files": len(submissions),
            "total_issues": total_issues,
            "average_quality_score": round(avg_quality, 2),
            "average_security_score": round(avg_security, 2),
            "average_maintainability": round(avg_maintainability, 2)
        },
        "language_breakdown": language_stats,
        "files_needing_attention": [
            {
                "filename": next(s.filename for s in submissions if s.id == r.submission_id),
                "issues_count": r.issues_count,
                "overall_score": r.overall_score
            }
            for r in top_issues
        ]
    }

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(
    user_id: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """
    Get dashboard statistics
    """
    # Build query
    query = db.query(Submission)
    if user_id:
        query = query.filter(Submission.user_id == user_id)
    
    total_submissions = query.count()
    
    # Get completed submissions
    completed = query.filter(Submission.status == 'completed').all()
    
    # Get all results
    if user_id:
        results = db.query(ReviewResult).join(Submission).filter(
            Submission.user_id == user_id
        ).all()
    else:
        results = db.query(ReviewResult).all()
    
    # Calculate averages
    avg_score = sum(r.overall_score for r in results) / len(results) if results else 0
    total_issues = sum(r.issues_count for r in results)
    
    # Get recent submissions
    recent_query = db.query(Submission)
    if user_id:
        recent_query = recent_query.filter(Submission.user_id == user_id)
    
    recent_submissions = recent_query.order_by(
        Submission.created_at.desc()
    ).limit(10).all()
    
    return {
        "stats": {
            "totalSubmissions": total_submissions,
            "averageScore": round(avg_score, 2),
            "totalIssues": total_issues
        },
        "recent_submissions": [
            {
                "id": s.id,
                "filename": s.filename,
                "language": s.language,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in recent_submissions
        ]
    }

# Add remaining endpoints in next sections...
