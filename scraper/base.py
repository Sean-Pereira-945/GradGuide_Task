"""Abstract Base Class for all site scrapers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from scraper.fetcher import Fetcher


@dataclass
class RawJob:
    title: str
    employer: str
    location: str
    pay_text: str
    type_text: str
    posted_text: str
    url: str
    description: str
    source: str


@dataclass
class ScrapeResult:
    source_name: str
    urls_scraped: int
    jobs_found: list[RawJob] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class BaseScraper(ABC):
    """Abstract scraper class enforcing consistent scraping interface."""

    name: str

    def __init__(self, fetcher: Fetcher, config: dict[str, Any]):
        self.fetcher = fetcher
        self.config = config

    @abstractmethod
    def list_urls(self) -> Iterable[str]:
        """Return iterable of listing page URLs to scrape."""
        pass

    @abstractmethod
    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        """Parse raw HTML listing page into unnormalized RawJob items."""
        pass

    def parse_detail(self, html: str, url: str) -> Optional[RawJob]:
        """Optional detail page parser."""
        return None

    def run(self) -> ScrapeResult:
        """Orchestrate fetch -> parse cycle safely catching per-page errors."""
        result = ScrapeResult(source_name=self.name, urls_scraped=0)

        for url in self.list_urls():
            result.urls_scraped += 1
            fetch_res = self.fetcher.fetch(url)

            if fetch_res.error:
                result.errors.append(f"Error fetching {url}: {fetch_res.error}")
                continue

            try:
                jobs = self.parse_listing(fetch_res.html, url)
                result.jobs_found.extend(jobs)
            except Exception as err:
                result.errors.append(f"Error parsing {url}: {err}")

        return result
