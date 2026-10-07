"""Site scraper for Woolworths Group Casual Careers (JSON-LD first)."""

from typing import Iterable
from scraper.base import BaseScraper, RawJob
from scraper.jsonld import extract_jobposting_jsonld, map_jsonld_to_raw_job


class WoolworthsScraper(BaseScraper):
    name = "woolworths"

    def list_urls(self) -> Iterable[str]:
        base_url = self.config.get("base_url", "https://www.woolworthsgroup.com.au/careers/casual")
        yield base_url

    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        if not html:
            return []

        jsonld_items = extract_jobposting_jsonld(html)
        jobs: list[RawJob] = []

        for item in jsonld_items:
            mapped = map_jsonld_to_raw_job(item, source_name=self.name, fallback_url=url)
            jobs.append(RawJob(**mapped))

        return jobs
