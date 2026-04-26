import os

from apify_client import ApifyClient
from dotenv import load_dotenv


load_dotenv()


def has_apify_config():
    api_token = os.getenv("APIFY_API_TOKEN", "").strip().strip('"').strip("'")
    return bool(api_token) and not api_token.startswith("http")


def _get_apify_client():
    api_token = os.getenv("APIFY_API_TOKEN", "").strip().strip('"').strip("'")
    if not api_token:
        raise RuntimeError("APIFY_API_TOKEN is not set.")
    if api_token.startswith("http"):
        raise RuntimeError("APIFY_API_TOKEN must be a raw token, not a URL.")
    return ApifyClient(api_token)


def _normalize_job(item, *, primary_link_key, fallback_link_key=None):
    title = item.get("title") or item.get("positionName") or item.get("position") or "Untitled role"
    company = (
        item.get("companyName")
        or item.get("company")
        or item.get("company_name")
        or item.get("organizationName")
        or "Unknown company"
    )
    location = item.get("location") or item.get("jobLocation") or item.get("formattedLocation") or "Location not provided"
    link = item.get(primary_link_key) or (item.get(fallback_link_key) if fallback_link_key else None) or "#"
    normalized = {
        "title": title,
        "companyName": company,
        "location": location,
        "link": link,
        "url": link,
    }
    return normalized


def fetch_linkedin_jobs(search_query, location="United Kingdom", rows=60):
    client = _get_apify_client()
    run_input = {
        "title": search_query,
        "location": location,
        "rows": rows,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
    }


    # Run the Actor and wait for it to finish
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [_normalize_job(item, primary_link_key="link", fallback_link_key="url") for item in items]


def fetch_indeed_jobs(search_query, location="United Kingdom", rows=60):
    client = _get_apify_client()
    run_input = {
        "query": search_query,
        "country": location,
        "maxItems": rows,
    }
    run = client.actor("MXLpngmVpE8WTESQr").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [_normalize_job(item, primary_link_key="url", fallback_link_key="link") for item in items]


def _expand_demo_role_variants(role: str) -> list[str]:
    clean_role = (role or "").strip()
    if not clean_role:
        return []

    variants = [
        clean_role,
        f"Junior {clean_role}",
        f"{clean_role} Intern",
        f"Remote {clean_role}",
        f"{clean_role} Associate",
        f"{clean_role} Specialist",
    ]

    lowered = clean_role.lower()
    if "engineer" in lowered or "developer" in lowered:
        variants.extend(
            [
                clean_role.replace("Engineer", "Developer"),
                clean_role.replace("Developer", "Engineer"),
                f"{clean_role} I",
                f"{clean_role} II",
            ]
        )
    if "analyst" in lowered:
        variants.extend(
            [
                f"Senior {clean_role}",
                clean_role.replace("Analyst", "Consultant"),
                clean_role.replace("Analyst", "Specialist"),
            ]
        )

    deduped: list[str] = []
    seen: set[str] = set()
    for item in variants:
        value = item.strip()
        if value and value.lower() not in seen:
            seen.add(value.lower())
            deduped.append(value)
    return deduped


def generate_demo_jobs(search_query, location="Remote / Flexible", rows=12):
    role_terms = [term.strip() for term in search_query.split(",") if term.strip()] or ["Software Engineer"]
    demo_jobs = []
    expanded_roles: list[str] = []
    for role in role_terms:
        expanded_roles.extend(_expand_demo_role_variants(role))

    deduped_roles: list[str] = []
    seen_roles: set[str] = set()
    for role in expanded_roles:
        if role.lower() not in seen_roles:
            seen_roles.add(role.lower())
            deduped_roles.append(role)

    for index, role in enumerate(deduped_roles[:rows], start=1):
        slug = role.lower().replace(" ", "-")
        demo_jobs.append(
            {
                "title": role,
                "companyName": f"Demo Company {index}",
                "location": location,
                "link": f"https://www.linkedin.com/jobs/search/?keywords={slug}",
                "url": f"https://www.indeed.com/jobs?q={slug}",
            }
        )
    return demo_jobs
