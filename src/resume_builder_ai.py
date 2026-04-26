from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote_plus


KEYWORD_POOL = [
    "Python", "SQL", "Java", "JavaScript", "TypeScript", "C++", "C#", "R Programming",
    "HTML", "CSS", "React", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "Git", "GitHub", "Docker", "Kubernetes", "Linux", "AWS", "Azure", "Google Cloud",
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum", "JIRA", "Confluence",
    "Data Analysis", "Data Science", "Machine Learning", "Deep Learning", "Artificial Intelligence",
    "NLP", "Computer Vision", "Power BI", "Tableau", "Excel", "MySQL", "PostgreSQL",
    "MongoDB", "Snowflake", "Databricks", "Apache Spark", "Airflow", "Pandas", "NumPy",
    "TensorFlow", "PyTorch", "Statistics", "Forecasting", "A/B Testing",
    "Financial Analysis", "Financial Modelling", "Accounting", "Budgeting", "Compliance",
    "Risk Management", "Business Development", "Sales", "Stakeholder Management", "Project Management",
    "Marketing", "Digital Marketing", "SEO", "Content Marketing", "Google Analytics",
    "HR", "Recruitment", "Talent Acquisition", "Employee Relations",
    "Teaching", "Curriculum Development", "Lesson Planning", "Assessment",
    "Patient Care", "Healthcare", "Clinical Skills", "First Aid",
    "Legal Research", "Contract Drafting", "Employment Law", "GDPR",
    "CAD", "AutoCAD", "Quality Assurance", "Quality Control", "Lean", "Six Sigma",
    "Graphic Design", "Figma", "Adobe Photoshop", "Adobe Illustrator", "UX Design", "UI Design",
    "Customer Service", "Communication", "Leadership", "Problem Solving", "Research",
]

COURSE_DB: dict[str, list[dict[str, str]]] = {
    "Python": [
        {"title": "Python for Everybody", "provider": "Coursera", "url": "https://www.coursera.org/specializations/python", "cost": "Free to audit"},
        {"title": "Python Tutorial", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "cost": "Free"},
        {"title": "Python Full Course", "provider": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "cost": "Free"},
    ],
    "SQL": [
        {"title": "SQL for Data Science", "provider": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science", "cost": "Free to audit"},
        {"title": "Intro to SQL", "provider": "Kaggle", "url": "https://www.kaggle.com/learn/intro-to-sql", "cost": "Free"},
        {"title": "SQL Full Database Course", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "cost": "Free"},
    ],
    "Power BI": [
        {"title": "Power BI Guided Learning", "provider": "Microsoft", "url": "https://learn.microsoft.com/power-bi/", "cost": "Free"},
        {"title": "Power BI Full Course", "provider": "Simplilearn", "url": "https://www.youtube.com/watch?v=AGrl-H87pRU", "cost": "Free"},
        {"title": "Power BI Dashboard End-to-End Project", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=power+bi+dashboard+project", "cost": "Free"},
    ],
    "Tableau": [
        {"title": "Tableau Training", "provider": "Tableau", "url": "https://www.tableau.com/learn/training", "cost": "Free"},
        {"title": "Tableau Full Course", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=aHaOIvR00So", "cost": "Free"},
        {"title": "Tableau Dashboard Projects", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=tableau+dashboard+project", "cost": "Free"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "cost": "Free to audit"},
        {"title": "Machine Learning for Everybody", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg", "cost": "Free"},
        {"title": "Machine Learning Projects", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=machine+learning+projects", "cost": "Free"},
    ],
    "React": [
        {"title": "React Course", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/news/learn-react-course/", "cost": "Free"},
        {"title": "React Full Course", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "cost": "Free"},
        {"title": "React Project Tutorials", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=react+project+tutorial", "cost": "Free"},
    ],
    "AWS": [
        {"title": "AWS Cloud Practitioner Essentials", "provider": "AWS", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "cost": "Free"},
        {"title": "AWS Cloud Practitioner Full Course", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc", "cost": "Free"},
        {"title": "AWS Hands-On Labs", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=aws+hands+on+labs", "cost": "Free"},
    ],
    "Docker": [
        {"title": "Docker for Beginners", "provider": "freeCodeCamp", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo", "cost": "Free"},
        {"title": "Docker Getting Started", "provider": "Docker", "url": "https://docs.docker.com/get-started/", "cost": "Free"},
        {"title": "Docker Project Tutorials", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=docker+project+tutorial", "cost": "Free"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Course for Beginners", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=kubernetes+course+for+beginners", "cost": "Free"},
        {"title": "Kubernetes Learning Path", "provider": "Google Search", "url": "https://www.google.com/search?q=kubernetes+learning+path", "cost": "Varies"},
        {"title": "Kubernetes Hands-On Labs", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=kubernetes+hands+on+labs", "cost": "Free"},
    ],
    "Excel": [
        {"title": "Excel Skills for Business", "provider": "Coursera", "url": "https://www.coursera.org/specializations/excel", "cost": "Free to audit"},
        {"title": "Excel Full Course", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=excel+full+course", "cost": "Free"},
        {"title": "Excel Dashboard Tutorials", "provider": "YouTube", "url": "https://www.youtube.com/results?search_query=excel+dashboard+tutorial", "cost": "Free"},
    ],
    "default": [
        {"title": "LinkedIn Learning", "provider": "LinkedIn", "url": "https://www.linkedin.com/learning/", "cost": "Free trial"},
        {"title": "freeCodeCamp", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "cost": "Free"},
    ],
}

ROLE_REQUIRED_SKILLS = {
    "software": ["Python", "JavaScript", "React", "Git", "REST API", "SQL", "Agile"],
    "data analyst": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "Data Analysis"],
    "data scientist": ["Python", "Machine Learning", "SQL", "Statistics", "Deep Learning"],
    "devops": ["Docker", "Kubernetes", "AWS", "Linux", "Git"],
    "finance": ["Excel", "Financial Analysis", "Financial Modelling", "Accounting", "Budgeting"],
    "marketing": ["Digital Marketing", "SEO", "Content Marketing", "Google Analytics", "Communication"],
    "hr": ["Recruitment", "Talent Acquisition", "Employee Relations", "Communication"],
    "teaching": ["Teaching", "Lesson Planning", "Curriculum Development", "Assessment"],
    "healthcare": ["Patient Care", "Healthcare", "Clinical Skills", "Communication"],
    "default": ["Communication", "Problem Solving", "Stakeholder Management", "Project Management"],
}

INTERVIEW_QUESTIONS = {
    "software": [
        "Describe the most complex bug you fixed and how you approached it.",
        "How do you ensure code quality in a team environment?",
        "How would you design a new feature from scratch?",
    ],
    "data analyst": [
        "How have you cleaned and prepared messy data for analysis?",
        "How would you explain a complex insight to a non-technical stakeholder?",
        "What KPIs would you track in a dashboard for this role?",
    ],
    "finance": [
        "Walk me through how you would build a financial model.",
        "How do you ensure accuracy when working with financial data?",
        "Describe a time you found and resolved a discrepancy.",
    ],
    "marketing": [
        "Describe a campaign you planned or contributed to.",
        "How do you measure the success of a digital campaign?",
        "How do you identify the right audience for a campaign?",
    ],
    "default": [
        "Walk me through your background and why it fits this role.",
        "Describe a project where you made measurable impact.",
        "Tell me about a challenge you faced and how you solved it.",
    ],
}


def extract_jd_keywords(jd: str) -> list[str]:
    jd_lower = (jd or "").lower()
    found: list[str] = []
    for keyword in KEYWORD_POOL:
        pattern = r"(?<![a-z])" + re.escape(keyword.lower()) + r"(?![a-z])"
        if re.search(pattern, jd_lower):
            found.append(keyword)

    deduped: list[str] = []
    seen: set[str] = set()
    for keyword in found:
        normalized = keyword.lower()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(keyword)
    return deduped[:20]


def clean_skills(raw: str) -> list[str]:
    return [item.strip() for item in re.split(r"[,|\n;/]", raw) if item.strip()]


def match_skills(user_skills: list[str], jd_keywords: list[str]) -> tuple[list[str], list[str]]:
    lowered_user = {skill.lower(): skill for skill in user_skills}
    matched = [keyword for keyword in jd_keywords if keyword.lower() in lowered_user]
    missing = [keyword for keyword in jd_keywords if keyword.lower() not in lowered_user]
    return matched, missing


def get_match_level(score: int) -> tuple[str, str, str]:
    if score >= 85:
        return "Excellent Match", "#1d7a56", "Strong fit"
    if score >= 70:
        return "Good Match", "#2c5282", "Competitive"
    if score >= 50:
        return "Moderate Match", "#b7791f", "Improve key gaps"
    return "Needs Work", "#b91c1c", "Major gaps"


def _detect_role_key(job_title: str, jd_text: str = "") -> str:
    combined = f"{job_title} {jd_text}".lower()
    if any(item in combined for item in ["data analyst", "bi analyst", "analytics"]):
        return "data analyst"
    if any(item in combined for item in ["data scientist", "machine learning", "ml engineer"]):
        return "data scientist"
    if any(item in combined for item in ["devops", "platform engineer", "site reliability", "cloud engineer"]):
        return "devops"
    if any(item in combined for item in ["finance", "financial", "accountant", "accounting"]):
        return "finance"
    if any(item in combined for item in ["marketing", "seo", "content", "campaign"]):
        return "marketing"
    if any(item in combined for item in ["hr", "recruit", "talent", "people partner"]):
        return "hr"
    if any(item in combined for item in ["teacher", "teaching", "lecturer", "curriculum"]):
        return "teaching"
    if any(item in combined for item in ["nurse", "healthcare", "patient", "clinical"]):
        return "healthcare"
    if any(item in combined for item in ["software", "developer", "engineer", "frontend", "backend", "full stack", "react", "python"]):
        return "software"
    return "default"


def get_role_required_skills(job_title: str, jd_text: str = "") -> list[str]:
    return ROLE_REQUIRED_SKILLS.get(_detect_role_key(job_title, jd_text), ROLE_REQUIRED_SKILLS["default"])


def get_courses_for_skill(skill: str) -> list[dict[str, str]]:
    for key, value in COURSE_DB.items():
        if key == "default":
            continue
        if key.lower() in skill.lower() or skill.lower() in key.lower():
            return _expand_learning_resources(skill, value)
    return _expand_learning_resources(skill, COURSE_DB["default"])


def _expand_learning_resources(skill: str, base_courses: list[dict[str, str]]) -> list[dict[str, str]]:
    query = quote_plus(f"{skill} tutorial")
    youtube_query = quote_plus(f"{skill} full course")
    extras = [
        {
            "title": f"{skill} YouTube Playlist",
            "provider": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={query}",
            "cost": "Free",
        },
        {
            "title": f"{skill} Full Course Videos",
            "provider": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={youtube_query}",
            "cost": "Free",
        },
        {
            "title": f"{skill} Learning Path",
            "provider": "Google Search",
            "url": f"https://www.google.com/search?q={quote_plus(f'{skill} certification learning path')}",
            "cost": "Varies",
        },
        {
            "title": f"{skill} Projects and Practice",
            "provider": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(f'{skill} project tutorial')}",
            "cost": "Free",
        },
        {
            "title": f"{skill} Interview Questions",
            "provider": "YouTube",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(f'{skill} interview questions')}",
            "cost": "Free",
        },
    ]

    merged: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for course in [*base_courses, *extras]:
        url = course.get("url", "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        merged.append(course)
    return merged[:7]


def get_interview_questions(jd_text: str, job_title: str) -> list[str]:
    role_key = _detect_role_key(job_title, jd_text)
    return INTERVIEW_QUESTIONS.get(role_key, INTERVIEW_QUESTIONS["default"])


def suggest_roles(user_skills: list[str], jd_keywords: list[str], target_job_title: str = "") -> list[str]:
    combined = " ".join(user_skills + jd_keywords + [target_job_title]).lower()
    roles: list[str] = []
    if any(term in combined for term in ["python", "react", "api", "software", "javascript"]):
        roles.extend(["Software Engineer", "Backend Developer", "Frontend Developer"])
    if any(term in combined for term in ["sql", "power bi", "tableau", "data analysis", "analytics"]):
        roles.extend(["Data Analyst", "Business Analyst"])
    if any(term in combined for term in ["machine learning", "deep learning", "nlp"]):
        roles.extend(["Machine Learning Engineer", "Data Scientist"])
    if any(term in combined for term in ["aws", "docker", "kubernetes", "linux"]):
        roles.extend(["DevOps Engineer", "Cloud Engineer"])
    if any(term in combined for term in ["marketing", "seo", "content"]):
        roles.extend(["Digital Marketing Specialist", "Content Strategist"])
    if any(term in combined for term in ["finance", "accounting", "budgeting"]):
        roles.extend(["Financial Analyst", "Accountant"])
    if not roles:
        roles = [target_job_title.strip() or "Professional Associate", "Operations Analyst", "Project Coordinator"]
    deduped: list[str] = []
    seen: set[str] = set()
    for role in roles:
        lowered = role.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(role)
    return deduped[:5]


def get_strength_breakdown(resume_text: str, matched: list[str], jd_keywords: list[str]) -> dict[str, int]:
    sections = {
        "summary": int("summary" in resume_text.lower() or "profile" in resume_text.lower()),
        "skills": int("skills" in resume_text.lower()),
        "projects": int("projects" in resume_text.lower()),
        "education": int("education" in resume_text.lower()),
        "matched_skills": len(matched),
        "missing_skills": max(0, len(jd_keywords) - len(matched)),
    }
    return sections


def get_improvement_tips(missing: list[str], matched: list[str]) -> list[str]:
    tips: list[str] = []
    if missing:
        tips.append(f"Add proof for missing skills such as {', '.join(missing[:4])}.")
    if matched:
        tips.append(f"Move strong signals like {', '.join(matched[:3])} higher in the summary and skills section.")
    tips.extend([
        "Rewrite recent bullets using measurable outcomes and clear action verbs.",
        "Keep role-specific keywords aligned with the job description wording.",
        "Use standard section headings so recruiters and parsers can scan quickly.",
    ])
    return tips[:5]


def generate_cover_letter(name: str, job_title: str, matched_skills: list[str], experience: str, education: str, jd_text: str) -> str:
    skills_text = ", ".join(matched_skills[:6]) if matched_skills else "relevant technical and professional strengths"
    experience_line = experience.strip().splitlines()[0].strip() if experience.strip() else "hands-on project and work experience"
    education_line = education.strip().splitlines()[0].strip() if education.strip() else "a strong academic foundation"
    return (
        f"Dear Hiring Manager,\n\n"
        f"I am applying for the {job_title or 'target role'} position. My background combines {education_line} with {experience_line}. "
        f"I can contribute through strengths in {skills_text}, and I am particularly interested in this opportunity because it aligns with my recent work and growth areas.\n\n"
        f"My experience has prepared me to deliver structured work, communicate clearly with stakeholders, and learn quickly in changing environments. "
        f"I would welcome the opportunity to contribute to your team and discuss how my profile aligns with your needs.\n\n"
        f"Sincerely,\n{name or 'Candidate'}"
    )


def generate_linkedin_headline(job_title: str, skills: list[str], education: str) -> str:
    lead = job_title.strip() or "Aspiring Professional"
    skill_text = " | ".join(skills[:3]) if skills else "Problem Solving | Communication"
    education_hint = education.strip().splitlines()[0].strip() if education.strip() else "Open to opportunities"
    return f"{lead} | {skill_text} | {education_hint[:60]}"


def _extract_resume_skills(resume_text: str, resume_summary: str) -> list[str]:
    combined = f"{resume_text}\n{resume_summary}".lower()
    detected = [keyword for keyword in KEYWORD_POOL if re.search(r"(?<![a-z])" + re.escape(keyword.lower()) + r"(?![a-z])", combined)]
    if not detected:
        detected = clean_skills(resume_summary)
    deduped: list[str] = []
    seen: set[str] = set()
    for skill in detected:
        lowered = skill.lower()
        if lowered not in seen:
            seen.add(lowered)
            deduped.append(skill)
    return deduped[:18]


def build_resume_builder_report(payload: dict[str, Any]) -> dict[str, Any]:
    resume_text = (payload.get("resume_text") or "").strip()
    resume_summary = (payload.get("resume_summary") or "").strip()
    job_description = (payload.get("job_description") or "").strip()
    target_role = (payload.get("target_role") or "").strip()

    if not resume_text and not resume_summary:
        raise ValueError("Resume text is required before building a resume plan.")

    effective_role = target_role or "Target role"
    jd_keywords = extract_jd_keywords(job_description) if job_description else get_role_required_skills(effective_role, job_description)
    if not jd_keywords:
        jd_keywords = get_role_required_skills(effective_role, job_description)

    user_skills = _extract_resume_skills(resume_text, resume_summary)
    matched, missing = match_skills(user_skills, jd_keywords)
    denominator = max(len(jd_keywords), 1)
    score = round((len(matched) / denominator) * 100)
    score = max(18, min(96, score))
    match_level, level_color, level_hint = get_match_level(score)

    required_skills = get_role_required_skills(effective_role, job_description)
    learning_plan = []
    for skill in (missing[:6] or required_skills[:6]):
        learning_plan.append({
            "skill": skill,
            "courses": get_courses_for_skill(skill),
        })

    suggested_roles = suggest_roles(user_skills, jd_keywords, effective_role)
    interview_questions = get_interview_questions(job_description, effective_role)
    resume_lines = [line.strip("-• ").strip() for line in resume_text.splitlines() if line.strip()]
    experience_seed = next((line for line in resume_lines if len(line.split()) > 5), resume_summary)
    education_seed = next((line for line in resume_lines if "university" in line.lower() or "college" in line.lower() or "bachelor" in line.lower() or "master" in line.lower()), "")
    cover_letter = generate_cover_letter(
        payload.get("candidate_name", ""),
        effective_role,
        matched or user_skills[:6],
        experience_seed,
        education_seed,
        job_description,
    )
    headline = generate_linkedin_headline(effective_role, matched or user_skills[:4], education_seed)

    return {
        "score": score,
        "match_level": match_level,
        "level_color": level_color,
        "level_hint": level_hint,
        "target_role": effective_role,
        "job_description_keywords": jd_keywords,
        "matched_skills": matched,
        "missing_skills": missing,
        "user_skills": user_skills,
        "required_skills": required_skills,
        "suggested_roles": suggested_roles,
        "strength_breakdown": get_strength_breakdown(resume_text, matched, jd_keywords),
        "improvement_tips": get_improvement_tips(missing, matched),
        "learning_plan": learning_plan,
        "interview_questions": interview_questions,
        "linkedin_headline": headline,
        "cover_letter": cover_letter,
    }
