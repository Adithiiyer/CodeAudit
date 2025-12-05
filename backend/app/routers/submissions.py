from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Submission, ReviewResult
from app.schemas import SubmissionOut
from app.services.storage import save_upload
from app.services.analyzer import analyze_file

router = APIRouter(prefix="/submissions", tags=["Submissions"])


def detect_lang(filename):
    ext = filename.split(".")[-1]
    return {
        "py": "python",
        "js": "javascript",
        "ts": "javascript",
        "java": "java",
        "cpp": "cpp",
        "c": "c",
        "go": "go"
    }.get(ext, "unknown")


@router.post("/", response_model=SubmissionOut)
async def upload_single(background: BackgroundTasks,
                        file: UploadFile = File(...),
                        db: Session = Depends(get_db)):

    path = save_upload(file, file.filename)
    lang = detect_lang(file.filename)

    submission = Submission(
        filename=file.filename,
        storage_path=path,
        language=lang,
        status="processing"
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    background.add_task(process_submission, submission.id, path, lang)

    return submission


def process_submission(id: int, path: str, lang: str):
    db = SessionLocal()

    submission = db.get(Submission, id)

    score, summary, issues, llm_json = analyze_file(id, path, lang)

    result = ReviewResult(
        submission_id=id,
        score=score,
        summary=summary,
        issues=issues,
        llm_analysis=str(llm_json)
    )

    db.add(result)
    submission.status = "completed"

    db.commit()
    db.close()


@router.get("/", response_model=list[SubmissionOut])
def list_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()


@router.get("/{id}", response_model=SubmissionOut)
def get_submission(id: int, db: Session = Depends(get_db)):
    return db.get(Submission, id)
