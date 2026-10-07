"""Unit tests for Fetcher, JSON-LD Extractor, and BaseScraper."""

import pytest
from scraper.fetcher import Fetcher
from scraper.jsonld import extract_jobposting_jsonld, map_jsonld_to_raw_job
from scraper.base import RawJob
from scraper.run import _filter_jobs_by_city


def test_fetcher_offline_mode(tmp_path):
    fixture_file = tmp_path / "test.html"
    fixture_file.write_text("<html><body>Test Fixture</body></html>", encoding="utf-8")

    fetcher = Fetcher(offline=True)
    res = fetcher.fetch("https://example.com/jobs", fixture_path=str(fixture_file))

    assert res.status_code == 200
    assert res.from_cache is True
    assert "Test Fixture" in res.html


def test_jsonld_extraction():
    sample_html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org/",
          "@type": "JobPosting",
          "title": "Casual Barista",
          "hiringOrganization": {"name": "Campus Cafe"},
          "jobLocation": {"address": {"addressLocality": "Adelaide", "addressCountry": "AU"}},
          "baseSalary": {"currency": "AUD", "value": {"minValue": 30.0, "unitText": "HOUR"}},
          "employmentType": "CASUAL",
          "datePosted": "2026-10-02"
        }
        </script>
      </head>
    </html>
    """

    postings = extract_jobposting_jsonld(sample_html)
    assert len(postings) == 1
    raw_job = map_jsonld_to_raw_job(postings[0], source_name="test_source", fallback_url="https://example.com")

    assert raw_job["title"] == "Casual Barista"
    assert raw_job["employer"] == "Campus Cafe"
    assert raw_job["location"] == "Adelaide, AU"
    assert "AUD $30.0" in raw_job["pay_text"]


def test_scraper_city_filter_keeps_only_matching_locations():
    jobs = [
        RawJob("Adelaide job", "Employer", "Adelaide, SA", "", "", "", "", "", "test"),
        RawJob("Sydney job", "Employer", "Sydney, NSW", "", "", "", "", "", "test"),
    ]

    filtered = _filter_jobs_by_city(jobs, "Adelaide")

    assert [job.title for job in filtered] == ["Adelaide job"]
