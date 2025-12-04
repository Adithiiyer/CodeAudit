import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR/'codeaudit.db'}")

STORAGE_DIR = os.getenv("STORAGE_DIR", str(BASE_DIR / "storage"))

Path(STORAGE_DIR).mkdir(exist_ok=True)
Path(STORAGE_DIR + "/uploads").mkdir(parents=True, exist_ok=True)
Path(STORAGE_DIR + "/reports").mkdir(parents=True, exist_ok=True)
