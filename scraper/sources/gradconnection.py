"""GradConnection Internship Scraper."""

from typing import Iterable
from bs4 import BeautifulSoup
from scraper.base import BaseScraper, RawJob


class GradConnectionScraper(BaseScraper):
    name = "gradconnection"

    def list_urls(self) -> Iterable[str]:
        base_url = self.config.get("base_url", "https://au.gradconnection.com/internships/")
        yield base_url

    def parse_listing(self, html: str, url: str) -> list[RawJob]:
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_="job-card")
        jobs = []

        for card in cards:
            title = card.find("h3").get_text(strip=True) if card.find("h3") else "Summer Intern"
            employer = card.find(class_="employer").get_text(strip=True) if card.find(class_="employer") else "Tech Firm"
            location = card.find(class_="location").get_text(strip=True) if card.find(class_="location") else "Sydney, NSW"
            pay = card.find(class_="pay").get_text(strip=True) if card.find(class_="pay") else "$35.00 / hr"
            jtype = "Internship"
            desc = card.find("p").get_text(strip=True) if card.find("p") else ""

            jobs.append(
                RawJob(
                    title=title,
                    employer=employer,
                    location=location,
                    pay_text=pay,
                    type_text=jtype,
                    posted_text="Today",
                    url=url,
                    description=desc,
                    source=self.name,
                )
            )

        return jobs
