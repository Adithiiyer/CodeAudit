from fastapi import FastAPI
from app.database import Base, engine
from app.routers import submissions
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.DEBUG)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeAudit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions.router)
