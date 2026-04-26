import argparse
import os

from apify_client import ApifyClient
from dotenv import load_dotenv


load_dotenv()


def get_apify_client():
    api_token = os.getenv("APIFY_API_TOKEN", "").strip().strip('"').strip("'")
    if not api_token:
        raise RuntimeError("APIFY_API_TOKEN is not set.")
    if api_token.startswith("http"):
        raise RuntimeError("APIFY_API_TOKEN must be a raw token, not a URL.")
    return ApifyClient(api_token)


def normalize_job(item):
    title = item.get("title") or item.get("positionName") or item.get("position") or "Untitled role"
    company = (
        item.get("companyName")
        or item.get("company")
        or item.get("company_name")
        or item.get("organizationName")
        or "Unknown company"
    )
    location = item.get("location") or item.get("jobLocation") or item.get("formattedLocation") or "Location not provided"
    url = item.get("url") or item.get("link") or "#"
    return {
        "title": title,
        "companyName": company,
        "location": location,
        "url": url,
    }


def fetch_indeed_uk_jobs(search_query, rows=20):
    client = get_apify_client()
    run_input = {
        "query": search_query,
        "country": "United Kingdom",
        "maxItems": rows,
    }
    run = client.actor("MXLpngmVpE8WTESQr").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [normalize_job(item) for item in items]


def main():
    parser = argparse.ArgumentParser(description="Fetch Indeed jobs for the United Kingdom.")
    parser.add_argument("query", help="Search query, for example: 'Environmental Analyst'")
    parser.add_argument("--rows", type=int, default=10, help="Number of jobs to fetch")
    args = parser.parse_args()

    jobs = fetch_indeed_uk_jobs(args.query, rows=args.rows)
    if not jobs:
        print("No jobs found.")
        return

    for index, job in enumerate(jobs, start=1):
        print(f"{index}. {job['title']}")
        print(f"   Company: {job['companyName']}")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")
        print()


if __name__ == "__main__":
    main()
