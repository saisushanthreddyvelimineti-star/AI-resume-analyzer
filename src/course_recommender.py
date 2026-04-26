import json
import os
import re
from typing import Any
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen

from src.helper import ask_openai, has_openai_config


PREFERRED_CHANNELS = {
    "freecodecamp.org": 30,
    "programming with mosh": 24,
    "alex hyett": 20,
    "tech with tim": 16,
    "corey schafer": 16,
    "traversy media": 14,
    "fireship": 10,
    "the net ninja": 10,
}


CURATED_COURSES: dict[str, list[dict[str, str]]] = {
    "python": [
        {
            "title": "Python for Beginners - Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "4h 26m",
            "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "why": "Covers syntax, data structures, functions, and practical beginner exercises.",
        },
        {
            "title": "Python Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "6h",
            "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "why": "Beginner-friendly pacing with hands-on examples useful for job-ready Python basics.",
        },
    ],
    "javascript": [
        {
            "title": "Learn JavaScript - Full Course for Beginners",
            "channel": "freeCodeCamp.org",
            "duration": "3h 26m",
            "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
            "why": "Strong foundation for variables, functions, objects, arrays, and browser logic.",
        },
        {
            "title": "JavaScript Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "48m",
            "url": "https://www.youtube.com/watch?v=W6NZfCO5SIk",
            "why": "Concise primer for candidates who need fast confidence before building projects.",
        },
    ],
    "react": [
        {
            "title": "React Course - Beginner's Tutorial",
            "channel": "freeCodeCamp.org",
            "duration": "11h 55m",
            "url": "https://www.youtube.com/watch?v=bMknfKXIFA8",
            "why": "Covers components, props, state, hooks, and app structure for frontend roles.",
        },
        {
            "title": "React JS - Full Course for Beginners",
            "channel": "Dave Gray",
            "duration": "9h",
            "url": "https://www.youtube.com/watch?v=RVFAyFWO4go",
            "why": "Project-based React practice with routing, effects, and API usage.",
        },
    ],
    "sql": [
        {
            "title": "SQL Tutorial - Full Database Course for Beginners",
            "channel": "freeCodeCamp.org",
            "duration": "4h 20m",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "why": "Teaches queries, joins, schemas, and database basics needed for analyst/backend roles.",
        },
        {
            "title": "SQL Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "3h 10m",
            "url": "https://www.youtube.com/watch?v=7S_tz1z_5bA",
            "why": "Practical SQL path from SELECT statements to relational concepts.",
        },
    ],
    "html": [
        {
            "title": "HTML Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "1h",
            "url": "https://www.youtube.com/watch?v=qz0aGYrrlhU",
            "why": "A clean starting point for semantic HTML and page structure.",
        },
        {
            "title": "HTML Full Course - Build a Website Tutorial",
            "channel": "freeCodeCamp.org",
            "duration": "2h",
            "url": "https://www.youtube.com/watch?v=pQN-pnXPaVg",
            "why": "Builds practical page markup while covering beginner fundamentals.",
        },
    ],
    "css": [
        {
            "title": "CSS Tutorial - Zero to Hero",
            "channel": "freeCodeCamp.org",
            "duration": "6h",
            "url": "https://www.youtube.com/watch?v=1Rs2ND1ryYc",
            "why": "Covers selectors, layout, responsive design, and styling foundations.",
        },
        {
            "title": "CSS Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "1h",
            "url": "https://www.youtube.com/watch?v=yfoY53QXEnI",
            "why": "Fast intro to styling concepts for frontend portfolio work.",
        },
    ],
    "machine learning": [
        {
            "title": "Machine Learning for Everybody - Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "3h 53m",
            "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
            "why": "Explains ML concepts, model training, and evaluation without assuming deep math.",
        },
        {
            "title": "Machine Learning Course for Beginners",
            "channel": "freeCodeCamp.org",
            "duration": "4h",
            "url": "https://www.youtube.com/watch?v=NWONeJKn6kc",
            "why": "A beginner project route for supervised learning and model workflow practice.",
        },
    ],
    "fastapi": [
        {
            "title": "FastAPI Course for Beginners",
            "channel": "freeCodeCamp.org",
            "duration": "3h",
            "url": "https://www.youtube.com/results?search_query=FastAPI+Course+for+Beginners+freeCodeCamp",
            "why": "Targets API fundamentals, routing, validation, and Python backend project patterns.",
        },
        {
            "title": "FastAPI Tutorial - Building REST APIs",
            "channel": "Programming with Mosh",
            "duration": "1h+",
            "url": "https://www.youtube.com/results?search_query=FastAPI+tutorial+Programming+with+Mosh",
            "why": "Good fit for learning production-style API basics for backend roles.",
        },
    ],
    "docker": [
        {
            "title": "Docker Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "1h",
            "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI",
            "why": "Covers images, containers, and Docker workflow for deployment readiness.",
        },
        {
            "title": "Docker Tutorial for Beginners - Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "2h 10m",
            "url": "https://www.youtube.com/results?search_query=Docker+tutorial+for+beginners+freeCodeCamp+full+course",
            "why": "Useful for building a deployable project and explaining container basics in interviews.",
        },
    ],
    "aws": [
        {
            "title": "AWS Certified Cloud Practitioner Training",
            "channel": "freeCodeCamp.org",
            "duration": "13h",
            "url": "https://www.youtube.com/results?search_query=AWS+Certified+Cloud+Practitioner+freeCodeCamp",
            "why": "Maps cloud fundamentals to services, pricing, security, and deployment vocabulary.",
        },
        {
            "title": "AWS Tutorial for Beginners",
            "channel": "Simplilearn",
            "duration": "10h+",
            "url": "https://www.youtube.com/results?search_query=AWS+tutorial+for+beginners+full+course",
            "why": "Broad beginner path for cloud concepts commonly listed in job descriptions.",
        },
    ],
    "azure": [
        {
            "title": "Microsoft Azure Fundamentals Certification Course",
            "channel": "freeCodeCamp.org",
            "duration": "3h+",
            "url": "https://www.youtube.com/results?search_query=Azure+fundamentals+freeCodeCamp+full+course",
            "why": "Covers Azure basics, core services, and certification-oriented cloud vocabulary.",
        },
        {
            "title": "Azure Tutorial for Beginners",
            "channel": "Simplilearn",
            "duration": "8h+",
            "url": "https://www.youtube.com/results?search_query=Azure+tutorial+for+beginners+full+course",
            "why": "Useful for candidates adding cloud deployment confidence to their profile.",
        },
    ],
    "power bi": [
        {
            "title": "Power BI Full Course",
            "channel": "freeCodeCamp.org",
            "duration": "3h+",
            "url": "https://www.youtube.com/results?search_query=Power+BI+full+course+freeCodeCamp",
            "why": "Covers dashboards, data modeling, and BI concepts for analyst roles.",
        },
        {
            "title": "Power BI Tutorial for Beginners",
            "channel": "Alex The Analyst",
            "duration": "4h+",
            "url": "https://www.youtube.com/results?search_query=Power+BI+tutorial+for+beginners+Alex+The+Analyst",
            "why": "Analyst-focused teaching style with practical dashboard examples.",
        },
    ],
    "git": [
        {
            "title": "Git and GitHub for Beginners - Crash Course",
            "channel": "freeCodeCamp.org",
            "duration": "1h 8m",
            "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
            "why": "Covers version control workflows expected in software and data teams.",
        },
        {
            "title": "Git Tutorial for Beginners",
            "channel": "Programming with Mosh",
            "duration": "1h 9m",
            "url": "https://www.youtube.com/watch?v=8JJ101D3knE",
            "why": "Clear explanation of commits, branches, merging, and collaboration basics.",
        },
    ],
}


def _normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def _fallback_course(skill: str, target_job_title: str, index: int) -> dict[str, str]:
    query_templates = [
        f"best {skill} course for beginners {target_job_title}",
        f"{skill} tutorial full course {target_job_title}",
        f"free {skill} crash course projects {target_job_title}",
    ]
    query = quote_plus(query_templates[(index - 1) % len(query_templates)].strip())
    channel = "YouTube Search"
    title_templates = [
        f"Best {skill} course for beginners",
        f"{skill} tutorial full course",
        f"Free {skill} crash course with projects",
    ]
    return {
        "title": title_templates[(index - 1) % len(title_templates)],
        "channel": channel,
        "duration": "Varies",
        "url": f"https://www.youtube.com/results?search_query={query}",
        "why": f"Searches current YouTube courses for {skill} aligned with {target_job_title or 'the target role'}.",
        "rank": index,
    }


def _course_score(course: dict[str, str], skill: str) -> int:
    text = f"{course.get('title', '')} {course.get('channel', '')}".lower()
    score = 0
    if skill.lower() in text:
        score += 35
    if "beginner" in text or "full course" in text:
        score += 18
    for channel, weight in PREFERRED_CHANNELS.items():
        if channel in text:
            score += weight
    return score


def _rank_with_openai(skill: str, target_job_title: str, courses: list[dict[str, str]]) -> list[dict[str, str]]:
    if not has_openai_config() or len(courses) < 2:
        return courses

    try:
        raw = ask_openai(
            f"""
Rank these YouTube courses for a beginner learning {skill} for a {target_job_title or "target job"} role.
Return valid JSON only: {{"ordered_titles": ["title"]}}.
Prioritize free, practical, beginner-friendly, full-course content and reputable channels.

Courses:
{json.dumps(courses)}
""".strip(),
            max_tokens=180,
        )
        parsed = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
        ordered_titles = parsed.get("ordered_titles", [])
        title_position = {str(title).strip().lower(): index for index, title in enumerate(ordered_titles)}
        return sorted(
            courses,
            key=lambda course: title_position.get(course["title"].lower(), 999),
        )
    except Exception:
        return courses


def _youtube_api_search(skill: str, target_job_title: str, max_results: int) -> list[dict[str, str]]:
    api_key = os.getenv("YOUTUBE_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        return []

    query = f"{skill} tutorial full course beginners {target_job_title}".strip()
    params = urlencode(
        {
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results * 2, 10),
            "q": query,
            "key": api_key,
            "videoEmbeddable": "true",
            "safeSearch": "moderate",
        }
    )
    try:
        with urlopen(f"https://www.googleapis.com/youtube/v3/search?{params}", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    courses = []
    for item in payload.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        title = snippet.get("title", "").strip()
        channel = snippet.get("channelTitle", "").strip()
        if not video_id or not title:
            continue
        courses.append(
            {
                "title": title,
                "channel": channel or "YouTube",
                "duration": "See YouTube",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "why": f"Matches the search intent for beginner {skill} learning and is relevant to {target_job_title or 'the target role'}.",
            }
        )
    return courses


def recommend_youtube_courses(
    missing_skills: list[str],
    target_job_title: str = "",
    per_skill: int = 3,
) -> dict[str, Any]:
    cleaned_skills = []
    for skill in missing_skills:
        normalized = _normalize_skill(str(skill))
        if normalized and normalized not in cleaned_skills:
            cleaned_skills.append(normalized)

    recommendations = []
    for skill in cleaned_skills[:8]:
        api_courses = _youtube_api_search(skill, target_job_title, per_skill)
        curated = CURATED_COURSES.get(skill, [])
        if not curated:
            curated = [
                course
                for key, courses in CURATED_COURSES.items()
                if skill in key or key in skill
                for course in courses
            ]

        candidates = [*api_courses, *curated]
        if not candidates:
            candidates = [_fallback_course(skill.title(), target_job_title, index) for index in range(1, per_skill + 1)]

        deduped = list({course["url"]: course for course in candidates}.values())
        ranked = sorted(deduped, key=lambda course: _course_score(course, skill), reverse=True)
        ranked = _rank_with_openai(skill, target_job_title, ranked)[:per_skill]

        recommendations.append(
            {
                "skill": skill.title(),
                "search_queries": [
                    f"best {skill} course for beginners",
                    f"{skill} tutorial full course",
                ],
                "courses": [
                    {
                        **course,
                        "rank": index + 1,
                    }
                    for index, course in enumerate(ranked)
                ],
            }
        )

    return {
        "target_job_title": target_job_title or "Target role",
        "mode": "youtube-api" if os.getenv("YOUTUBE_API_KEY", "").strip() else "simulated-search",
        "per_skill": per_skill,
        "recommendations": recommendations,
    }
