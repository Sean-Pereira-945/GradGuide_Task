"""Live HTML Site Scraper for Monash University Student Work Opportunities."""

from typing import Iterable
from bs4 import BeautifulSoup
from scraper.base import BaseScraper, RawJob
from scraper.jsonld import extract_jobposting_jsonld, map_jsonld_to_raw_job


class MonashScraper(BaseScraper):
    name = "monash_uni"

    def list_urls(self) -> Iterable[str]:
        base_url = self.config.get("base_url", "https://www.monash.edu/student-jobs/listings")
        yield base_url

    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        if not html:
            return []

        # First try JSON-LD
        jsonld_items = extract_jobposting_jsonld(html)
        if jsonld_items:
            return [RawJob(**map_jsonld_to_raw_job(item, self.name, url)) for item in jsonld_items]

        # Fallback to HTML selectors
        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_="job-card")
        jobs = []

        for card in cards:
            title = card.find("h3").get_text(strip=True) if card.find("h3") else "Student Assistant"
            employer = card.find(class_="employer").get_text(strip=True) if card.find(class_="employer") else "Monash University"
            location = card.find(class_="location").get_text(strip=True) if card.find(class_="location") else "Clayton Campus, VIC"
            pay = card.find(class_="pay").get_text(strip=True) if card.find(class_="pay") else "$30.50 / hr"
            jtype = card.find(class_="type").get_text(strip=True) if card.find(class_="type") else "Part-time"
            desc = card.find("p").get_text(strip=True) if card.find("p") else ""

            jobs.append(
                RawJob(
                    title=title,
                    employer=employer,
                    location=location,
                    pay_text=pay,
                    type_text=jtype,
                    posted_text="Just now",
                    url=url,
                    description=desc,
                    source=self.name,
                )
            )

        return jobs
