"""Generic parser for public university and college job listing pages."""

from typing import Iterable

from bs4 import BeautifulSoup

from scraper.base import BaseScraper, RawJob
from scraper.jsonld import extract_jobposting_jsonld, map_jsonld_to_raw_job


class UniversityJobsScraper(BaseScraper):
    """Parse common HTML cards or Schema.org JobPosting markup."""

    name = "university_jobs"

    def __init__(self, fetcher, config):
        super().__init__(fetcher, config)
        self.name = config.get("name", self.name)

    def list_urls(self) -> Iterable[str]:
        base_url = self.config["base_url"]
        max_pages = self.config.get("max_pages", 1)
        yield base_url
        for page in range(2, max_pages + 1):
            separator = "&" if "?" in base_url else "?"
            yield f"{base_url}{separator}page={page}"

    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        if not html:
            return []

        jsonld_items = extract_jobposting_jsonld(html)
        if jsonld_items:
            jobs = []
            for item in jsonld_items:
                mapped = map_jsonld_to_raw_job(item, self.name, url)
                if not mapped["location"]:
                    mapped["location"] = self.config.get("default_location", "")
                jobs.append(RawJob(**mapped))
            return jobs

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select(
            ".job-card, .job-listing, .job-listing-card, .listing-item, "
            "[data-job-card]"
        )
        jobs: list[RawJob] = []

        for card in cards:
            title = self._text(card, [".title", ".job-title", "h2", "h3", "h4"])
            if not title:
                continue

            link = card.find("a", href=True)
            jobs.append(
                RawJob(
                    title=title,
                    employer=self._text(
                        card, [".employer", ".company", ".organisation"]
                    )
                    or self.config.get("label", self.name),
                    location=self._text(
                        card, [".location", ".job-location", "[data-location]"]
                    )
                    or self.config.get("default_location", ""),
                    pay_text=self._text(card, [".pay", ".salary", ".remuneration"]),
                    type_text=self._text(
                        card, [".type", ".employment-type", ".job-type"]
                    )
                    or self.config.get("default_job_type_hint", ""),
                    posted_text=self._text(
                        card, [".posted", ".date-posted", "time"]
                    ),
                    url=link["href"] if link else url,
                    description=self._text(
                        card, [".description", ".summary", "p"]
                    ),
                    source=self.name,
                )
            )

        return jobs

    @staticmethod
    def _text(card, selectors: list[str]) -> str:
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                return element.get_text(" ", strip=True)
        return ""
