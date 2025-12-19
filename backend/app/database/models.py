from sqlalchemy import Column, Integer, String
from app.database.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    resume_text = Column(String)
    job_description = Column(String)
    match_score = Column(Integer)
    skills = Column(String)  # comma-separated skills or JSON string
