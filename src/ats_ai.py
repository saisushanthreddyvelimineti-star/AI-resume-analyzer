from __future__ import annotations

import csv
import io
import re
from typing import Any


KEYWORD_LIBRARY: dict[str, dict[str, Any]] = {
    "Python": {"aliases": ["python", "python3"], "category": "technical"},
    "Java": {"aliases": ["java"], "category": "technical"},
    "C++": {"aliases": ["c++", "cpp"], "category": "technical"},
    "C#": {"aliases": ["c#", "csharp"], "category": "technical"},
    "JavaScript": {"aliases": ["javascript", "js"], "category": "technical"},
    "TypeScript": {"aliases": ["typescript", "ts"], "category": "technical"},
    "React": {"aliases": ["react", "reactjs", "react.js"], "category": "technical"},
    "Node.js": {"aliases": ["node.js", "nodejs"], "category": "technical"},
    "Express.js": {"aliases": ["express", "express.js"], "category": "technical"},
    "FastAPI": {"aliases": ["fastapi"], "category": "technical"},
    "Django": {"aliases": ["django"], "category": "technical"},
    "Flask": {"aliases": ["flask"], "category": "technical"},
    "HTML": {"aliases": ["html", "html5"], "category": "technical"},
    "CSS": {"aliases": ["css", "css3"], "category": "technical"},
    "Tailwind CSS": {"aliases": ["tailwind", "tailwind css"], "category": "technical"},
    "Bootstrap": {"aliases": ["bootstrap"], "category": "technical"},
    "SQL": {"aliases": ["sql", "structured query language"], "category": "technical"},
    "PostgreSQL": {"aliases": ["postgresql", "postgres"], "category": "technical"},
    "MySQL": {"aliases": ["mysql"], "category": "technical"},
    "MongoDB": {"aliases": ["mongodb", "mongo db"], "category": "technical"},
    "REST APIs": {"aliases": ["rest api", "restful api", "rest APIs".lower()], "category": "technical"},
    "GraphQL": {"aliases": ["graphql"], "category": "technical"},
    "Microservices": {"aliases": ["microservices", "microservice"], "category": "technical"},
    "Docker": {"aliases": ["docker"], "category": "technical"},
    "Kubernetes": {"aliases": ["kubernetes", "k8s"], "category": "technical"},
    "Git": {"aliases": ["git", "github", "gitlab"], "category": "technical"},
    "CI/CD": {"aliases": ["ci/cd", "ci cd", "continuous integration", "continuous delivery"], "category": "technical"},
    "AWS": {"aliases": ["aws", "amazon web services"], "category": "technical"},
    "Azure": {"aliases": ["azure", "microsoft azure"], "category": "technical"},
    "Google Cloud": {"aliases": ["google cloud", "gcp"], "category": "technical"},
    "Linux": {"aliases": ["linux"], "category": "technical"},
    "Testing": {"aliases": ["testing", "unit testing", "integration testing"], "category": "technical"},
    "PyTest": {"aliases": ["pytest", "py test"], "category": "technical"},
    "Jest": {"aliases": ["jest"], "category": "technical"},
    "Selenium": {"aliases": ["selenium"], "category": "technical"},
    "Machine Learning": {"aliases": ["machine learning", "ml"], "category": "technical"},
    "Deep Learning": {"aliases": ["deep learning"], "category": "technical"},
    "NLP": {"aliases": ["nlp", "natural language processing"], "category": "technical"},
    "Computer Vision": {"aliases": ["computer vision"], "category": "technical"},
    "LLMs": {"aliases": ["llm", "llms", "large language model", "large language models"], "category": "technical"},
    "Prompt Engineering": {"aliases": ["prompt engineering", "prompt design"], "category": "technical"},
    "Data Analysis": {"aliases": ["data analysis", "data analytics", "analytics"], "category": "technical"},
    "Data Visualization": {"aliases": ["data visualization", "visualisation"], "category": "technical"},
    "Power BI": {"aliases": ["power bi"], "category": "technical"},
    "Tableau": {"aliases": ["tableau"], "category": "technical"},
    "Excel": {"aliases": ["excel", "microsoft excel"], "category": "technical"},
    "Pandas": {"aliases": ["pandas"], "category": "technical"},
    "NumPy": {"aliases": ["numpy"], "category": "technical"},
    "ETL": {"aliases": ["etl"], "category": "technical"},
    "Apache Spark": {"aliases": ["spark", "apache spark"], "category": "technical"},
    "Airflow": {"aliases": ["airflow", "apache airflow"], "category": "technical"},
    "Agile": {"aliases": ["agile"], "category": "soft"},
    "Scrum": {"aliases": ["scrum"], "category": "soft"},
    "Communication": {"aliases": ["communication", "communicate"], "category": "soft"},
    "Leadership": {"aliases": ["leadership", "leading teams"], "category": "soft"},
    "Stakeholder Management": {"aliases": ["stakeholder management", "stakeholder engagement"], "category": "soft"},
    "Problem Solving": {"aliases": ["problem solving", "problem-solving"], "category": "soft"},
    "Project Management": {"aliases": ["project management", "project delivery"], "category": "soft"},
    "Customer Service": {"aliases": ["customer service"], "category": "domain"},
    "Sales": {"aliases": ["sales"], "category": "domain"},
    "CRM": {"aliases": ["crm"], "category": "domain"},
    "Digital Marketing": {"aliases": ["digital marketing", "marketing"], "category": "domain"},
    "SEO": {"aliases": ["seo", "search engine optimization"], "category": "domain"},
    "Content Marketing": {"aliases": ["content marketing", "content strategy"], "category": "domain"},
    "Finance": {"aliases": ["finance", "financial"], "category": "domain"},
    "Accounting": {"aliases": ["accounting", "bookkeeping"], "category": "domain"},
    "Payroll": {"aliases": ["payroll"], "category": "domain"},
    "Budgeting": {"aliases": ["budgeting", "budget management"], "category": "domain"},
    "Risk Management": {"aliases": ["risk management", "risk"], "category": "domain"},
    "Healthcare": {"aliases": ["healthcare"], "category": "domain"},
    "Patient Care": {"aliases": ["patient care"], "category": "domain"},
    "Clinical": {"aliases": ["clinical"], "category": "domain"},
    "Teaching": {"aliases": ["teaching"], "category": "domain"},
    "Curriculum": {"aliases": ["curriculum"], "category": "domain"},
    "Lesson Planning": {"aliases": ["lesson planning"], "category": "domain"},
    "Assessment": {"aliases": ["assessment"], "category": "domain"},
    "Compliance": {"aliases": ["compliance"], "category": "domain"},
    "Operations": {"aliases": ["operations"], "category": "domain"},
    "Administration": {"aliases": ["administration", "administrative"], "category": "domain"},
    "Scheduling": {"aliases": ["scheduling"], "category": "domain"},
    "Research": {"aliases": ["research"], "category": "domain"},
    "Writing": {"aliases": ["writing", "technical writing"], "category": "domain"},
}

ROLE_LIBRARY = [
    "Full Stack Developer",
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "React Developer",
    "Python Developer",
    "Data Analyst",
    "Business Analyst",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Project Manager",
    "Marketing Coordinator",
    "Healthcare Assistant",
    "Teacher",
    "Accountant",
]

GENERIC_SINGLE_WORDS = {
    "seeking",
    "ideal",
    "candidate",
    "successful",
    "strong",
    "solid",
    "excellent",
    "demonstrated",
    "preferred",
    "required",
    "responsibilities",
    "responsibility",
    "requirements",
    "ability",
    "abilities",
    "knowledge",
    "proficient",
    "proficiency",
    "familiarity",
    "experience",
    "experienced",
    "skills",
    "skill",
    "background",
    "role",
    "job",
    "position",
    "opportunity",
    "team",
    "teams",
    "company",
    "environment",
    "development",
    "developing",
    "building",
    "working",
    "supporting",
    "using",
    "preferred",
    "plus",
    "must",
    "should",
    "will",
    "can",
    "have",
    "has",
    "our",
    "your",
    "their",
}

TRIGGER_PATTERNS = [
    r"(?:experience with|hands-on experience with|proficiency in|proficient in|knowledge of|familiarity with|expertise in|skilled in|skills in|background in|working with|using|required skills include|requirements include|must have|nice to have|preferred skills include|technologies include)\s+([^.:\n;]+)",
]

ACTION_VERBS = [
    "built",
    "developed",
    "designed",
    "implemented",
    "delivered",
    "launched",
    "improved",
    "optimized",
    "analysed",
    "analyzed",
    "led",
    "created",
    "deployed",
    "automated",
    "reduced",
    "increased",
]

RESUME_SECTION_HINTS = [
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]


ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, metadata in KEYWORD_LIBRARY.items():
    for alias in metadata["aliases"]:
        normalized = re.sub(r"[^a-z0-9+#/.\- ]", "", alias.lower()).strip()
        ALIAS_TO_CANONICAL[normalized] = canonical
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical


def _normalize_token(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#/.\- ]", " ", text.lower())).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"
    return bool(re.search(pattern, text))


def _extract_known_keywords(text: str) -> list[str]:
    normalized_text = _normalize_token(text)
    found: list[str] = []
    for canonical, metadata in KEYWORD_LIBRARY.items():
        if any(_contains_phrase(normalized_text, _normalize_token(alias)) for alias in metadata["aliases"]):
            found.append(canonical)
    return found


def _extract_role_titles(text: str, target_role: str = "") -> list[str]:
    normalized_text = _normalize_token(f"{target_role}\n{text}")
    found = [role for role in ROLE_LIBRARY if _contains_phrase(normalized_text, role.lower())]
    if target_role.strip() and target_role.strip() not in found:
        found.insert(0, target_role.strip())
    return list(dict.fromkeys(found))


def _split_candidates(text: str) -> list[str]:
    chunks = re.split(r",|/|;|\band\b|\bor\b", text)
    return [chunk.strip(" .:-") for chunk in chunks if chunk.strip(" .:-")]


def _map_candidate_to_keyword(candidate: str) -> str | None:
    normalized = _normalize_token(candidate)
    if not normalized:
        return None
    if normalized in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[normalized]

    if normalized in GENERIC_SINGLE_WORDS:
        return None

    words = normalized.split()
    if len(words) == 1 and words[0] in GENERIC_SINGLE_WORDS:
        return None
    if len(words) > 4:
        return None
    if all(word in GENERIC_SINGLE_WORDS for word in words):
        return None

    # Unknown single-word tokens are usually noise in ATS matching unless covered by the canonical alias map.
    if len(words) == 1:
        return None
    if 2 <= len(words) <= 4:
        return " ".join(word.upper() if len(word) <= 4 and word.isalpha() else word.title() for word in words)
    return None


def _extract_trigger_keywords(text: str) -> list[str]:
    found: list[str] = []
    for pattern in TRIGGER_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            segment = match.group(1)
            for candidate in _split_candidates(segment):
                mapped = _map_candidate_to_keyword(candidate)
                if mapped:
                    found.append(mapped)
    return found


def _extract_acronyms(text: str) -> list[str]:
    acronyms = re.findall(r"\b[A-Z][A-Z0-9/+.-]{1,8}\b", text)
    found: list[str] = []
    for acronym in acronyms:
        mapped = _map_candidate_to_keyword(acronym)
        if mapped:
            found.append(mapped)
    return found


def _extract_keywords(text: str, *, target_role: str = "") -> dict[str, Any]:
    known = _extract_known_keywords(text)
    triggered = _extract_trigger_keywords(text)
    acronyms = _extract_acronyms(text)
    roles = _extract_role_titles(text, target_role)

    ordered = list(dict.fromkeys([*known, *triggered, *acronyms]))
    precise_keywords = [keyword for keyword in ordered if keyword not in roles and keyword not in ROLE_LIBRARY]

    categories = {
        "technical": [keyword for keyword in precise_keywords if KEYWORD_LIBRARY.get(keyword, {}).get("category") == "technical"],
        "domain": [keyword for keyword in precise_keywords if KEYWORD_LIBRARY.get(keyword, {}).get("category") == "domain"],
        "soft": [keyword for keyword in precise_keywords if KEYWORD_LIBRARY.get(keyword, {}).get("category") == "soft"],
        "other": [
            keyword
            for keyword in precise_keywords
            if keyword not in KEYWORD_LIBRARY or KEYWORD_LIBRARY.get(keyword, {}).get("category") not in {"technical", "domain", "soft"}
        ],
    }
    return {
        "keywords": precise_keywords[:24],
        "roles": roles[:3],
        "categories": categories,
    }


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9+#.\-/]{1,}", text)}


def _canonical_token(token: str) -> str:
    cleaned = token.lower().replace(".", "").replace("-", "").replace("/", "")
    if cleaned.endswith("ies") and len(cleaned) > 4:
        return f"{cleaned[:-3]}y"
    if cleaned.endswith("s") and len(cleaned) > 4:
        return cleaned[:-1]
    return cleaned


def _canonical_tokens(text: str) -> set[str]:
    return {_canonical_token(token) for token in _tokens(text)}


def _keyword_present(keyword: str, resume_text: str, resume_tokens: set[str], resume_keywords: set[str]) -> bool:
    if keyword in resume_keywords:
        return True

    keyword_lower = keyword.lower()
    if re.search(rf"\b{re.escape(keyword_lower)}\b", resume_text):
        return True

    keyword_tokens = {_canonical_token(token) for token in re.findall(r"[A-Za-z0-9+#.\-/]+", keyword)}
    if not keyword_tokens:
        return False
    if len(keyword_tokens) == 1:
        return next(iter(keyword_tokens)) in resume_tokens
    return len(keyword_tokens & resume_tokens) / len(keyword_tokens) >= 0.75


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(term.lower())}\b", text) for term in terms)


def _field_from_keywords(keywords: list[str], target_role: str) -> str:
    role_text = target_role.lower()
    text = " ".join(keywords + [target_role]).lower()
    if _contains_any(role_text, ["backend", "software engineer", "python developer", "java developer", "api developer"]):
        return "Backend Development"
    if _contains_any(role_text, ["frontend", "react", "ui engineer", "web developer"]):
        return "Frontend Development"
    if _contains_any(role_text, ["full stack", "full-stack"]):
        return "Full Stack Development"
    if _contains_any(role_text, ["data analyst", "business analyst", "analytics", "bi analyst"]):
        return "Data Analytics"
    if _contains_any(role_text, ["machine learning engineer", "ml engineer", "ai engineer"]):
        return "AI / Machine Learning"
    if _contains_any(role_text, ["devops", "cloud engineer", "platform engineer"]):
        return "Cloud / DevOps"
    if _contains_any(role_text, ["marketing", "communications", "content", "social media"]):
        return "Marketing / Communications"
    if _contains_any(role_text, ["healthcare", "nurse", "clinical", "care assistant"]):
        return "Healthcare"
    if _contains_any(role_text, ["finance", "accounting", "bookkeeper", "payroll"]):
        return "Finance / Accounting"
    if _contains_any(role_text, ["teacher", "teaching", "education"]):
        return "Education"
    if _contains_any(role_text, ["operations", "administrator", "coordinator", "project manager"]):
        return "Operations / Administration"

    if _contains_any(text, ["machine learning", "deep learning", "nlp", "computer vision", "llms"]):
        return "AI / Machine Learning"
    if _contains_any(text, ["data analysis", "sql", "power bi", "tableau", "analytics"]):
        return "Data Analytics"
    if _contains_any(text, ["react", "javascript", "typescript", "html", "css"]):
        return "Frontend Development"
    if _contains_any(text, ["python", "fastapi", "django", "flask", "rest apis", "microservices"]):
        return "Backend Development"
    if _contains_any(text, ["docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd"]):
        return "Cloud / DevOps"
    if _contains_any(text, ["marketing", "seo", "content marketing", "crm"]):
        return "Marketing / Communications"
    if _contains_any(text, ["finance", "accounting", "bookkeeping", "payroll", "budgeting"]):
        return "Finance / Accounting"
    if _contains_any(text, ["healthcare", "patient care", "clinical"]):
        return "Healthcare"
    if _contains_any(text, ["teaching", "curriculum", "lesson planning", "assessment"]):
        return "Education"
    return target_role or "Software / Technology"


def _weighted_score(jd_keywords: list[str], matched: list[str], category_lookup: dict[str, str]) -> float:
    weights = {"technical": 1.0, "domain": 0.85, "soft": 0.55, "other": 0.7}
    total = sum(weights.get(category_lookup.get(keyword, "other"), 0.7) for keyword in jd_keywords)
    if total <= 0:
        return 0.0
    matched_weight = sum(weights.get(category_lookup.get(keyword, "other"), 0.7) for keyword in matched)
    return matched_weight / total


def _resume_evidence_score(resume_text: str) -> float:
    lowered = resume_text.lower()
    metric_hits = len(re.findall(r"\b\d+(?:\.\d+)?%?|\b\d+[xkmb]?\b", lowered))
    action_hits = sum(lowered.count(verb) for verb in ACTION_VERBS)
    section_hits = sum(1 for hint in RESUME_SECTION_HINTS if hint in lowered)
    score = min(1.0, metric_hits / 5) * 0.45 + min(1.0, action_hits / 6) * 0.35 + min(1.0, section_hits / 4) * 0.20
    return max(0.0, min(1.0, score))


def _resume_lines(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", line).strip(" -\t•")
        for line in re.split(r"[\r\n]+", text)
        if re.sub(r"\s+", " ", line).strip(" -\t•")
    ]


def _find_keyword_evidence(keyword: str, resume_text: str) -> str:
    lines = _resume_lines(resume_text)
    aliases = [_normalize_token(keyword)] + [
        _normalize_token(alias)
        for alias in KEYWORD_LIBRARY.get(keyword, {}).get("aliases", [])
    ]
    for line in lines:
        normalized_line = _normalize_token(line)
        if any(alias and _contains_phrase(normalized_line, alias) for alias in aliases):
            return line[:180]
    return ""


def _ats_rating(score: int) -> str:
    if score >= 82:
        return "Strong"
    if score >= 66:
        return "Good"
    if score >= 48:
        return "Moderate"
    return "Needs work"


def _resource_links(field: str, missing_keywords: list[str]) -> list[dict[str, str]]:
    search_terms = missing_keywords[:3] or [field]
    search = "+".join(term.replace(" ", "+") for term in search_terms)
    return [
        {
            "title": f"Role learning path for {field}",
            "type": "Roadmap",
            "url": f"https://www.google.com/search?q={field.replace(' ', '+')}+career+roadmap+skills",
            "why": "Use this to structure the skill path, certifications, and portfolio evidence.",
        },
        {
            "title": "Coursera courses",
            "type": "Course",
            "url": f"https://www.coursera.org/search?query={search.replace(' ', '%20')}",
            "why": "Use guided courses or certificates for the highest-priority missing skills.",
        },
        {
            "title": "edX courses",
            "type": "Course",
            "url": f"https://www.edx.org/search?q={search.replace(' ', '%20')}",
            "why": "Useful for fundamentals and professional credentials around missing requirements.",
        },
        {
            "title": "LinkedIn Learning search",
            "type": "Course",
            "url": f"https://www.linkedin.com/learning/search?keywords={search.replace(' ', '%20')}",
            "why": "Useful for short role-specific upskilling before applications.",
        },
        {
            "title": "YouTube full-course search",
            "type": "Free Course",
            "url": f"https://www.youtube.com/results?search_query={search.replace(' ', '+')}+full+course",
            "why": "Quick free learning resources to close the most visible gaps.",
        },
        {
            "title": "Resume keyword examples",
            "type": "Resume",
            "url": f"https://www.google.com/search?q={field.replace(' ', '+')}+resume+keywords+examples",
            "why": "Use this to phrase truthful experience in ATS-friendly language.",
        },
    ]


def _profile_actions(
    *,
    matched: list[str],
    missing: list[str],
    technical_missing: list[str],
    domain_missing: list[str],
    target_role: str,
    resume_text: str,
) -> list[str]:
    actions: list[str] = []
    if technical_missing:
        actions.append(
            f"Add direct evidence for these core technical requirements: {', '.join(technical_missing[:4])}. Use projects, tools, or work examples."
        )
    if domain_missing:
        actions.append(
            f"Show role-specific exposure to {', '.join(domain_missing[:3])} so the profile looks closer to the job context."
        )
    if missing and not technical_missing and not domain_missing:
        actions.append(
            f"Cover these missing requirements more clearly and truthfully: {', '.join(missing[:4])}."
        )

    lowered_resume = resume_text.lower()
    if target_role.strip() and target_role.lower() not in lowered_resume:
        actions.append(f"Align the resume headline and summary to the target role: {target_role}.")
    if _resume_evidence_score(resume_text) < 0.45:
        actions.append("Rewrite 3 to 5 bullets with measurable outcomes, metrics, and action verbs.")
    if "skills" not in lowered_resume:
        actions.append("Add a clear Skills section so ATS systems can see tools and technologies quickly.")
    if matched:
        actions.append(
            f"Move matched strengths like {', '.join(matched[:3])} higher in the summary, skills, or recent project bullets."
        )

    actions.append("Use exact section names: Skills, Experience, Projects, Education, Certifications.")
    return list(dict.fromkeys(actions))[:5]


def _stronger_resume_bullets(field: str, matched: list[str], missing: list[str]) -> list[str]:
    anchor = matched[:3] or missing[:3] or [field]
    return [
        f"Delivered a {field.lower()} outcome using {', '.join(anchor[:3])}, improving speed, quality, or efficiency with measurable impact.",
        f"Built and shipped a project using {', '.join(anchor[:2])}, translating business requirements into a production-ready result.",
        "Collaborated with stakeholders, clarified requirements, and documented outcomes with clear ownership and results.",
    ]


def build_ats_report(payload: dict[str, Any]) -> dict[str, Any]:
    resume_text = payload.get("resume_text", "") or payload.get("resume_summary", "")
    resume_summary = payload.get("resume_summary", "")
    job_description = payload.get("job_description", "")
    target_role = payload.get("target_role", "")

    if not resume_text.strip() and not resume_summary.strip():
        raise ValueError("Resume text is required before ATS scoring.")
    if not job_description.strip():
        raise ValueError("Paste a target job description before ATS scoring.")

    combined_resume = f"{resume_text}\n{resume_summary}".strip()
    jd_extracted = _extract_keywords(job_description, target_role=target_role)
    resume_extracted = _extract_keywords(combined_resume)

    jd_keywords = jd_extracted["keywords"]
    if not jd_keywords:
        raise ValueError("The job description did not contain enough recognizable role keywords to score against.")

    category_lookup = {}
    for category, items in jd_extracted["categories"].items():
        for item in items:
            category_lookup[item] = category

    resume_lower = combined_resume.lower()
    resume_tokens = _canonical_tokens(combined_resume)
    resume_keyword_set = set(resume_extracted["keywords"])

    matched = [keyword for keyword in jd_keywords if _keyword_present(keyword, resume_lower, resume_tokens, resume_keyword_set)]
    missing = [keyword for keyword in jd_keywords if keyword not in matched]

    inferred_roles = jd_extracted["roles"]
    effective_target_role = target_role.strip() or (inferred_roles[0] if inferred_roles else "")
    field = _field_from_keywords(jd_keywords, effective_target_role)

    technical_missing = [keyword for keyword in missing if category_lookup.get(keyword) == "technical"]
    domain_missing = [keyword for keyword in missing if category_lookup.get(keyword) == "domain"]
    keyword_score = _weighted_score(jd_keywords, matched, category_lookup)
    keyword_coverage = len(matched) / max(len(jd_keywords), 1)
    evidence_score = _resume_evidence_score(combined_resume)
    role_alignment = 1.0 if effective_target_role and effective_target_role.lower() in combined_resume.lower() else 0.0
    score = round(
        (
            keyword_score * 0.74 +
            keyword_coverage * 0.16 +
            evidence_score * 0.08 +
            role_alignment * 0.02
        ) * 100
    )
    score = max(12, min(98, score))
    matched_keyword_details = [
        {
            "keyword": keyword,
            "evidence": _find_keyword_evidence(keyword, combined_resume) or "Keyword detected in resume content.",
        }
        for keyword in matched[:16]
    ]
    actions = _profile_actions(
        matched=matched,
        missing=missing,
        technical_missing=technical_missing,
        domain_missing=domain_missing,
        target_role=effective_target_role,
        resume_text=combined_resume,
    )

    return {
        "score": score,
        "rating": _ats_rating(score),
        "target_role": effective_target_role or field,
        "field": field,
        "keyword_fit_score": round(keyword_score * 100),
        "keyword_coverage": round(keyword_coverage * 100),
        "matched_keywords": matched[:16],
        "matched_keyword_details": matched_keyword_details,
        "missing_keywords": missing[:16],
        "job_description_keywords": jd_keywords[:24],
        "resume_keywords": resume_extracted["keywords"][:24],
        "profile_actions": actions,
        "stronger_resume_bullets": _stronger_resume_bullets(field, matched, missing),
        "resources": _resource_links(field, missing),
        "download_rows": [
            ["ATS Score", str(score)],
            ["Rating", _ats_rating(score)],
            ["Field", field],
            ["Target Role", effective_target_role or field],
            ["Keyword Fit Score", str(round(keyword_score * 100))],
            ["Keyword Coverage", str(round(keyword_coverage * 100))],
            ["Matched Keywords", ", ".join(matched[:16])],
            ["Missing Keywords", ", ".join(missing[:16])],
        ],
    }


def ats_report_to_csv(report: dict[str, Any]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(report.get("download_rows", []))
    writer.writerow([])
    writer.writerow(["Profile Actions"])
    for item in report.get("profile_actions", []):
        writer.writerow([item])
    writer.writerow([])
    writer.writerow(["Resources", "Type", "URL", "Why"])
    for resource in report.get("resources", []):
        writer.writerow([resource.get("title"), resource.get("type"), resource.get("url"), resource.get("why")])
    return output.getvalue()
