import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import time
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

from src.agentic_ai import derive_target_profile as derive_agentic_target_profile, run_agentic_career_workflow
from src.ats_ai import ats_report_to_csv, build_ats_report
from src.course_recommender import recommend_youtube_courses
from src.helper import (
    ask_interview_coach,
    ask_openai,
    extract_text_from_pdf,
    fallback_interview_reply,
    generate_resume_insights,
    has_openai_config,
    suggest_job_keywords,
    synthesize_speech,
    transcribe_audio,
)
from src.interview_ai import (
    build_interview_feedback_report,
    build_interview_profile,
    evaluate_interview_presence,
    score_interview_answer,
)
from src.local_voice_stack import local_voice_stack_status
from src.multimodal_ai import (
    build_structured_profile,
    extract_text_from_document,
    has_embedding_support,
    has_ocr_support,
    match_jobs_with_resume,
    parse_document_layout,
)
from src.job_api import fetch_indeed_jobs, fetch_linkedin_jobs, generate_demo_jobs, has_apify_config
from src.resume_builder_ai import build_resume_builder_report


app = FastAPI(title="Jarvis Career Studio API")
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobRequest(BaseModel):
    summary: str
    location: str = "United Kingdom"


class AtsScoreRequest(BaseModel):
    resume_summary: str = ""
    resume_text: str = ""
    job_description: str
    target_role: str = ""


class ResumeBuilderRequest(BaseModel):
    resume_summary: str = ""
    resume_text: str = ""
    job_description: str = ""
    target_role: str = ""
    candidate_name: str = ""


class ChatTurn(BaseModel):
    role: str
    content: str


class JarvisRequest(BaseModel):
    summary: str
    prompt: str
    conversation: list[ChatTurn] = []


class AgenticRequest(BaseModel):
    summary: str
    resume_text: str = ""
    location: str = "United Kingdom"
    prompt: str = ""
    target_role: str = ""
    job_description: str = ""
    conversation: list[ChatTurn] = []


class CourseRecommendationRequest(BaseModel):
    missing_skills: list[str]
    target_job_title: str = ""
    per_skill: int = 3


class InterviewFeedbackRequest(BaseModel):
    role: str = "General Interview"
    transcript: str = ""
    duration_seconds: float = 0.0
    face_visible_ratio: float = 0.0
    attentive_ratio: float = 0.0
    average_attention_score: float = 0.0
    distraction_events: int = 0
    absence_events: int = 0
    longest_absence_seconds: float = 0.0
    longest_distraction_seconds: float = 0.0
    timeline: list[dict[str, Any]] = []


class InterviewProfileRequest(BaseModel):
    resume_summary: str = ""
    resume_text: str = ""
    target_role: str = "Software Engineer"
    job_description: str = ""
    difficulty: str = "Medium"
    interviewer_style: str = "Balanced"


class InterviewScoreRequest(BaseModel):
    interview_profile: dict[str, Any] = {}
    question: str = ""
    answer: str = ""


class InterviewPresenceRequest(BaseModel):
    session_id: str = "local-session"
    question_id: str = ""
    answer_id: str = ""
    frame_window_start: float = 0.0
    frame_window_end: float = 0.0
    face_detected: bool = True
    face_centered_score: float = 0.7
    face_visibility_score: float = 0.7
    eye_contact_score: float = 0.7
    gaze_away_frequency: float = 0.25
    blink_rate_score: float = 0.7
    head_stability_score: float = 0.7
    posture_score: float = 0.7
    shoulder_tension_score: float = 0.7
    fidget_score: float = 0.7
    expression_consistency_score: float = 0.7
    smile_naturalness_score: float = 0.65
    attention_score: float = 0.7
    stress_signal_score: float = 0.35
    calmness_signal_score: float = 0.65
    dominant_emotion: str = "neutral"
    emotion_distribution: dict[str, float] = {}
    recovery_after_hesitation_score: float = 0.6
    speaking_alignment_score: float = 0.65
    pacing_support_signal: str = ""
    notable_events: list[str] = []


class DuixSpeakRequest(BaseModel):
    text: str


class VisualJobMatch(BaseModel):
    title: str
    company: str = ""
    description: str = ""


class MultimodalMatchRequest(BaseModel):
    resume_text: str
    jobs: list[VisualJobMatch]


def _normalize_json_text(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def _fallback_job_description(target_role: str, analysis: dict[str, Any]) -> str:
    role_lower = target_role.lower()
    summary = analysis.get("summary", "").strip()

    requirements = [
        "strong communication and stakeholder collaboration",
        "evidence of project ownership and measurable outcomes",
        "ability to work with modern digital tools and structured workflows",
        "problem solving, adaptability, and continuous learning",
    ]

    responsibilities = [
        f"deliver high-quality work as a {target_role}",
        "translate requirements into clear actions and measurable results",
        "collaborate with cross-functional teams and communicate progress clearly",
        "improve processes, documentation, and reporting quality",
    ]

    if any(term in role_lower for term in ["data", "analyst", "analytics", "bi"]):
        requirements = [
            "SQL, Excel, Python, or BI tooling such as Power BI or Tableau",
            "data cleaning, reporting, dashboarding, and stakeholder communication",
            "analytical problem solving with measurable business impact",
            "clear presentation of insights and recommendations",
        ]
        responsibilities = [
            "analyze operational and business data to identify trends and opportunities",
            "build dashboards, reports, and actionable recommendations for stakeholders",
            "translate business questions into data requirements and structured analysis",
            "improve reporting accuracy, automation, and decision support",
        ]
    elif any(term in role_lower for term in ["frontend", "react", "ui", "web"]):
        requirements = [
            "React, JavaScript or TypeScript, HTML, CSS, and responsive UI development",
            "REST API integration, testing, and component-based architecture",
            "attention to user experience, accessibility, and performance",
            "collaboration with designers, product teams, and backend engineers",
        ]
        responsibilities = [
            "build and improve responsive user interfaces for web applications",
            "integrate APIs and present complex data in clear interaction flows",
            "maintain reusable components, testing quality, and visual consistency",
            "ship polished frontend experiences with measurable product impact",
        ]
    elif any(term in role_lower for term in ["backend", "python", "software", "api", "developer"]):
        requirements = [
            "Python, FastAPI or backend API development, SQL, and Git",
            "REST APIs, testing, debugging, and production-focused engineering",
            "cloud, Docker, CI/CD, or deployment familiarity",
            "clear communication, ownership, and measurable delivery outcomes",
        ]
        responsibilities = [
            "design and maintain backend services, APIs, and integrations",
            "improve reliability, performance, and developer workflow quality",
            "work with data models, testing, deployment, and production support",
            "communicate technical decisions and deliver business-facing outcomes",
        ]
    elif any(term in role_lower for term in ["cloud", "devops", "platform"]):
        requirements = [
            "AWS or Azure, Docker, CI/CD, infrastructure automation, and monitoring",
            "deployment reliability, incident response, and environment management",
            "Linux, scripting, and configuration management",
            "strong collaboration with engineering and product teams",
        ]
        responsibilities = [
            "maintain and improve cloud infrastructure, CI/CD, and observability",
            "support secure, reliable, and scalable deployment workflows",
            "automate operational tasks and strengthen release quality",
            "partner with engineering teams to improve platform performance and uptime",
        ]

    return (
        f"We are hiring a {target_role}. "
        f"The ideal candidate can {responsibilities[0]}, {responsibilities[1]}, {responsibilities[2]}, and {responsibilities[3]}. "
        f"Required skills include {requirements[0]}, {requirements[1]}, {requirements[2]}, and {requirements[3]}. "
        f"Candidates should demonstrate measurable impact, strong teamwork, and professional communication. "
        f"Resume context: {summary[:500]}"
    )


def derive_target_profile(analysis: dict[str, Any]) -> dict[str, str]:
    summary = analysis.get("summary", "").strip()
    resume_text = analysis.get("resume_text", "").strip()
    fallback_role = (suggest_job_keywords(summary) or ["Software Engineer"])[0]
    fallback_description = _fallback_job_description(fallback_role, analysis)

    if has_openai_config():
        try:
            response = ask_openai(
                "Based on this resume, choose the single best target role and write a concise ATS-style "
                "job description for that role. Return JSON only with keys target_role and job_description.\n\n"
                f"Resume summary:\n{summary}\n\nResume text:\n{resume_text[:2500]}",
                max_tokens=500,
            )
            parsed = json.loads(_normalize_json_text(response))
            target_role = str(parsed.get("target_role", "")).strip() or fallback_role
            job_description = str(parsed.get("job_description", "")).strip() or fallback_description
            return {"target_role": target_role, "job_description": job_description}
        except Exception:
            pass

    return {"target_role": fallback_role, "job_description": fallback_description}


def audio_to_base64(audio_bytes: bytes | None) -> str | None:
    if not audio_bytes:
        return None
    return base64.b64encode(audio_bytes).decode("utf-8")


def _base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def create_duix_signature(app_id: str, app_key: str, expires_in_seconds: int = 1800) -> str:
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"appId": app_id, "iat": now, "exp": now + expires_in_seconds}
    signing_input = f"{_base64url(json.dumps(header, separators=(',', ':')).encode())}.{_base64url(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = hmac.new(app_key.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_base64url(signature)}"


def get_duix_config() -> dict[str, str]:
    app_id = os.getenv("DUIX_APP_ID", "").strip().strip('"').strip("'")
    app_key = os.getenv("DUIX_APP_KEY", "").strip().strip('"').strip("'")
    conversation_id = os.getenv("DUIX_CONVERSATION_ID", "").strip().strip('"').strip("'")
    avatar_id = os.getenv("DUIX_AVATAR_ID", "").strip().strip('"').strip("'")
    platform = os.getenv("DUIX_PLATFORM", "duix.com").strip().strip('"').strip("'") or "duix.com"
    return {
        "app_id": app_id,
        "app_key": app_key,
        "conversation_id": conversation_id,
        "avatar_id": avatar_id,
        "platform": platform,
    }


def has_duix_config() -> bool:
    config = get_duix_config()
    return bool(config["app_id"] and config["app_key"] and config["conversation_id"])


def build_resume_analysis(resume_text: str) -> dict[str, Any]:
    summary = ""
    gaps = ""
    roadmap = ""
    mode = "fallback"

    if has_openai_config():
        try:
            summary = ask_openai(
                f"Summarize this resume highlighting the skills, education, and experience:\n\n{resume_text}",
                max_tokens=500,
            )
            gaps = ask_openai(
                "Analyze this resume and highlight missing skills, certificates, and experience needed "
                f"for better job opportunities:\n\n{resume_text}",
                max_tokens=400,
            )
            roadmap = ask_openai(
                "Based on this resume, suggest a future roadmap to improve this person's career prospects "
                f"(skills to learn, certifications needed, industry exposure):\n\n{resume_text}",
                max_tokens=400,
            )
            mode = "openai"
        except Exception:
            fallback = generate_resume_insights(resume_text)
            summary = fallback["summary"]
            gaps = fallback["gaps"]
            roadmap = fallback["roadmap"]
    else:
        fallback = generate_resume_insights(resume_text)
        summary = fallback["summary"]
        gaps = fallback["gaps"]
        roadmap = fallback["roadmap"]

    return {
        "summary": summary,
        "gaps": gaps,
        "roadmap": roadmap,
        "resume_text": resume_text,
        "mode": mode,
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "openai_ready": has_openai_config(),
        "apify_ready": has_apify_config(),
        "analysis_available": True,
        "ats_scoring_available": True,
        "resume_builder_available": True,
        "jobs_available": True,
        "jarvis_chat_available": True,
        "jarvis_voice_ready": has_openai_config(),
        "duix_avatar_ready": has_duix_config(),
        "agentic_ai_available": True,
        "course_recommender_available": True,
        "local_voice_stack": local_voice_stack_status(),
        "interview_profile_available": True,
        "interview_answer_scoring_available": True,
        "interview_tracking_available": True,
        "ocr_available": has_ocr_support(),
        "multimodal_matching_available": True,
        "embedding_support_available": has_embedding_support(),
    }


@app.get("/api/local-voice/stack")
def local_voice_stack() -> dict[str, Any]:
    return local_voice_stack_status()


@app.post("/api/analyze")
async def analyze_resume(resume: UploadFile = File(...)) -> dict[str, Any]:
    if not resume.filename:
        raise HTTPException(status_code=400, detail="Please upload a resume file.")

    try:
        parsed = extract_text_from_document(await resume.read(), resume.filename, resume.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    resume_text = parsed.get("text", "").strip()
    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text was found in this resume. Try a text-based PDF or DOCX file.",
        )

    result = build_resume_analysis(resume_text)
    result["filename"] = resume.filename
    result["document_mode"] = parsed.get("mode", "unknown")
    return result


@app.post("/api/intake/auto")
async def auto_resume_intake(
    resume: UploadFile = File(...),
    location: str = Form("United Kingdom"),
    target_role: str = Form(""),
    job_description: str = Form(""),
) -> dict[str, Any]:
    analysis = await analyze_resume(resume)
    clean_location = location.strip() or "United Kingdom"
    agentic_report = run_agentic_career_workflow(
        summary=analysis.get("summary", ""),
        resume_text=analysis.get("resume_text", ""),
        location=clean_location,
        prompt=(
            "Run an agentic intake workflow. Use the supplied job description if present; otherwise infer the strongest "
            "target role and create a provisional ATS benchmark. Find matching jobs, recommend next actions, and clearly "
            "flag any missing user inputs required for a real ATS comparison."
        ),
        target_role=target_role.strip(),
        job_description=job_description.strip(),
    )
    target_profile = agentic_report.get("derived_target_profile") or derive_agentic_target_profile(
        summary=analysis.get("summary", ""),
        resume_text=analysis.get("resume_text", ""),
    )
    resume_builder_report = build_resume_builder(
        ResumeBuilderRequest(
            resume_summary=analysis.get("summary", ""),
            resume_text=analysis.get("resume_text", ""),
            job_description=job_description.strip() or target_profile.get("job_description", ""),
            target_role=target_role.strip() or target_profile.get("target_role", ""),
        )
    )

    jobs = agentic_report.get("jobs_report")
    if not jobs:
        jobs = generate_jobs(
            JobRequest(
                summary=analysis.get("summary", ""),
                location=clean_location,
            )
        )

    return {
        "analysis": analysis,
        "resume_builder_report": resume_builder_report,
        "jobs": jobs,
        "auto_target": {
            "target_role": target_profile["target_role"],
            "job_description": target_profile["job_description"],
            "location": clean_location,
            "source": target_profile.get("source", "fallback"),
        },
        "ats_context": agentic_report.get("ats_context", {}),
        "agentic_report": agentic_report,
    }


@app.get("/api/analyze/demo")
def analyze_demo_resume() -> dict[str, Any]:
    demo_resume = BASE_DIR / "smoke_resume.pdf"
    if not demo_resume.exists():
        raise HTTPException(status_code=404, detail="Demo resume file was not found.")

    with demo_resume.open("rb") as resume_file:
        resume_text = extract_text_from_pdf(resume_file)
    result = build_resume_analysis(resume_text)
    result["filename"] = demo_resume.name
    return result


@app.post("/api/jobs")
def generate_jobs(payload: JobRequest) -> dict[str, Any]:
    try:
        location = payload.location.strip() or "United Kingdom"

        if has_openai_config():
            try:
                keywords = ask_openai(
                    "Based on this resume summary, suggest the best job titles and search keywords. Return a "
                    f"comma-separated list only, with no explanation.\n\nSummary: {payload.summary}",
                    max_tokens=100,
                ).replace("\n", " ").strip()
            except Exception:
                keywords = ", ".join(suggest_job_keywords(payload.summary))
        else:
            keywords = ", ".join(suggest_job_keywords(payload.summary))

        linkedin_jobs = []
        indeed_jobs = []

        if has_apify_config():
            linkedin_live = False
            indeed_live = False

            try:
                linkedin_jobs = fetch_linkedin_jobs(keywords, location=location, rows=16)
                if linkedin_jobs:
                    linkedin_live = True
                else:
                    linkedin_jobs = generate_demo_jobs(keywords, location=location, rows=12)
            except Exception:
                linkedin_jobs = generate_demo_jobs(keywords, location=location, rows=12)

            try:
                indeed_jobs = fetch_indeed_jobs(keywords, location=location, rows=16)
                if indeed_jobs:
                    indeed_live = True
                else:
                    indeed_jobs = generate_demo_jobs(keywords, location=location, rows=12)
            except Exception:
                indeed_jobs = generate_demo_jobs(keywords, location=location, rows=12)

            live_sources = int(linkedin_live) + int(indeed_live)
            if live_sources == 2:
                mode = "live"
            elif live_sources == 1:
                mode = "mixed"
            else:
                mode = "fallback"
        else:
            linkedin_jobs = generate_demo_jobs(keywords, location=location, rows=12)
            indeed_jobs = generate_demo_jobs(keywords, location=location, rows=12)
            mode = "fallback"
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {exc}") from exc

    return {
        "keywords": keywords,
        "location": location,
        "linkedin_jobs": linkedin_jobs,
        "indeed_jobs": indeed_jobs,
        "mode": mode,
    }


@app.post("/api/ats/score")
def ats_score(payload: AtsScoreRequest) -> dict[str, Any]:
    try:
        return build_ats_report(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ATS scoring failed: {exc}") from exc


@app.post("/api/resume-builder")
def build_resume_builder(payload: ResumeBuilderRequest) -> dict[str, Any]:
    try:
        return build_resume_builder_report(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Resume builder failed: {exc}") from exc


@app.post("/api/ats/export/csv")
def ats_export_csv(payload: AtsScoreRequest) -> dict[str, str]:
    try:
        report = build_ats_report(payload.model_dump())
        return {"filename": "ats-profile-report.csv", "content": ats_report_to_csv(report)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ATS export failed: {exc}") from exc


@app.post("/api/vision/parse")
async def parse_visual_resume(document: UploadFile = File(...)) -> dict[str, Any]:
    try:
        file_bytes = await document.read()
        extraction = extract_text_from_document(
            file_bytes,
            filename=document.filename or "upload",
            content_type=document.content_type,
        )
        sections = parse_document_layout(extraction["text"])
        profile = build_structured_profile(extraction["text"], sections)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Visual parsing failed: {exc}") from exc

    return {
        "filename": document.filename,
        "mode": extraction["mode"],
        "pages": extraction["pages"],
        "extracted_text": extraction["text"],
        "sections": sections,
        "profile": profile,
    }


@app.post("/api/vision/profile-from-screenshot")
async def profile_from_screenshot(document: UploadFile = File(...)) -> dict[str, Any]:
    parsed = await parse_visual_resume(document)
    return {
        "mode": parsed["mode"],
        "profile": parsed["profile"],
        "sections": parsed["sections"],
    }


@app.post("/api/multimodal/job-match")
def multimodal_job_match(payload: MultimodalMatchRequest) -> dict[str, Any]:
    try:
        return match_jobs_with_resume(
            payload.resume_text,
            [job.model_dump() for job in payload.jobs],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Multimodal job match failed: {exc}") from exc


@app.post("/api/jarvis/chat")
def jarvis_chat(payload: JarvisRequest) -> dict[str, Any]:
    try:
        if has_openai_config():
            try:
                reply = ask_interview_coach(
                    payload.summary,
                    [turn.model_dump() for turn in payload.conversation],
                    payload.prompt,
                )
                audio = audio_to_base64(synthesize_speech(reply))
                mode = "openai"
            except Exception:
                reply = fallback_interview_reply(payload.summary, payload.prompt)
                audio = None
                mode = "fallback"
        else:
            reply = fallback_interview_reply(payload.summary, payload.prompt)
            audio = None
            mode = "fallback"
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Jarvis failed: {exc}") from exc

    return {
        "reply": reply,
        "audio_base64": audio,
        "mode": mode,
    }


@app.post("/api/agentic/workflow")
def agentic_workflow(payload: AgenticRequest) -> dict[str, Any]:
    try:
        return run_agentic_career_workflow(
            summary=payload.summary,
            resume_text=payload.resume_text,
            location=payload.location.strip() or "United Kingdom",
            prompt=payload.prompt,
            target_role=payload.target_role,
            job_description=payload.job_description,
            conversation=[turn.model_dump() for turn in payload.conversation],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agentic workflow failed: {exc}") from exc


@app.post("/api/courses/recommend")
def course_recommendations(payload: CourseRecommendationRequest) -> dict[str, Any]:
    try:
        missing_skills = [skill.strip() for skill in payload.missing_skills if skill.strip()]
        if not missing_skills:
            raise HTTPException(status_code=400, detail="Provide at least one missing skill.")

        per_skill = max(1, min(payload.per_skill, 3))
        return recommend_youtube_courses(
            missing_skills=missing_skills,
            target_job_title=payload.target_job_title.strip(),
            per_skill=per_skill,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Course recommendation failed: {exc}") from exc


@app.post("/api/interview/feedback")
def interview_feedback(payload: InterviewFeedbackRequest) -> dict[str, Any]:
    try:
        return build_interview_feedback_report(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interview feedback failed: {exc}") from exc


@app.post("/api/interview/profile")
def interview_profile(payload: InterviewProfileRequest) -> dict[str, Any]:
    try:
        return build_interview_profile(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interview profile failed: {exc}") from exc


@app.post("/api/interview/score-answer")
def interview_score_answer(payload: InterviewScoreRequest) -> dict[str, Any]:
    try:
        return score_interview_answer(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interview answer scoring failed: {exc}") from exc


@app.post("/api/interview/presence")
def interview_presence(payload: InterviewPresenceRequest) -> dict[str, Any]:
    try:
        return evaluate_interview_presence(payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interview presence analysis failed: {exc}") from exc


@app.get("/api/duix/session")
def duix_session() -> dict[str, Any]:
    config = get_duix_config()
    if not has_duix_config():
        raise HTTPException(
            status_code=400,
            detail="DuiX avatar needs DUIX_APP_ID, DUIX_APP_KEY, and DUIX_CONVERSATION_ID in the backend environment.",
        )

    return {
        "appId": config["app_id"],
        "sign": create_duix_signature(config["app_id"], config["app_key"]),
        "conversationId": config["conversation_id"],
        "avatarId": config["avatar_id"],
        "platform": config["platform"],
        "authMode": "signed-session",
        "expiresIn": 1800,
    }


@app.post("/api/jarvis/voice")
async def jarvis_voice(
    audio: UploadFile = File(...),
    summary: str = Form(""),
    conversation: str = Form("[]"),
) -> dict[str, Any]:
    if not has_openai_config():
        raise HTTPException(status_code=400, detail="Voice mode needs a working OPENAI_API_KEY.")

    try:
        conversation_data = json.loads(conversation)
        transcript = transcribe_audio(await audio.read())
        reply = ask_interview_coach(summary, conversation_data, transcript)
        audio_data = audio_to_base64(synthesize_speech(reply))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice coaching failed: {exc}") from exc

    return {
        "transcript": transcript,
        "reply": reply,
        "audio_base64": audio_data,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
