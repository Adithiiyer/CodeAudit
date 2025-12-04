from pathlib import Path
from ..config import STORAGE_DIR

def save_upload(file, filename):
    folder = Path(STORAGE_DIR) / "uploads"
    folder.mkdir(exist_ok=True)
    path = folder / filename
    with open(path, "wb") as f:
        f.write(file.file.read())
    return str(path)

def write_report(submission_id: int, content: str):
    folder = Path(STORAGE_DIR) / "reports"
    folder.mkdir(exist_ok=True)
    path = folder / f"submission_{submission_id}.txt"
    path.write_text(content)
    return str(path)
