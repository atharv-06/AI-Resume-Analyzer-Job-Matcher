# app/routes/resume.py

import asyncio
import inspect
import logging
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, Depends
from pydantic import BaseModel, Field

from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.ai_engine import analyze_resume as analyze_resume_fn  # keep name distinct

router = APIRouter()
logger = logging.getLogger(__name__)


class ResumeAnalysisResponse(BaseModel):
    resume_preview: str = Field(..., description="First portion of extracted resume text")
    match_score: float = Field(..., description="Overall match score (0-100 or 0-1 depending on engine)")
    skills_detected: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    summary: Optional[str] = Field("", description="Short summary of candidate/resume")
    improvements: Optional[str] = Field("", description="Suggested improvements for resume")
    job_suggestions: List[str] = Field(default_factory=list, description="Suggested job titles/roles")


# config: adjust to your needs
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB


def _is_pdf_bytes(b: bytes) -> bool:
    """Quick check for PDF magic header."""
    return isinstance(b, (bytes, bytearray)) and b.startswith(b"%PDF")


async def _maybe_await(fn, *args, **kwargs):
    """Call fn and await it if it returns an awaitable/coroutine."""
    result = fn(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume_upload(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Accepts a PDF resume (file upload) and a job description (form field), extracts text,
    and returns an analysis. Validates PDF signature and size and gracefully handles errors.
    """

    # Basic content type check (sometimes client may not set content_type)
    content_type = (resume.content_type or "").lower()
    if "pdf" not in content_type and not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    # Read bytes (UploadFile.read consumes the stream)
    try:
        file_bytes = await resume.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to read uploaded file.")

    # Enforce upload size limit
    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file is too large. Max allowed size is {MAX_UPLOAD_SIZE // (1024*1024)} MB."
        )

    # Quick sanity check for PDF signature before parsing
    if not _is_pdf_bytes(file_bytes):
        # still try to parse — sometimes PDFs are wrapped / content-type is wrong; but warn to user
        logger.warning("Uploaded file does not start with PDF header; aborting extraction.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file does not appear to be a valid PDF."
        )

    # Extract text (wrap in try/except — parser may raise)
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except Exception as exc:
        logger.exception("PDF text extraction failed")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to extract text from PDF. Try uploading a text-based PDF."
        )

    if not resume_text or not resume_text.strip():
        # empty or unextractable
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to extract text from PDF. Try uploading a text-based PDF."
        )

    # Validate job_description minimal length (simple guard)
    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="job_description form field is required and cannot be empty."
        )

    # Call AI analyze function; be tolerant of both sync and async implementations
    try:
        result = await _maybe_await(analyze_resume_fn, resume_text, job_description)
    except Exception as exc:
        logger.exception("AI analysis failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Resume analysis failed.")

    # Normalize result to expected structure (defensive)
    if not isinstance(result, dict):
        logger.warning("analyze_resume returned non-dict result, coercing to dict")
        result = {} if result is None else {"score": 0, "summary": str(result)}

    score = result.get("score", 0)
    skills_detected = result.get("skills_detected", []) or []
    matched_skills = result.get("matched_skills", []) or []
    missing_skills = result.get("missing_skills", []) or []
    summary = result.get("summary", "") or ""
    improvements = result.get("improvements", "") or ""
    job_suggestions = result.get("job_suggestions", []) or []

    # Build a safe preview (limit to first N characters / avoid breaking unicode)
    preview_limit = 1000
    preview_text = resume_text[:preview_limit]
    if len(resume_text) > preview_limit:
        preview_text = preview_text.rstrip() + "…"

    response = {
        "resume_preview": preview_text,
        "match_score": float(score) if isinstance(score, (int, float)) else 0.0,
        "skills_detected": skills_detected,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "summary": summary,
        "improvements": improvements,
        "job_suggestions": job_suggestions,
    }

    return response
