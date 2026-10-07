"""JSON-LD Schema.org JobPosting Extractor module.

Parses <script type="application/ld+json"> elements from raw HTML,
tolerates syntax flaws, handles arrays / @graph trees, and extracts
structured JobPosting data.
"""

import json
import logging
from typing import Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_jobposting_jsonld(html: str) -> list[dict[str, Any]]:
    """Find and extract all JobPosting schema objects from HTML."""
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    job_postings: list[dict[str, Any]] = []

    for script in jsonld_scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string.strip())
            _collect_job_postings(data, job_postings)
        except json.JSONDecodeError as err:
            logger.debug(f"Failed to parse JSON-LD script block: {err}")
            continue

    return job_postings


def _collect_job_postings(node: Any, results: list[dict[str, Any]]) -> None:
    """Recursively traverse JSON-LD dicts/lists to collect items with @type == JobPosting."""
    if isinstance(node, list):
        for item in node:
            _collect_job_postings(item, results)
    elif isinstance(node, dict):
        # Handle @graph or nested items
        node_type = node.get("@type")
        if node_type == "JobPosting" or (
            isinstance(node_type, list) and "JobPosting" in node_type
        ):
            results.append(node)

        if "@graph" in node:
            _collect_job_postings(node["@graph"], results)

        for key, val in node.items():
            if key != "@graph" and isinstance(val, (dict, list)):
                _collect_job_postings(val, results)


def map_jsonld_to_raw_job(item: dict[str, Any], source_name: str, fallback_url: str) -> dict[str, Any]:
    """Map standard JSON-LD JobPosting schema fields into raw job dictionary."""
    title = item.get("title", "")
    
    employer = ""
    hiring_org = item.get("hiringOrganization")
    if isinstance(hiring_org, dict):
        employer = hiring_org.get("name", "")
    elif isinstance(hiring_org, str):
        employer = hiring_org

    location = ""
    job_loc = item.get("jobLocation")
    if isinstance(job_loc, dict):
        addr = job_loc.get("address", {})
        if isinstance(addr, dict):
            parts = [
                addr.get("addressLocality"),
                addr.get("addressRegion"),
                addr.get("addressCountry"),
            ]
            location = ", ".join([p for p in parts if p])
        elif isinstance(addr, str):
            location = addr
    elif isinstance(job_loc, str):
        location = job_loc

    pay_text = ""
    salary = item.get("baseSalary")
    if isinstance(salary, dict):
        val = salary.get("value", {})
        unit = salary.get("unitText", "")
        currency = salary.get("currency", "AUD")
        if isinstance(val, dict):
            min_v = val.get("minValue")
            max_v = val.get("maxValue")
            if min_v and max_v:
                pay_text = f"{currency} ${min_v}-${max_v} per {unit.lower() if unit else 'period'}"
            elif min_v:
                pay_text = f"{currency} ${min_v} per {unit.lower() if unit else 'period'}"
        elif isinstance(val, (int, float)):
            pay_text = f"{currency} ${val} per {unit.lower() if unit else 'period'}"

    return {
        "title": str(title),
        "employer": str(employer),
        "location": str(location),
        "pay_text": str(pay_text),
        "type_text": str(item.get("employmentType", "")),
        "posted_text": str(item.get("datePosted", "")),
        "url": str(item.get("url") or fallback_url),
        "description": str(item.get("description", "")),
        "source": source_name,
    }
