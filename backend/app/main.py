from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.routes.resume import router as resume_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Analyzer & Job Matcher")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])
