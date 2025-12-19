# add near top of file
import difflib
import re
from typing import List, Dict, Any

# Define raw skill keywords for fuzzy matching
RAW_SKILL_KEYWORDS = [
    "python", "javascript", "java", "c++", "c#", "go", "rust", "typescript",
    "react", "angular", "vue", "node.js", "django", "flask", "spring",
    "sql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "ci/cd", "jenkins", "gitlab", "github", "devops",
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "rest api", "graphql", "microservices", "agile", "scrum"
]

# ---------------------------
# Extract skills using strict keyword matching
# ---------------------------
def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using strict keyword matching.
    Returns a list of normalized skills found in the text.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found = set()
    
    for keyword in RAW_SKILL_KEYWORDS:
        if keyword.lower() in text_lower:
            found.add(_normalize_skill(keyword))
    
    return sorted(found)


# ---------------------------
# Normalize skill names
# ---------------------------
def _normalize_skill(skill: str) -> str:
    """
    Normalize skill names to a consistent format.
    Removes extra whitespace and converts to title case.
    """
    return skill.strip().title()


# ---------------------------
# Fuzzy fallback skill extraction
# ---------------------------
def extract_skills_fuzzy(text: str, max_ngram: int = 3, cutoff: float = 0.78) -> List[str]:
    """
    Try to find approximate matches of RAW_SKILL_KEYWORDS inside `text`.
    Builds n-grams (1..max_ngram) from the text and checks close matches
    to raw keywords using difflib.get_close_matches.
    Returns normalized skill tokens.
    """
    if not text:
        return []

    text_l = re.sub(r"[^\w\s\+\#\-\.]", " ", text.lower())  # keep + # . - for things like c++ node.js
    tokens = text_l.split()
    ngrams = set()

    # build n-grams up to max_ngram
    for n in range(1, max_ngram + 1):
        for i in range(len(tokens) - n + 1):
            ng = " ".join(tokens[i:i + n])
            ngrams.add(ng.strip())

    # candidate pool: use RAW_SKILL_KEYWORDS raw forms
    pool = [rk.lower() for rk in RAW_SKILL_KEYWORDS]

    found = set()
    for ng in ngrams:
        # exact quick check first
        if ng in pool:
            found.add(_normalize_skill(ng))
            continue
        # fuzzy check
        matches = difflib.get_close_matches(ng, pool, n=1, cutoff=cutoff)
        if matches:
            found.add(_normalize_skill(matches[0]))

    return sorted(found)


# ---------------------------
# Replace analyze_resume with this improved version
# ---------------------------
def analyze_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Improved analyze_resume:
      - strict local extraction (exact)
      - AI extraction (validated against text)
      - fallback: fuzzy extraction for JD if strict detection yields nothing
      - compute score as percent of JD skills present in resume
    """
    # 1) Strict local keyword extraction
    resume_skills_local = extract_skills(resume_text)
    jd_skills_local = extract_skills(job_description)

    # 2) AI extraction + validation (as in your existing code)
    ai = get_groq_analysis(resume_text, job_description)
    ai_resume_valid = _filter_ai_skills_by_text(ai.get("resume_skills_ai", []), resume_text)
    ai_jd_valid = _filter_ai_skills_by_text(ai.get("jd_skills_ai", []), job_description)

    # 3) Combine strict results
    resume_combined = sorted(set(resume_skills_local) | set(ai_resume_valid))
    jd_combined = sorted(set(jd_skills_local) | set(ai_jd_valid))

    # 4) If JD yielded no skills at all, try fuzzy extraction as a fallback
    if not jd_combined:
        jd_fuzzy = extract_skills_fuzzy(job_description, max_ngram=3, cutoff=0.78)
        # use fuzzy only if it returns something
        if jd_fuzzy:
            jd_combined = sorted(set(jd_fuzzy) | set(ai_jd_valid))  # still keep validated AI JD skills

    # 5) Matched / missing (strict intersection)
    matched = sorted(set(resume_combined) & set(jd_combined))
    missing = sorted(set(jd_combined) - set(resume_combined))

    # 6) Score calculation
    if jd_combined:
        score = int((len(matched) / len(jd_combined)) * 100)
    else:
        # no detectable JD skills even after fallback -> score 0 (no basis)
        score = 0

    job_suggestions = suggest_jobs(resume_combined)

    return {
        "score": score,
        "skills_detected": resume_combined,
        "matched_skills": matched,
        "missing_skills": missing,
        "summary": ai.get("summary", ""),
        "improvements": ai.get("improvements", ""),
        "job_suggestions": job_suggestions
    }
