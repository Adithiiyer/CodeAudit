from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Optional

app = FastAPI(title="CodeAudit API", version="1.0.0")

# Enable CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubmissionResponse(BaseModel):
    submission_id: str
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "CodeAudit API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/submit", response_model=SubmissionResponse)
async def submit_code(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    """
    Upload a code file for review
    """
    # Generate unique submission ID
    submission_id = str(uuid.uuid4())
    
    # Validate file type
    allowed_extensions = {'.py', '.js', '.java', '.ts', '.jsx', '.tsx'}
    file_ext = '.' + file.filename.split('.')[-1] if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # TODO: Upload to GCS
    # TODO: Publish to Pub/Sub
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message="Code submitted successfully"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)