from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import submissions

Base.metadata.create_all(engine)

app = FastAPI(title="CodeAudit — Local Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

app.include_router(submissions.router)
