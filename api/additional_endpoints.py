# Additional API endpoints - append to api/main.py

# ==================== PROJECT & TRENDS ENDPOINTS ====================

@app.post("/api/v1/projects")
async def create_project(project: ProjectCreate, db: SessionLocal = Depends(get_db)):
    """Create a new project for tracking"""
    new_project = Project(
        name=project.name,
        description=project.description
    )
    
    db.add(new_project)
    try:
        db.commit()
        db.refresh(new_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Project creation failed: {str(e)}")
    
    return {
        "project_id": new_project.id,
        "name": new_project.name,
        "message": "Project created successfully"
    }

@app.get("/api/v1/projects/{project_id}/trends")
async def get_project_trends(
    project_id: str,
    days: int = 30,
    db: SessionLocal = Depends(get_db)
):
    """Get code quality trends for a project over time"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    metrics = db.query(CodeMetricsHistory).filter(
        CodeMetricsHistory.project_id == project_id,
        CodeMetricsHistory.recorded_at >= cutoff_date
    ).order_by(CodeMetricsHistory.recorded_at.asc()).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this project")
    
    # Format data for charting
    trend_data = [
        {
            "date": m.recorded_at.strftime("%Y-%m-%d"),
            "overall_score": m.overall_score,
            "quality_score": m.quality_score,
            "security_score": m.security_score,
            "maintainability_score": m.maintainability_score,
            "total_issues": m.total_issues
        }
        for m in metrics
    ]
    
    # Calculate trend
    if len(metrics) >= 2:
        first_score = metrics[0].overall_score
        last_score = metrics[-1].overall_score
        change = last_score - first_score
        
        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
        change = 0
    
    return {
        "project_id": project_id,
        "period_days": days,
        "trend": trend,
        "data_points": len(trend_data),
        "current_score": metrics[-1].overall_score if metrics else None,
        "score_change": round(change, 2) if len(metrics) >= 2 else 0,
        "trends": trend_data
    }

@app.post("/api/v1/projects/{project_id}/record-metrics")
async def record_project_metrics(
    project_id: str,
    submission_id: str,
    db: SessionLocal = Depends(get_db)
):
    """Record current metrics snapshot for a project"""
    result = db.query(ReviewResult).filter(
        ReviewResult.submission_id == submission_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Submission result not found")
    
    metrics_snapshot = CodeMetricsHistory(
        project_id=project_id,
        submission_id=submission_id,
        overall_score=result.overall_score,
        quality_score=result.quality_score,
        security_score=result.security_score,
        maintainability_score=result.maintainability_score,
        total_issues=result.issues_count,
        total_files=1
    )
    
    db.add(metrics_snapshot)
    db.commit()
    
    return {"message": "Metrics recorded successfully"}

# ==================== CUSTOM RULES ENDPOINTS ====================

@app.post("/api/v1/rules")
async def create_custom_rule(rule: CustomRuleCreate, db: SessionLocal = Depends(get_db)):
    """Create a custom review rule"""
    new_rule = CustomRule(
        user_id=rule.user_id,
        project_id=rule.project_id,
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        language=rule.language,
        pattern=rule.pattern,
        severity=rule.severity,
        message=rule.message
    )
    
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    return {
        "rule_id": new_rule.id,
        "message": "Custom rule created successfully"
    }

@app.get("/api/v1/rules")
async def get_custom_rules(
    user_id: str,
    project_id: Optional[str] = None,
    db: SessionLocal = Depends(get_db)
):
    """Get all custom rules for a user/project"""
    query = db.query(CustomRule).filter(CustomRule.user_id == user_id)
    
    if project_id:
        query = query.filter(CustomRule.project_id == project_id)
    
    rules = query.all()
    
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "rule_type": r.rule_type,
                "language": r.language,
                "pattern": r.pattern,
                "severity": r.severity,
                "enabled": r.enabled
            }
            for r in rules
        ]
    }

@app.put("/api/v1/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, db: SessionLocal = Depends(get_db)):
    """Enable/disable a custom rule"""
    rule = db.query(CustomRule).filter(CustomRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.enabled = not rule.enabled
    db.commit()
    
    return {
        "rule_id": rule_id,
        "enabled": rule.enabled,
        "message": f"Rule {'enabled' if rule.enabled else 'disabled'}"
    }

@app.delete("/api/v1/rules/{rule_id}")
async def delete_rule(rule_id: str, db: SessionLocal = Depends(get_db)):
    """Delete a custom rule"""
    rule = db.query(CustomRule).filter(CustomRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Rule deleted successfully"}

# ==================== CHAT ENDPOINTS ====================

@app.post("/api/v1/chat/start")
async def start_chat_session(submission_id: str, db: SessionLocal = Depends(get_db)):
    """Start a new chat session about a code review"""
    # Get submission and results
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()
    
    result = db.query(ReviewResult).filter(
        ReviewResult.submission_id == submission_id
    ).first()
    
    if not submission or not result:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Download code from GCS/local storage
    try:
        if submission.gcs_path.startswith("gs://"):
            path_parts = submission.gcs_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_path = path_parts[1]
            
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            code = blob.download_as_text()
        elif submission.gcs_path.startswith("file://"):
            local_path = submission.gcs_path.replace("file://", "")
            with open(local_path, 'r') as f:
                code = f.read()
        else:
            # Assume local path
            with open(submission.gcs_path, 'r') as f:
                code = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading code: {str(e)}")
    
    # Create chat agent
    chat_agent = FeedbackChatAgent()
    session_id = str(uuid.uuid4())
    
    # Store session
    chat_sessions[session_id] = {
        "agent": chat_agent,
        "code": code,
        "results": {
            "overall_score": result.overall_score,
            "quality_score": result.quality_score,
            "security_score": result.security_score,
            "ai_review": result.ai_review,
            "security_analysis": result.security_analysis
        }
    }
    
    return {
        "session_id": session_id,
        "submission_id": submission_id,
        "message": "Chat session started. Ask questions about your code review!"
    }

@app.post("/api/v1/chat/{session_id}/message")
async def send_chat_message(session_id: str, message: str):
    """Send a message in a chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session = chat_sessions[session_id]
    agent = session["agent"]
    
    # Get response from agent
    response = agent.chat(
        user_question=message,
        code=session["code"],
        review_results=session["results"]
    )
    
    return {
        "session_id": session_id,
        "user_message": message,
        "assistant_response": response
    }

@app.get("/api/v1/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session = chat_sessions[session_id]
    agent = session["agent"]
    
    return {
        "session_id": session_id,
        "history": agent.conversation_history
    }

@app.delete("/api/v1/chat/{session_id}")
async def end_chat_session(session_id: str):
    """End a chat session"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return {"message": "Chat session ended"}
