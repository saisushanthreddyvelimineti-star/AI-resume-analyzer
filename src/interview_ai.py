from __future__ import annotations

import json
import re
from typing import Any

from src.helper import ask_openai, has_openai_config


CORE_SKILLS = [
    "Python",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "FastAPI",
    "SQL",
    "Machine Learning",
    "Data Analysis",
    "Power BI",
    "AWS",
    "Azure",
    "Docker",
    "Git",
    "Testing",
    "APIs",
    "Communication",
]


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _score_0_1(value: Any, default: float = 0.5) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number > 1:
        number = number / 100
    return max(0.0, min(1.0, number))


def _extract_skills(*texts: str) -> list[str]:
    combined = " ".join(texts).lower()
    found = [skill for skill in CORE_SKILLS if skill.lower() in combined]
    return list(dict.fromkeys(found))[:10]


def _split_keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z+#.\-]{2,}", text)
    blocked = {
        "and",
        "the",
        "for",
        "with",
        "from",
        "that",
        "this",
        "your",
        "will",
        "role",
        "candidate",
        "experience",
    }
    ranked: dict[str, int] = {}
    for word in words:
        key = word.strip(".,").lower()
        if key in blocked:
            continue
        ranked[key] = ranked.get(key, 0) + 1
    return [word.title() for word, _ in sorted(ranked.items(), key=lambda item: item[1], reverse=True)[:10]]


def _fallback_questions(target_role: str, focus_areas: list[str], difficulty: str) -> list[dict[str, str]]:
    focus = focus_areas or ["project impact", "technical decisions", "role fit"]
    pressure = "with tradeoffs and measurable impact" if difficulty.lower() == "hard" else "clearly and specifically"
    return [
        {
            "round": "Opening",
            "question": f"Walk me through your background and why it fits this {target_role} role.",
            "probe": "Listen for role fit, concise structure, and evidence from the resume.",
        },
        {
            "round": "Project Depth",
            "question": f"Choose one project related to {focus[0]} and explain your exact contribution {pressure}.",
            "probe": "Ask what they personally owned, what changed, and how they measured success.",
        },
        {
            "round": "Technical",
            "question": f"What is the strongest technical decision you made, and what alternative did you reject?",
            "probe": "Push for reasoning, constraints, and tradeoffs.",
        },
        {
            "round": "Gap Probe",
            "question": f"This role may need {', '.join(focus[:2])}. Where are you strongest and where are you still improving?",
            "probe": "Look for honest self-awareness and a practical learning plan.",
        },
        {
            "round": "Close",
            "question": "Why should we choose you over another candidate with similar technical skills?",
            "probe": "Listen for differentiation, confidence, and role-specific evidence.",
        },
    ]


def _profile_prompt(payload: dict[str, Any]) -> str:
    return f"""
Return valid JSON only.

Create a personalized mock interview profile.

Resume summary:
{payload.get("resume_summary", "")[:1800]}

Resume text excerpt:
{payload.get("resume_text", "")[:2200]}

Target role:
{payload.get("target_role", "Software Engineer")}

Job description:
{payload.get("job_description", "")[:2200]}

Difficulty:
{payload.get("difficulty", "Medium")}

Interviewer style:
{payload.get("interviewer_style", "Balanced")}

JSON shape:
{{
  "strengths": ["short", "short"],
  "gaps": ["short", "short"],
  "focus_areas": ["short", "short", "short"],
  "likely_themes": ["short", "short", "short"],
  "missing_keywords": ["keyword", "keyword"],
  "question_bank": [
    {{"round": "Opening", "question": "question text", "probe": "what to evaluate"}}
  ],
  "realtime_instructions": "system prompt for a spoken realtime interviewer"
}}
""".strip()


def build_interview_profile(payload: dict[str, Any]) -> dict[str, Any]:
    resume_summary = payload.get("resume_summary", "")
    resume_text = payload.get("resume_text", "")
    target_role = payload.get("target_role") or "Software Engineer"
    job_description = payload.get("job_description", "")
    difficulty = payload.get("difficulty") or "Medium"
    interviewer_style = payload.get("interviewer_style") or "Balanced"

    resume_skills = _extract_skills(resume_summary, resume_text)
    jd_skills = _extract_skills(job_description)
    jd_keywords = _split_keywords(job_description)
    missing = [skill for skill in jd_skills if skill not in resume_skills]
    focus_areas = (missing + jd_keywords + resume_skills)[:5] or ["role fit", "project depth", "communication"]
    strengths = resume_skills[:4] or ["problem solving", "communication", "learning agility"]
    gaps = missing[:4] or ["add more measurable impact", "prepare deeper technical tradeoffs"]
    questions = _fallback_questions(target_role, focus_areas, difficulty)
    instructions = (
        f"You are a {interviewer_style.lower()} professional mock interviewer for a {target_role} role. "
        "Speak naturally, keep live responses short, ask one question at a time, wait for the candidate, "
        "ask adaptive follow-ups, challenge vague claims politely, and save model answers until the end. "
        f"Focus on: {', '.join(focus_areas[:4])}."
    )

    fallback = {
        "mode": "fallback",
        "target_role": target_role,
        "difficulty": difficulty,
        "interviewer_style": interviewer_style,
        "resume_skills": resume_skills,
        "job_keywords": jd_keywords,
        "strengths": strengths,
        "gaps": gaps,
        "focus_areas": focus_areas,
        "likely_themes": ["resume walkthrough", "project ownership", "technical tradeoffs", "role motivation"],
        "missing_keywords": missing[:6] or jd_keywords[:6],
        "question_bank": questions,
        "realtime_instructions": instructions,
    }

    if not has_openai_config():
        return fallback

    try:
        raw = ask_openai(_profile_prompt(payload), max_tokens=900)
        parsed = json.loads(raw)
        return {
            **fallback,
            "mode": "openai",
            "strengths": list(parsed.get("strengths") or fallback["strengths"])[:6],
            "gaps": list(parsed.get("gaps") or fallback["gaps"])[:6],
            "focus_areas": list(parsed.get("focus_areas") or fallback["focus_areas"])[:6],
            "likely_themes": list(parsed.get("likely_themes") or fallback["likely_themes"])[:6],
            "missing_keywords": list(parsed.get("missing_keywords") or fallback["missing_keywords"])[:8],
            "question_bank": list(parsed.get("question_bank") or fallback["question_bank"])[:8],
            "realtime_instructions": str(parsed.get("realtime_instructions") or fallback["realtime_instructions"]),
        }
    except Exception:
        return fallback


def _score_prompt(payload: dict[str, Any]) -> str:
    return f"""
Return valid JSON only.

Score this mock interview answer from 1 to 5.

Interview profile:
{json.dumps(payload.get("interview_profile", {}))[:2200]}

Question:
{payload.get("question", "")}

Candidate answer:
{payload.get("answer", "")[:1800]}

JSON shape:
{{
  "scores": {{
    "relevance": 1,
    "clarity": 1,
    "structure": 1,
    "technical_depth": 1,
    "examples": 1,
    "confidence": 1,
    "conciseness": 1
  }},
  "overall": 1,
  "strengths": ["short"],
  "improvements": ["short"],
  "model_answer": "stronger sample answer",
  "follow_up_question": "next adaptive question"
}}
""".strip()


def score_interview_answer(payload: dict[str, Any]) -> dict[str, Any]:
    answer = (payload.get("answer") or "").strip()
    profile = payload.get("interview_profile") or {}
    focus_areas = profile.get("focus_areas") or []
    answer_lower = answer.lower()
    word_count = len(answer.split())
    relevance_hits = sum(1 for area in focus_areas if str(area).lower() in answer_lower)

    scores = {
        "relevance": _clamp(2.5 + relevance_hits, 1, 5),
        "clarity": 4 if 45 <= word_count <= 180 else 3 if word_count > 20 else 2,
        "structure": 4 if any(token in answer_lower for token in ["situation", "task", "action", "result", "because", "first"]) else 3,
        "technical_depth": 4 if any(skill.lower() in answer_lower for skill in CORE_SKILLS) else 2.5,
        "examples": 4 if any(char.isdigit() for char in answer) or "project" in answer_lower else 2.5,
        "confidence": 4 if not any(token in answer_lower for token in ["maybe", "i guess", "sort of"]) else 2.5,
        "conciseness": 4 if word_count <= 180 else 2.5,
    }
    overall = round(sum(scores.values()) / len(scores), 1)
    fallback = {
        "mode": "fallback",
        "scores": {key: round(float(value), 1) for key, value in scores.items()},
        "overall": overall,
        "strengths": ["The answer gives enough signal to continue the interview."],
        "improvements": [
            "Use a clearer STAR structure with one specific metric.",
            "Tie the answer back to the target role requirements.",
        ],
        "model_answer": (
            "A stronger answer would briefly set the context, state your responsibility, explain the technical "
            "or behavioral action you took, and close with a measurable result plus what you learned."
        ),
        "follow_up_question": "What tradeoff did you make in that situation, and why was it the right choice?",
    }

    if not has_openai_config():
        return fallback

    try:
        raw = ask_openai(_score_prompt(payload), max_tokens=700)
        parsed = json.loads(raw)
        parsed_scores = parsed.get("scores") or fallback["scores"]
        return {
            "mode": "openai",
            "scores": {key: round(_clamp(float(value), 1, 5), 1) for key, value in parsed_scores.items()},
            "overall": round(_clamp(float(parsed.get("overall") or fallback["overall"]), 1, 5), 1),
            "strengths": list(parsed.get("strengths") or fallback["strengths"])[:4],
            "improvements": list(parsed.get("improvements") or fallback["improvements"])[:4],
            "model_answer": str(parsed.get("model_answer") or fallback["model_answer"]),
            "follow_up_question": str(parsed.get("follow_up_question") or fallback["follow_up_question"]),
        }
    except Exception:
        return fallback


def summarize_interview_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    duration_seconds = float(payload.get("duration_seconds") or 0.0)
    face_visible_ratio = float(payload.get("face_visible_ratio") or 0.0)
    attentive_ratio = float(payload.get("attentive_ratio") or 0.0)
    average_attention_score = float(payload.get("average_attention_score") or 0.0)
    distraction_events = int(payload.get("distraction_events") or 0)
    absence_events = int(payload.get("absence_events") or 0)
    longest_absence_seconds = float(payload.get("longest_absence_seconds") or 0.0)
    longest_distraction_seconds = float(payload.get("longest_distraction_seconds") or 0.0)

    presence_score = _clamp(face_visible_ratio * 100.0)
    attention_score = _clamp(average_attention_score * 100.0)
    stability_penalty = distraction_events * 3.0 + absence_events * 4.0 + longest_absence_seconds * 0.6
    engagement_score = _clamp((presence_score * 0.35) + (attention_score * 0.5) + (attentive_ratio * 100.0 * 0.15) - stability_penalty)

    strengths: list[str] = []
    improvements: list[str] = []
    risks: list[str] = []

    if presence_score >= 88:
        strengths.append("Strong camera presence was maintained for most of the session.")
    elif presence_score >= 72:
        strengths.append("Presence was mostly stable with only brief dropouts.")
    else:
        improvements.append("Stay inside the camera frame more consistently to avoid weak interviewer presence.")
        risks.append("Frequent loss of face visibility can look disengaged in remote interviews.")

    if attention_score >= 82:
        strengths.append("Attention remained high with good forward focus.")
    elif attention_score >= 65:
        improvements.append("Reduce side glances and off-screen checks to improve attention consistency.")
    else:
        improvements.append("Attention drift was high. Practice answering while keeping gaze closer to the lens.")
        risks.append("Sustained gaze drift may be interpreted as low confidence or poor listening.")

    if longest_absence_seconds >= 4:
        risks.append("A long absence from the frame was detected during the session.")
    if longest_distraction_seconds >= 5:
        risks.append("A prolonged distraction period suggests weak interview stamina.")
    if distraction_events <= 2 and attention_score >= 75:
        strengths.append("Visual engagement remained stable without frequent distraction spikes.")

    if not strengths:
        strengths.append("The session still provides enough telemetry to guide practice improvements.")
    if not improvements:
        improvements.append("Maintain the same posture, camera alignment, and visual focus in longer interviews.")

    overall = "strong" if engagement_score >= 80 else "good" if engagement_score >= 65 else "developing"
    snapshot = {
        "overall_rating": overall,
        "engagement_score": round(engagement_score, 1),
        "presence_score": round(presence_score, 1),
        "attention_score": round(attention_score, 1),
        "duration_seconds": round(duration_seconds, 1),
        "strengths": strengths[:3],
        "improvements": improvements[:3],
        "risks": risks[:3],
    }
    return snapshot


def _feedback_prompt(payload: dict[str, Any], metrics: dict[str, Any]) -> str:
    role = payload.get("role") or "general interview"
    transcript = payload.get("transcript") or "No transcript provided."
    return f"""
You are an advanced mock interview evaluator.
Return valid JSON only.

Candidate role target: {role}
Transcript excerpt:
{transcript[:1800]}

Telemetry:
{metrics}

Required JSON format:
{{
  "summary": "2-3 sentence evaluation",
  "presence_feedback": ["short point", "short point"],
  "attention_feedback": ["short point", "short point"],
  "behavioral_feedback": ["short point", "short point"],
  "recommended_actions": ["short action", "short action", "short action"]
}}
""".strip()


def build_interview_feedback_report(payload: dict[str, Any]) -> dict[str, Any]:
    metrics = summarize_interview_metrics(payload)
    fallback = {
        "summary": (
            f"The mock interview session was rated {metrics['overall_rating']} with an engagement score of "
            f"{metrics['engagement_score']}/100. Presence and attention telemetry suggest the candidate should "
            "focus on steadier eye-line control and stronger on-camera consistency."
        ),
        "presence_feedback": metrics["strengths"][:1] + metrics["improvements"][:1],
        "attention_feedback": [
            f"Attention score: {metrics['attention_score']}/100.",
            "Keep gaze near the camera lens when listening and answering.",
        ],
        "behavioral_feedback": [
            "Use a stable upright posture and avoid repeated screen checks.",
            "Pause briefly before answering instead of looking away for recall.",
        ],
        "recommended_actions": [
            "Practice 5-minute mock answers while keeping your face centered in frame.",
            "Move notes closer to the webcam to reduce eye-line drift.",
            "Rehearse with timed follow-up questions to improve stamina under attention tracking.",
        ],
    }

    if not has_openai_config():
        return {"mode": "fallback", "metrics": metrics, **fallback}

    try:
        raw = ask_openai(_feedback_prompt(payload, metrics), max_tokens=500)
        import json

        parsed = json.loads(raw)
        return {
            "mode": "openai",
            "metrics": metrics,
            "summary": str(parsed.get("summary") or fallback["summary"]),
            "presence_feedback": list(parsed.get("presence_feedback") or fallback["presence_feedback"])[:4],
            "attention_feedback": list(parsed.get("attention_feedback") or fallback["attention_feedback"])[:4],
            "behavioral_feedback": list(parsed.get("behavioral_feedback") or fallback["behavioral_feedback"])[:4],
            "recommended_actions": list(parsed.get("recommended_actions") or fallback["recommended_actions"])[:5],
        }
    except Exception:
        return {"mode": "fallback", "metrics": metrics, **fallback}


def evaluate_interview_presence(payload: dict[str, Any]) -> dict[str, Any]:
    face_detected = bool(payload.get("face_detected", True))
    face_visibility = _score_0_1(payload.get("face_visibility_score"), 0.75 if face_detected else 0.0)
    face_centered = _score_0_1(payload.get("face_centered_score"), 0.7)
    eye_contact = _score_0_1(payload.get("eye_contact_score"), 0.7)
    head_stability = _score_0_1(payload.get("head_stability_score"), 0.7)
    posture = _score_0_1(payload.get("posture_score"), 0.7)
    shoulder_tension = _score_0_1(payload.get("shoulder_tension_score"), 0.7)
    fidget = _score_0_1(payload.get("fidget_score"), 0.7)
    expression = _score_0_1(payload.get("expression_consistency_score"), 0.7)
    smile = _score_0_1(payload.get("smile_naturalness_score"), 0.65)
    attention = _score_0_1(payload.get("attention_score"), 0.7)
    stress = _score_0_1(payload.get("stress_signal_score"), 0.35)
    calmness = _score_0_1(payload.get("calmness_signal_score"), 0.65)
    recovery = _score_0_1(payload.get("recovery_after_hesitation_score"), 0.6)
    speaking_alignment = _score_0_1(payload.get("speaking_alignment_score"), 0.65)
    gaze_away_frequency = _score_0_1(payload.get("gaze_away_frequency"), 0.25)
    dominant_emotion = str(payload.get("dominant_emotion") or "neutral")
    notable_events = payload.get("notable_events") if isinstance(payload.get("notable_events"), list) else []

    calmness_score = (calmness * 0.55 + (1 - stress) * 0.25 + recovery * 0.20) * 100
    eye_score = (eye_contact * 0.70 + (1 - gaze_away_frequency) * 0.20 + face_centered * 0.10) * 100
    expression_score = (expression * 0.65 + smile * 0.20 + face_visibility * 0.15) * 100
    posture_score = (posture * 0.45 + head_stability * 0.30 + shoulder_tension * 0.15 + fidget * 0.10) * 100
    emotional_score = (calmness * 0.35 + expression * 0.25 + (1 - stress) * 0.20 + recovery * 0.20) * 100
    presence_score = (attention * 0.35 + speaking_alignment * 0.20 + eye_contact * 0.20 + posture * 0.15 + face_visibility * 0.10) * 100

    if not face_detected or face_visibility < 0.35:
        calmness_score *= 0.75
        eye_score *= 0.55
        expression_score *= 0.55
        posture_score *= 0.70
        emotional_score *= 0.70
        presence_score *= 0.65

    dimensions = {
        "calmness_composure": round(_clamp(calmness_score)),
        "eye_contact": round(_clamp(eye_score)),
        "facial_expression": round(_clamp(expression_score)),
        "posture_body_stability": round(_clamp(posture_score)),
        "emotional_control": round(_clamp(emotional_score)),
        "overall_presence_confidence": round(_clamp(presence_score)),
    }
    weights = {
        "calmness_composure": 20,
        "eye_contact": 20,
        "facial_expression": 15,
        "posture_body_stability": 15,
        "emotional_control": 15,
        "overall_presence_confidence": 15,
    }
    total = round(sum(dimensions[key] * weight for key, weight in weights.items()) / 100)
    confidence = round(_clamp((face_visibility * 0.45 + attention * 0.25 + speaking_alignment * 0.15 + face_centered * 0.15) * 100))
    if not face_detected:
        confidence = min(confidence, 30)

    strengths: list[str] = []
    improvements: list[str] = []
    if dimensions["eye_contact"] >= 72:
        strengths.append("Eye contact looked steady and interview-friendly.")
    else:
        improvements.append("Look closer to the camera naturally during key points.")

    if dimensions["posture_body_stability"] >= 72:
        strengths.append("Posture and body position looked stable.")
    else:
        improvements.append("Sit upright, stay centered, and reduce unnecessary movement.")

    if dimensions["calmness_composure"] >= 72:
        strengths.append("You appeared calm and composed through the answer.")
    else:
        improvements.append("Take a slow breath before continuing when you feel rushed.")

    if recovery >= 0.7 and stress > 0.45:
        strengths.append("You showed positive recovery after a nervous moment.")
    if expression < 0.5:
        improvements.append("Keep your facial expression relaxed and engaged.")
    if attention < 0.5:
        improvements.append("Refocus on the interviewer and avoid visible distractions.")

    if not face_detected or face_visibility < 0.35:
        strengths = []
        improvements = ["Make sure your face is visible, well-lit, and centered before the answer."]
        summary = "Interview presence cannot be assessed reliably because the face was not visible enough."
        active_tip = "Move into frame and keep your face visible."
    else:
        summary = "Your interview presence was assessed from visible camera behavior. Use the suggestions as coaching cues, not diagnostic conclusions."
        if dimensions["eye_contact"] < 55:
            active_tip = "Try to look closer to the camera."
        elif dimensions["posture_body_stability"] < 55:
            active_tip = "Sit upright and stay centered."
        elif dimensions["calmness_composure"] < 55:
            active_tip = "Take a slow breath and continue."
        elif recovery >= 0.7 and stress > 0.45:
            active_tip = "Nice recovery, keep going."
        elif total >= 78:
            active_tip = "Good presence — keep it steady."
        else:
            active_tip = ""

    return {
        "engine": "Interview Presence AI",
        "session_id": payload.get("session_id", "local-session"),
        "question_id": payload.get("question_id", ""),
        "answer_id": payload.get("answer_id", ""),
        "score_total": total,
        "score_confidence": confidence,
        "dimensions": dimensions,
        "dominant_emotion": dominant_emotion,
        "strengths": strengths[:3],
        "improvement_areas": improvements[:4],
        "real_time_tip": active_tip,
        "summary": summary,
        "notable_events": notable_events[:6],
        "safety_note": "This is interview coaching based on visible behavior, not a medical, psychological, or biometric diagnosis.",
    }
