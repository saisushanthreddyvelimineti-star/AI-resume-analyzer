import base64
import json
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs, generate_demo_jobs, has_apify_config


app = FastAPI(title="Jarvis Career Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobRequest(BaseModel):
    summary: str


class ChatTurn(BaseModel):
    role: str
    content: str


class JarvisRequest(BaseModel):
    summary: str
    prompt: str
    conversation: list[ChatTurn] = []


def audio_to_base64(audio_bytes: bytes | None) -> str | None:
    if not audio_bytes:
        return None
    return base64.b64encode(audio_bytes).decode("utf-8")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "openai_ready": has_openai_config(),
        "apify_ready": has_apify_config(),
        "analysis_available": True,
        "jobs_available": True,
        "jarvis_chat_available": True,
        "jarvis_voice_ready": has_openai_config(),
    }


@app.post("/api/analyze")
async def analyze_resume(resume: UploadFile = File(...)) -> dict[str, Any]:
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    resume_text = extract_text_from_pdf(resume.file)
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


@app.post("/api/jobs")
def generate_jobs(payload: JobRequest) -> dict[str, Any]:
    try:
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

        if has_apify_config():
            try:
                linkedin_jobs = fetch_linkedin_jobs(keywords, rows=9)
                naukri_jobs = fetch_naukri_jobs(keywords, rows=9)
                mode = "live"
            except Exception:
                linkedin_jobs = generate_demo_jobs(keywords, rows=6)
                naukri_jobs = generate_demo_jobs(keywords, rows=6)
                mode = "fallback"
        else:
            linkedin_jobs = generate_demo_jobs(keywords, rows=6)
            naukri_jobs = generate_demo_jobs(keywords, rows=6)
            mode = "fallback"
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {exc}") from exc

    return {
        "keywords": keywords,
        "linkedin_jobs": linkedin_jobs,
        "naukri_jobs": naukri_jobs,
        "mode": mode,
    }


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
