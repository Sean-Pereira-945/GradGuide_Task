"""Site scraper for Adelaide Uni Student Employment jobs."""

from typing import Iterable
from bs4 import BeautifulSoup
from scraper.base import BaseScraper, RawJob


class AdelaideUniScraper(BaseScraper):
    name = "adelaide_uni"

    def list_urls(self) -> Iterable[str]:
        base_url = self.config.get("base_url", "https://www.adelaide.edu.au/student/employment/jobs")
        max_pages = self.config.get("max_pages", 1)
        # Yield pagination URLs
        yield base_url
        for page in range(2, max_pages + 1):
            yield f"{base_url}?page={page}"

    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        job_cards = soup.find_all("div", class_="job-card")
        jobs: list[RawJob] = []

        for card in job_cards:
            title_el = card.find(class_="title")
            title = title_el.get_text(strip=True) if title_el else "Unknown Title"

            employer_el = card.find(class_="employer")
            employer = employer_el.get_text(strip=True) if employer_el else "University of Adelaide"

            location_el = card.find(class_="location")
            location = location_el.get_text(strip=True) if location_el else "Adelaide, SA"

            pay_el = card.find(class_="pay")
            pay_text = pay_el.get_text(strip=True) if pay_el else ""

            type_el = card.find(class_="type")
            type_text = type_el.get_text(strip=True) if type_el else "Casual"

            posted_el = card.find(class_="posted")
            posted_text = posted_el.get_text(strip=True) if posted_el else ""

            desc_el = card.find("p", class_="description")
            description = desc_el.get_text(strip=True) if desc_el else ""

            link_el = card.find("a", href=True)
            job_url = link_el["href"] if link_el else url

            jobs.append(
                RawJob(
                    title=title,
                    employer=employer,
                    location=location,
                    pay_text=pay_text,
                    type_text=type_text,
                    posted_text=posted_text,
                    url=job_url,
                    description=description,
                    source=self.name,
                )
            )

        return jobs
