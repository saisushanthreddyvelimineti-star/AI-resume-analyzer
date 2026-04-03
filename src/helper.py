import os
import re
from io import BytesIO

import fitz
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def has_openai_config():
    api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    return api_key.startswith("sk-")


def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def _get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    if not api_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY does not look valid.")
    return OpenAI(api_key=api_key)


def ask_openai(prompt, max_tokens=500):
    """Send a prompt to the OpenAI API and return the response text."""
    client = _get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


COMMON_SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Power BI",
    "Excel",
    "AWS",
    "Azure",
    "Docker",
    "Git",
    "Streamlit",
    "FastAPI",
    "HTML",
    "CSS",
]


def _normalize_resume_text(resume_text):
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    compact_text = re.sub(r"\s+", " ", resume_text).strip()
    return lines, compact_text


def _extract_resume_signals(resume_text):
    lines, compact_text = _normalize_resume_text(resume_text)
    lower_text = compact_text.lower()
    found_skills = [skill for skill in COMMON_SKILLS if skill.lower() in lower_text]
    experience_lines = [
        line for line in lines if any(token in line.lower() for token in ["experience", "intern", "engineer", "developer", "analyst", "project"])
    ][:5]
    education_lines = [
        line for line in lines if any(token in line.lower() for token in ["b.tech", "bachelor", "master", "university", "college", "education"])
    ][:3]
    return {
        "skills": found_skills[:8],
        "experience_lines": experience_lines,
        "education_lines": education_lines,
        "compact_text": compact_text,
        "lines": lines,
    }


def generate_resume_insights(resume_text):
    signals = _extract_resume_signals(resume_text)
    skills = signals["skills"] or ["communication", "problem solving", "adaptability"]
    experience = signals["experience_lines"] or ["Experience details were limited in the extracted text."]
    education = signals["education_lines"] or ["Education details were limited in the extracted text."]

    summary = (
        "This resume shows a profile with strengths in "
        + ", ".join(skills[:5])
        + ". "
        + "Relevant experience signals include: "
        + "; ".join(experience[:2])
        + ". "
        + "Education indicators include: "
        + "; ".join(education[:1])
        + "."
    )

    missing = []
    for item in ["SQL", "Docker", "AWS", "Azure", "React", "Machine Learning"]:
        if item not in skills:
            missing.append(item)
    gaps = (
        "Potential improvement areas: "
        + ", ".join(missing[:4])
        + ". Add stronger proof of impact with metrics, clearer project outcomes, and role-specific keywords for target jobs."
    )

    roadmap = (
        "Recommended roadmap: strengthen one core stack, build 2-3 measurable portfolio projects, "
        "add quantified resume bullets, prepare STAR stories for key projects, and align your resume with "
        "roles such as "
        + ", ".join(suggest_job_keywords(summary)[:3])
        + "."
    )
    return {"summary": summary, "gaps": gaps, "roadmap": roadmap}


def suggest_job_keywords(resume_summary):
    summary = resume_summary.lower()
    roles = []
    if any(word in summary for word in ["machine learning", "data", "analysis", "power bi"]):
        roles.extend(["Data Analyst", "Business Analyst", "Machine Learning Intern"])
    if any(word in summary for word in ["react", "javascript", "html", "css", "frontend"]):
        roles.extend(["Frontend Developer", "React Developer", "UI Engineer"])
    if any(word in summary for word in ["python", "fastapi", "backend", "api"]):
        roles.extend(["Python Developer", "Backend Developer", "Software Engineer"])
    if any(word in summary for word in ["aws", "azure", "docker", "devops"]):
        roles.extend(["Cloud Engineer", "DevOps Engineer"])
    if not roles:
        roles = ["Software Engineer", "Graduate Engineer", "Analyst"]
    # Preserve order while deduplicating.
    deduped_roles = list(dict.fromkeys(roles))
    return deduped_roles[:5]


def fallback_interview_reply(resume_summary, user_prompt):
    target_roles = ", ".join(suggest_job_keywords(resume_summary)[:3])
    return (
        "Jarvis fallback mode active.\n\n"
        "What the interviewer is likely testing: clarity, ownership, impact, and role fit.\n\n"
        "How to answer:\n"
        "1. Start with the situation in one line.\n"
        "2. Explain your task and the constraint.\n"
        "3. Describe the exact action you took.\n"
        "4. End with a measurable result and what you learned.\n\n"
        f"Use your background to steer answers toward roles like {target_roles}.\n\n"
        f"Your prompt was: {user_prompt}\n"
        "Practice follow-up: give me a 60-second answer with one metric and one technical decision."
    )


def transcribe_audio(uploaded_audio):
    """Transcribe an uploaded audio clip using OpenAI audio transcription."""
    client = _get_openai_client()
    if isinstance(uploaded_audio, bytes):
        audio_bytes = uploaded_audio
        file_name = "voice_note.wav"
    elif hasattr(uploaded_audio, "getvalue"):
        audio_bytes = uploaded_audio.getvalue()
        file_name = getattr(uploaded_audio, "name", "voice_note.wav")
    else:
        audio_bytes = uploaded_audio.read()
        file_name = getattr(uploaded_audio, "name", "voice_note.wav")
    audio_file = BytesIO(audio_bytes)
    audio_file.name = file_name
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
    )
    return transcript.text


def synthesize_speech(text):
    """Convert assistant text into spoken audio bytes."""
    client = _get_openai_client()
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )
    return response.read()


def ask_interview_coach(resume_summary, conversation, user_prompt):
    """Generate a concise interview-coach response grounded in the resume."""
    client = _get_openai_client()
    messages = [
        {
            "role": "system",
            "content": (
                "You are Jarvis, a sharp interview coach. Help the user crack interviews with "
                "clear, practical answers. Use the resume summary as context. When useful, give "
                "STAR-based answer structure, likely interviewer intent, a better sample answer, "
                "and one follow-up question for practice. Keep responses concise but high signal."
            ),
        },
        {
            "role": "system",
            "content": f"Resume summary:\n{resume_summary}",
        },
    ]
    messages.extend(conversation[-6:])
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.6,
        max_tokens=500,
    )
    return response.choices[0].message.content or ""
