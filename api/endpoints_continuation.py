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
