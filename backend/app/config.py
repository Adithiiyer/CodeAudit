import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR/'codeaudit.db'}")

STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
REPORT_DIR = STORAGE_DIR / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    print("✅ GROQ_API_KEY loaded")
else:
    print("❌ GROQ_API_KEY missing")
