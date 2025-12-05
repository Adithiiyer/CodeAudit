import shutil
from pathlib import Path
from app.config import UPLOAD_DIR, REPORT_DIR

def save_upload(file, filename):
    path = UPLOAD_DIR / filename
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return str(path)

def write_report(submission_id: int, content: str):
    report_path = REPORT_DIR / f"{submission_id}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(report_path)
