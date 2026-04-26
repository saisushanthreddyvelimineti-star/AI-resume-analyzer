import math
import re
import shutil
import zipfile
from collections import Counter
from importlib.util import find_spec
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import fitz


SECTION_ALIASES = {
    "summary": {"summary", "profile", "professional summary", "about"},
    "skills": {"skills", "technical skills", "core skills", "competencies"},
    "experience": {"experience", "work experience", "employment", "professional experience"},
    "projects": {"projects", "project experience", "academic projects"},
    "education": {"education", "academics", "academic background"},
    "certifications": {"certifications", "licenses", "courses"},
}

PROFILE_SKILL_HINTS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "fastapi",
    "sql",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "opencv",
    "pytorch",
    "tensorflow",
    "azure",
    "aws",
    "docker",
    "git",
]


def _optional_import(module_name: str):
    try:
        module = __import__(module_name)
        return module
    except Exception:
        return None


def has_ocr_support() -> bool:
    return (
        find_spec("PIL") is not None
        and find_spec("pytesseract") is not None
        and _resolve_tesseract_cmd() is not None
    )


def has_embedding_support() -> bool:
    return find_spec("sentence_transformers") is not None


def extract_text_from_document(file_bytes: bytes, filename: str, content_type: str | None = None) -> dict[str, Any]:
    lowered_name = (filename or "").lower()
    lowered_type = (content_type or "").lower()

    if lowered_name.endswith(".pdf") or "pdf" in lowered_type:
        return _extract_text_from_pdf_bytes(file_bytes)

    if lowered_name.endswith(".docx") or "wordprocessingml.document" in lowered_type:
        return _extract_text_from_docx_bytes(file_bytes)

    if any(lowered_name.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]) or lowered_type.startswith("image/"):
        return _extract_text_from_image_bytes(file_bytes)

    raise ValueError("Unsupported file type. Use PDF, DOCX, or image formats such as PNG/JPG.")


def _extract_text_from_pdf_bytes(file_bytes: bytes) -> dict[str, Any]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    page_text = []
    for page in doc:
        text = page.get_text().strip()
        page_text.append(text)

    combined = "\n".join(chunk for chunk in page_text if chunk).strip()
    mode = "pdf-text"

    if combined:
        return {"text": combined, "mode": mode, "pages": len(doc)}

    if has_ocr_support():
        ocr_pages = []
        for page in doc:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            ocr_pages.append(_ocr_image_bytes(pixmap.tobytes("png")))
        combined = "\n".join(chunk for chunk in ocr_pages if chunk).strip()
        mode = "pdf-ocr"

    return {"text": combined, "mode": mode, "pages": len(doc)}


def _extract_text_from_image_bytes(file_bytes: bytes) -> dict[str, Any]:
    if has_ocr_support():
        return {"text": _ocr_image_bytes(file_bytes), "mode": "image-ocr", "pages": 1}
    return {"text": "", "mode": "image-no-ocr", "pages": 1}


def _extract_text_from_docx_bytes(file_bytes: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(BytesIO(file_bytes)) as archive:
            xml_bytes = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml_bytes)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs = []
        for paragraph in root.findall(".//w:p", namespace):
            texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
            if texts:
                paragraphs.append("".join(texts))
        combined = "\n".join(paragraphs).strip()
        return {"text": combined, "mode": "docx-text", "pages": 1}
    except Exception as exc:
        raise ValueError(f"DOCX parsing failed: {exc}") from exc


def _ocr_image_bytes(file_bytes: bytes) -> str:
    pil_module = _optional_import("PIL")
    pytesseract = _optional_import("pytesseract")
    if pil_module is None or pytesseract is None:
        return ""

    tesseract_cmd = _resolve_tesseract_cmd()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    image = pil_module.Image.open(BytesIO(file_bytes))
    return pytesseract.image_to_string(image)


def _resolve_tesseract_cmd() -> str | None:
    binary = shutil.which("tesseract")
    if binary:
        return binary

    common_paths = [
        Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
        Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
    ]
    for path in common_paths:
        if path.exists():
            return str(path)

    return None


def parse_document_layout(text: str) -> dict[str, list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return {key: [] for key in SECTION_ALIASES}

    sections = {key: [] for key in SECTION_ALIASES}
    current_section = "summary"

    for line in lines:
        normalized = _normalize_heading(line)
        matched = next((name for name, aliases in SECTION_ALIASES.items() if normalized in aliases), None)
        if matched:
            current_section = matched
            continue
        sections[current_section].append(line)

    return sections


def build_structured_profile(text: str, sections: dict[str, list[str]]) -> dict[str, Any]:
    compact_text = re.sub(r"\s+", " ", text).strip()
    lower_text = compact_text.lower()
    skills = []
    for skill in PROFILE_SKILL_HINTS:
        if skill in lower_text:
            skills.append(skill.title() if skill.islower() else skill)

    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", compact_text)
    phone_match = re.search(r"(\+?\d[\d\s\-]{8,}\d)", compact_text)
    linkedin_match = re.search(r"(https?://(?:www\.)?linkedin\.com/[^\s]+)", compact_text, re.IGNORECASE)
    github_match = re.search(r"(https?://(?:www\.)?github\.com/[^\s]+)", compact_text, re.IGNORECASE)

    return {
        "headline": _best_headline(sections),
        "summary": " ".join(sections.get("summary", [])[:4]).strip(),
        "skills": skills[:12],
        "experience": sections.get("experience", [])[:8],
        "projects": sections.get("projects", [])[:6],
        "education": sections.get("education", [])[:4],
        "certifications": sections.get("certifications", [])[:4],
        "contact": {
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "linkedin": linkedin_match.group(0) if linkedin_match else "",
            "github": github_match.group(0) if github_match else "",
        },
    }


def _best_headline(sections: dict[str, list[str]]) -> str:
    for key in ["summary", "experience", "projects"]:
        values = sections.get(key, [])
        if values:
            return values[0]
    return ""


def _normalize_heading(line: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", line).strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def match_jobs_with_resume(resume_text: str, job_descriptions: list[dict[str, str]]) -> dict[str, Any]:
    if has_embedding_support():
        try:
            return _semantic_match_jobs(resume_text, job_descriptions)
        except Exception:
            pass
    return _token_match_jobs(resume_text, job_descriptions)


def _semantic_match_jobs(resume_text: str, job_descriptions: list[dict[str, str]]) -> dict[str, Any]:
    sentence_transformers = _optional_import("sentence_transformers")
    model = sentence_transformers.SentenceTransformer("all-MiniLM-L6-v2")
    resume_vector = model.encode(resume_text)
    scored_jobs = []

    for job in job_descriptions:
        combined = " ".join(filter(None, [job.get("title", ""), job.get("company", ""), job.get("description", "")]))
        job_vector = model.encode(combined)
        score = _cosine_from_vectors(resume_vector, job_vector)
        scored_jobs.append(_job_score_payload(job, score))

    ranked = sorted(scored_jobs, key=lambda item: item["score"], reverse=True)
    return {"mode": "semantic-embedding", "matches": ranked}


def _token_match_jobs(resume_text: str, job_descriptions: list[dict[str, str]]) -> dict[str, Any]:
    resume_tokens = _token_counter(resume_text)
    scored_jobs = []

    for job in job_descriptions:
        combined = " ".join(filter(None, [job.get("title", ""), job.get("company", ""), job.get("description", "")]))
        job_tokens = _token_counter(combined)
        score = _cosine_from_counters(resume_tokens, job_tokens)
        shared = sorted(set(resume_tokens) & set(job_tokens))
        scored_jobs.append(_job_score_payload(job, score, shared_keywords=shared[:8]))

    ranked = sorted(scored_jobs, key=lambda item: item["score"], reverse=True)
    return {"mode": "token-fallback", "matches": ranked}


def _job_score_payload(job: dict[str, str], score: float, shared_keywords: list[str] | None = None) -> dict[str, Any]:
    return {
        "title": job.get("title", "Untitled role"),
        "company": job.get("company", ""),
        "description": job.get("description", ""),
        "score": round(score * 100, 2),
        "shared_keywords": shared_keywords or [],
    }


def _token_counter(text: str) -> Counter:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{1,}", text.lower())
    filtered = [token for token in tokens if token not in {"with", "from", "that", "this", "have", "will", "your"}]
    return Counter(filtered)


def _cosine_from_counters(left: Counter, right: Counter) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_mag = math.sqrt(sum(value * value for value in left.values()))
    right_mag = math.sqrt(sum(value * value for value in right.values()))
    if not left_mag or not right_mag:
        return 0.0
    return numerator / (left_mag * right_mag)


def _cosine_from_vectors(left: Any, right: Any) -> float:
    numerator = float(sum(a * b for a, b in zip(left, right)))
    left_mag = math.sqrt(float(sum(a * a for a in left)))
    right_mag = math.sqrt(float(sum(b * b for b in right)))
    if not left_mag or not right_mag:
        return 0.0
    return numerator / (left_mag * right_mag)
