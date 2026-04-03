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
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def fetch_naukri_jobs(search_query, location="United Kingdom", rows=60):
    client = _get_apify_client()
    run_input = {
        "keyword": search_query,
        "location": location,
        "maxJobs": rows,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
        "maxRowsPerUrl": rows,
        "enableUniqueJobs": False,
        "includeSimilarJobs": True,
    }
    run = client.actor("MXLpngmVpE8WTESQr").call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def generate_demo_jobs(search_query, location="Remote / Flexible", rows=6):
    role_terms = [term.strip() for term in search_query.split(",") if term.strip()] or ["Software Engineer"]
    demo_jobs = []
    for index, role in enumerate(role_terms[:rows], start=1):
        slug = role.lower().replace(" ", "-")
        demo_jobs.append(
            {
                "title": role,
                "companyName": f"Demo Company {index}",
                "location": location,
                "link": f"https://www.linkedin.com/jobs/search/?keywords={slug}",
                "url": f"https://www.naukri.com/{slug}-jobs",
            }
        )
    return demo_jobs
