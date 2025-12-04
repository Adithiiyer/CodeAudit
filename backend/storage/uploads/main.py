from api.storage import get_storage_client

storage_client = get_storage_client()

@app.post("/api/v1/submit", response_model=SubmissionResponse)
async def submit_code(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    submission_id = str(uuid.uuid4())
    
    # Upload to GCS
    file_path = f"submissions/{submission_id}/{file.filename}"
    gcs_url = storage_client.upload_file(file.file, file_path)
    
    return SubmissionResponse(
        submission_id=submission_id,
        status="pending",
        message="Code submitted successfully",
        gcs_url=gcs_url
    )