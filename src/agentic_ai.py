from __future__ import annotations

import json
import re
from typing import Any

from src.ats_ai import build_ats_report
from src.course_recommender import recommend_youtube_courses
from src.helper import (
    ask_openai,
    fallback_interview_reply,
    generate_resume_insights,
    has_openai_config,
    suggest_job_keywords,
)
from src.interview_ai import build_interview_profile
from src.job_api import fetch_indeed_jobs, fetch_linkedin_jobs, generate_demo_jobs, has_apify_config


TOOL_REGISTRY = {
    "profile_analysis": "Analyze resume summary and infer strengths, gaps, and role direction.",
    "target_role_inference": "Infer the strongest target role and build a provisional benchmark job description.",
    "ats_score": "Compare resume against the supplied job description or a provisional benchmark if no JD exists.",
    "job_search": "Generate role search keywords and job recommendations.",
    "course_recommendations": "Recommend YouTube courses for missing skills.",
    "interview_plan": "Create a role-aware mock interview plan and question bank.",
    "interview_coaching": "Produce interview strategy and answer guidance.",
    "verifier": "Check assumptions, missing inputs, and next actions.",
}


def _extract_json_block(raw_text: str) -> dict[str, Any] | None:
    text = (raw_text or "").strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        parsed = json.loads(text[start : end + 1])
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_json_text(raw_text: str) -> str:
    cleaned = (raw_text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _clean_skill(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9+#./ -]", " ", value or "")
    text = re.sub(r"\s+", " ", text).strip(" .,-")
    return text[:42]


def _dedupe(items: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = item.strip()
        if clean and clean.lower() not in seen:
            ordered.append(clean)
            seen.add(clean.lower())
    return ordered


def _fallback_job_description(target_role: str, summary: str) -> str:
    role_lower = target_role.lower()
    clean_summary = summary.strip()

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
        "Candidates should demonstrate measurable impact, strong teamwork, and professional communication. "
        f"Resume context: {clean_summary[:500]}"
    )


def derive_target_profile(*, summary: str, resume_text: str = "", preferred_role: str = "") -> dict[str, str]:
    clean_summary = summary.strip() or resume_text.strip()
    fallback_role = preferred_role.strip() or (suggest_job_keywords(clean_summary) or ["Software Engineer"])[0]
    fallback_description = _fallback_job_description(fallback_role, clean_summary)

    if has_openai_config():
        try:
            response = ask_openai(
                "Based on this resume, choose the single best target role and write a concise ATS-style job description "
                "for that role. Return JSON only with keys target_role and job_description. "
                "If a preferred role is supplied, keep it unless the resume clearly points elsewhere.\n\n"
                f"Preferred role: {preferred_role or 'Not supplied'}\n\n"
                f"Resume summary:\n{clean_summary}\n\nResume text:\n{resume_text[:2500]}",
                max_tokens=500,
            )
            parsed = json.loads(_normalize_json_text(response))
            target_role = str(parsed.get("target_role", "")).strip() or fallback_role
            job_description = str(parsed.get("job_description", "")).strip() or _fallback_job_description(
                target_role,
                clean_summary,
            )
            return {
                "target_role": target_role,
                "job_description": job_description,
                "source": "openai",
            }
        except Exception:
            pass

    return {
        "target_role": fallback_role,
        "job_description": fallback_description,
        "source": "fallback",
    }


def _infer_missing_skills(summary: str, prompt: str, ats_report: dict[str, Any] | None = None) -> list[str]:
    skills: list[str] = []
    if ats_report:
        skills.extend(_clean_skill(item) for item in ats_report.get("missing_keywords", [])[:6])

    text = f"{summary}\n{prompt}".lower()
    keyword_map = [
        ("sql", "SQL"),
        ("python", "Python"),
        ("excel", "Excel"),
        ("power bi", "Power BI"),
        ("tableau", "Tableau"),
        ("communication", "Communication"),
        ("project", "Project Management"),
        ("marketing", "Digital Marketing"),
        ("sales", "Sales Strategy"),
        ("finance", "Financial Analysis"),
        ("healthcare", "Healthcare Compliance"),
        ("teaching", "Classroom Management"),
        ("cloud", "Cloud Fundamentals"),
        ("data", "Data Analysis"),
    ]
    for needle, skill in keyword_map:
        if needle in text and skill not in skills:
            skills.append(skill)

    if not skills:
        skills = ["Interview Communication", "Role-Specific Portfolio", "ATS Keyword Targeting"]
    return [skill for skill in skills if skill][:8]


def _suggest_search_keywords(summary: str, target_role: str, prompt: str) -> list[str]:
    fallback_keywords = _dedupe(([target_role] if target_role.strip() else []) + suggest_job_keywords(f"{summary} {prompt}"))
    if not has_openai_config():
        return fallback_keywords[:12]

    try:
        response = ask_openai(
            "Based on this resume summary and user goal, suggest the best role titles and search keywords for job search. "
            "Return a comma-separated list only with 8 to 12 items.\n\n"
            f"Resume summary: {summary}\n\nTarget role: {target_role or 'Any role'}\n\nGoal: {prompt or 'Run a complete career workflow.'}",
            max_tokens=120,
        )
        raw_keywords = [part.strip() for part in re.split(r"[,|\n]", response) if part.strip()]
        keywords = _dedupe(([target_role] if target_role.strip() else []) + raw_keywords + fallback_keywords)
        return keywords[:12]
    except Exception:
        return fallback_keywords[:12]


def _job_search_bundle(*, summary: str, target_role: str, location: str, prompt: str) -> dict[str, Any]:
    clean_location = location.strip() or "United Kingdom"
    keywords = _suggest_search_keywords(summary, target_role, prompt)
    search_query = ", ".join(keywords) or target_role.strip() or "Career role"

    linkedin_jobs: list[dict[str, Any]]
    indeed_jobs: list[dict[str, Any]]

    if has_apify_config():
        linkedin_live = False
        indeed_live = False

        try:
            linkedin_jobs = fetch_linkedin_jobs(search_query, location=clean_location, rows=16)
            if linkedin_jobs:
                linkedin_live = True
            else:
                linkedin_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)
        except Exception:
            linkedin_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)

        try:
            indeed_jobs = fetch_indeed_jobs(search_query, location=clean_location, rows=16)
            if indeed_jobs:
                indeed_live = True
            else:
                indeed_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)
        except Exception:
            indeed_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)

        live_sources = int(linkedin_live) + int(indeed_live)
        if live_sources == 2:
            mode = "live"
        elif live_sources == 1:
            mode = "mixed"
        else:
            mode = "fallback"
    else:
        linkedin_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)
        indeed_jobs = generate_demo_jobs(search_query, location=clean_location, rows=12)
        mode = "fallback"

    return {
        "keywords": search_query,
        "keyword_list": keywords[:12],
        "location": clean_location,
        "linkedin_jobs": linkedin_jobs,
        "indeed_jobs": indeed_jobs,
        "mode": mode,
    }


def _allowed_tools_for_inputs(job_description: str) -> list[str]:
    return [
        "profile_analysis",
        "target_role_inference",
        "ats_score",
        "job_search",
        "course_recommendations",
        "interview_plan",
        "interview_coaching",
        "verifier",
    ]


def _fallback_plan(prompt: str, job_description: str) -> list[dict[str, str]]:
    requested = prompt.lower()
    plan = [
        {"tool": "profile_analysis", "reason": "Build candidate context before taking action."},
        {"tool": "target_role_inference", "reason": "Infer the strongest role direction before ATS and job search."},
    ]
    if job_description.strip() or "ats" in requested or "job description" in requested or "apply" in requested or not requested:
        plan.append({"tool": "ats_score", "reason": "Score resume fit using the real JD when available, otherwise a provisional benchmark."})
    if "job" in requested or "career" in requested or "apply" in requested or not requested:
        plan.append({"tool": "job_search", "reason": "Find suitable role directions and openings."})
    if "skill" in requested or "course" in requested or "learn" in requested or not requested:
        plan.append({"tool": "course_recommendations", "reason": "Close missing skill gaps with free courses."})
    if "interview" in requested or "mock" in requested or not requested:
        plan.extend(
            [
                {"tool": "interview_plan", "reason": "Prepare adaptive interview questions."},
                {"tool": "interview_coaching", "reason": "Give spoken-answer strategy."},
            ]
        )
    plan.append({"tool": "verifier", "reason": "Check assumptions and produce next actions."})
    return plan


def _build_agent_plan(
    *,
    summary: str,
    resume_text: str,
    location: str,
    prompt: str,
    target_role: str,
    job_description: str,
    conversation: list[dict[str, str]],
) -> list[dict[str, str]]:
    fallback = _fallback_plan(prompt, job_description)
    if not has_openai_config():
        return fallback

    try:
        raw_response = ask_openai(
            f"""
You are the Planner Agent for a career assistant. Choose tools from this registry:
{json.dumps(TOOL_REGISTRY, indent=2)}

Return valid JSON only:
{{
  "plan": [
    {{"tool": "profile_analysis", "reason": "why this is needed"}}
  ]
}}

Rules:
- Use only registered tool names.
- Include verifier last.
- Use target_role_inference before ats_score or job_search whenever role direction is missing or weak.
- ats_score may use a real job description when supplied, otherwise it can score against a provisional benchmark generated by target_role_inference.
- Prefer 5-7 tool steps.

Candidate summary: {summary}
Resume text available: {bool(resume_text.strip())}
Target role: {target_role or "Any role"}
Location: {location}
Job description exists: {bool(job_description.strip())}
User goal: {prompt or "Run a complete career workflow."}
Recent conversation: {json.dumps(conversation[-4:])}
""".strip(),
            max_tokens=420,
        )
    except Exception:
        return fallback

    parsed = _extract_json_block(raw_response)
    raw_plan = parsed.get("plan") if parsed else None
    if not isinstance(raw_plan, list):
        return fallback

    allowed = set(_allowed_tools_for_inputs(job_description))
    cleaned: list[dict[str, str]] = []
    for item in raw_plan[:8]:
        if not isinstance(item, dict):
            continue
        tool = str(item.get("tool") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if tool in allowed and tool not in [step["tool"] for step in cleaned]:
            cleaned.append({"tool": tool, "reason": reason or TOOL_REGISTRY[tool]})

    selected_tools = [step["tool"] for step in cleaned]
    needs_role_context = any(tool in selected_tools for tool in ["ats_score", "job_search", "interview_plan"]) and not target_role.strip()
    if needs_role_context and "target_role_inference" not in selected_tools:
        cleaned.insert(1 if cleaned and cleaned[0]["tool"] == "profile_analysis" else 0, {
            "tool": "target_role_inference",
            "reason": "Infer a target role before downstream actions.",
        })

    if not cleaned or cleaned[-1]["tool"] != "verifier":
        cleaned = [step for step in cleaned if step["tool"] != "verifier"]
        cleaned.append({"tool": "verifier", "reason": "Validate the workflow output."})

    return cleaned if len(cleaned) >= 3 else fallback


def _run_tool(tool: str, context: dict[str, Any]) -> dict[str, Any]:
    summary = context["summary"]
    resume_text = context["resume_text"]
    prompt = context["prompt"]
    location = context["location"]
    target_role = context["target_role"]
    job_description = context["job_description"]

    if tool == "profile_analysis":
        insights = generate_resume_insights(resume_text or summary)
        role_keywords = suggest_job_keywords(f"{summary} {resume_text}")
        output = {
            "summary": insights.get("summary", summary),
            "gaps": insights.get("gaps", ""),
            "roadmap": insights.get("roadmap", ""),
            "role_keywords": role_keywords[:8],
        }
        context["profile_analysis"] = output
        return {"tool": tool, "status": "completed", "output": output}

    if tool == "target_role_inference":
        target_profile = derive_target_profile(
            summary=summary,
            resume_text=resume_text,
            preferred_role=target_role,
        )
        context["target_profile"] = target_profile
        context["benchmark_job_description"] = target_profile["job_description"]
        if not context["target_role"].strip():
            context["target_role"] = target_profile["target_role"]
        return {"tool": tool, "status": "completed", "output": target_profile}

    if tool == "ats_score":
        manual_description = job_description.strip()
        benchmark_description = str(context.get("benchmark_job_description", "")).strip()
        active_description = manual_description or benchmark_description
        active_role = context["target_role"].strip() or str(context.get("target_profile", {}).get("target_role", "")).strip()
        if not active_description:
            return {"tool": tool, "status": "skipped", "reason": "No job description or benchmark was available."}

        report = build_ats_report(
            {
                "resume_summary": summary,
                "resume_text": resume_text,
                "job_description": active_description,
                "target_role": active_role,
            }
        )
        ats_context = {
            "target_role": active_role or report.get("target_role", ""),
            "job_description": active_description,
            "source": "manual" if manual_description else "benchmark",
        }
        context["ats_report"] = report
        context["ats_context"] = ats_context
        return {"tool": tool, "status": "completed", "output": {"report": report, "context": ats_context}}

    if tool == "job_search":
        active_role = context["target_role"].strip() or str(context.get("target_profile", {}).get("target_role", "")).strip()
        jobs_report = _job_search_bundle(
            summary=summary,
            target_role=active_role,
            location=location,
            prompt=prompt,
        )
        context["jobs_report"] = jobs_report
        return {"tool": tool, "status": "completed", "output": jobs_report}

    if tool == "course_recommendations":
        missing_skills = _infer_missing_skills(summary, prompt, context.get("ats_report"))
        courses = recommend_youtube_courses(
            missing_skills=missing_skills,
            target_job_title=context["target_role"] or "target role",
            per_skill=2,
        )
        output = {
            "missing_skills": missing_skills,
            "courses": courses.get("recommendations", []),
        }
        context["course_recommendations"] = output
        return {"tool": tool, "status": "completed", "output": output}

    if tool == "interview_plan":
        active_role = context["target_role"].strip() or str(context.get("target_profile", {}).get("target_role", "")).strip()
        active_description = job_description.strip() or str(context.get("benchmark_job_description", "")).strip()
        profile = build_interview_profile(
            {
                "resume_summary": summary,
                "resume_text": resume_text,
                "target_role": active_role or "Any job interview",
                "job_description": active_description,
                "difficulty": "Medium",
                "interviewer_style": "Balanced",
            }
        )
        context["interview_profile"] = profile
        return {"tool": tool, "status": "completed", "output": profile}

    if tool == "interview_coaching":
        active_role = context["target_role"].strip() or str(context.get("target_profile", {}).get("target_role", "")).strip()
        active_description = job_description.strip() or str(context.get("benchmark_job_description", "")).strip()
        reply = fallback_interview_reply(summary, prompt or f"Prepare me for a {active_role or 'job'} interview.")
        if has_openai_config():
            try:
                reply = ask_openai(
                    f"""
You are an interview coach. Give concise practical coaching.
Candidate summary: {summary}
Target role: {active_role or "Any job"}
Job description: {active_description[:1800] or "Not supplied"}
User goal: {prompt or "Prepare for interview"}
Return 4 bullets and one opening mock interview question.
""".strip(),
                    max_tokens=350,
                )
            except Exception:
                pass
        output = {"coaching": reply}
        context["interview_coaching"] = output
        return {"tool": tool, "status": "completed", "output": output}

    if tool == "verifier":
        completed = [result["tool"] for result in context["tool_results"] if result.get("status") == "completed"]
        skipped = [result for result in context["tool_results"] if result.get("status") == "skipped"]
        input_gaps: list[str] = []
        ats_context = context.get("ats_context", {})

        if not resume_text.strip():
            input_gaps.append("Upload a full resume file for stronger evidence.")
        if not job_description.strip():
            input_gaps.append("Paste a real target job description to replace the provisional ATS benchmark.")
        if ats_context.get("source") == "benchmark":
            input_gaps.append("The current ATS score is benchmark-based, so treat it as directional until you paste the actual job posting.")
        if not context.get("jobs_report"):
            input_gaps.append("No job search results were produced. Rerun with a clearer role or location.")

        confidence = "high" if len(completed) >= 5 and not input_gaps else "medium" if len(completed) >= 3 else "low"
        output = {
            "completed_tools": completed,
            "skipped_tools": skipped,
            "confidence": confidence,
            "checks": [
                "The workflow selected tools based on available inputs.",
                "Recommendations are grounded in resume summary, inferred role direction, and ATS context.",
                "Missing inputs are surfaced before strong claims are presented as final.",
            ],
            "input_gaps": input_gaps,
            "ats_source": ats_context.get("source", "unavailable"),
        }
        context["verification"] = output
        return {"tool": tool, "status": "completed", "output": output}

    return {"tool": tool, "status": "skipped", "reason": "Unknown tool."}


def _result_output(tool_results: list[dict[str, Any]], tool_name: str) -> dict[str, Any]:
    for result in tool_results:
        if result.get("tool") == tool_name and isinstance(result.get("output"), dict):
            return result["output"]
    return {}


def _summarize_workflow(context: dict[str, Any]) -> dict[str, Any]:
    tool_results = context["tool_results"]
    ats = context.get("ats_report") or {}
    ats_context = context.get("ats_context") or {}
    interview_profile = context.get("interview_profile") or {}
    jobs_report = context.get("jobs_report") or {}
    profile_analysis = context.get("profile_analysis") or {}
    target_profile = context.get("target_profile") or {}

    priority_actions: list[str] = []
    if ats_context.get("source") == "benchmark":
        priority_actions.append("Paste the real job description to replace the provisional ATS benchmark before trusting the ATS score.")
    if ats.get("missing_keywords"):
        priority_actions.append(f"Add missing ATS keywords where truthful: {', '.join(ats['missing_keywords'][:5])}.")
    if profile_analysis.get("roadmap"):
        priority_actions.append(str(profile_analysis["roadmap"])[:220])
    if jobs_report.get("keyword_list"):
        priority_actions.append(f"Start applying across these role families: {', '.join(jobs_report['keyword_list'][:4])}.")
    course_output = _result_output(tool_results, "course_recommendations")
    if course_output.get("missing_skills"):
        priority_actions.append(f"Start with these skill gaps: {', '.join(course_output['missing_skills'][:4])}.")
    priority_actions.extend(
        [
            "Use one tailored resume version per target job family.",
            "Run a mock interview and score the latest answer after each response.",
        ]
    )

    deduped_actions = _dedupe(priority_actions)
    primary_role = context["target_role"] or target_profile.get("target_role") or ", ".join(suggest_job_keywords(context["summary"])[:3])

    return {
        "north_star": primary_role or "Target roles aligned to your resume.",
        "primary_role": primary_role,
        "ats_source": ats_context.get("source", "unavailable"),
        "priority_actions": deduped_actions[:6],
        "job_search_keywords": jobs_report.get("keyword_list", [])[:6],
        "next_best_step": deduped_actions[0] if deduped_actions else "Paste a real job description and continue refining the fit.",
        "interview_next_question": (interview_profile.get("question_bank") or [{}])[0].get(
            "question",
            "Tell me about yourself and why this role is a strong fit.",
        ),
        "tools_used": [result["tool"] for result in tool_results if result.get("status") == "completed"],
    }


def run_agentic_career_workflow(
    *,
    summary: str,
    resume_text: str = "",
    location: str = "United Kingdom",
    prompt: str = "",
    target_role: str = "",
    job_description: str = "",
    conversation: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    convo = conversation or []
    clean_summary = summary.strip() or "No resume summary provided yet."
    context: dict[str, Any] = {
        "summary": clean_summary,
        "resume_text": resume_text or "",
        "location": location.strip() or "United Kingdom",
        "prompt": prompt.strip(),
        "target_role": target_role.strip(),
        "job_description": job_description.strip(),
        "conversation": convo,
        "tool_results": [],
    }

    plan = _build_agent_plan(
        summary=clean_summary,
        resume_text=context["resume_text"],
        location=context["location"],
        prompt=context["prompt"],
        target_role=context["target_role"],
        job_description=context["job_description"],
        conversation=convo,
    )

    for step in plan:
        tool = step["tool"]
        if tool == "verifier":
            continue
        result = _run_tool(tool, context)
        context["tool_results"].append(result)

    verifier = _run_tool("verifier", context)
    context["tool_results"].append(verifier)

    return {
        "mode": "agentic-tool-router-openai" if has_openai_config() else "agentic-tool-router-fallback",
        "planner": {
            "goal": context["prompt"] or "Run a complete career workflow.",
            "available_tools": TOOL_REGISTRY,
            "plan": plan,
        },
        "tool_trace": context["tool_results"],
        "final_recommendation": _summarize_workflow(context),
        "verification": verifier.get("output", {}),
        "profile_analysis": context.get("profile_analysis", {}),
        "derived_target_profile": context.get("target_profile", {}),
        "ats_report": context.get("ats_report"),
        "ats_context": context.get("ats_context", {}),
        "jobs_report": context.get("jobs_report", {}),
        "course_recommendations": context.get("course_recommendations", {}),
        "interview_profile": context.get("interview_profile", {}),
    }
