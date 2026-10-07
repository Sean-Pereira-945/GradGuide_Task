# SOURCES.md: Scrape Target Research & Spike Results

This document logs candidate websites evaluated for scraping according to project rules:
1. Scraping using our own code (`requests` + `BeautifulSoup` / JSON-LD).
2. Must respect `robots.txt` and Terms of Service.
3. No job-board aggregators/APIs (Indeed, LinkedIn, Seek, Glassdoor).
4. HTML must contain target job listings without mandatory JavaScript rendering or login.

## Target Sources Evaluation Summary

| Source | Category | Target URL | Robots.txt Result | JSON-LD / HTML Structure | Decision |
|---|---|---|---|---|---|
| **Adelaide University Student Employment** | Campus / Student Jobs | `https://www.adelaide.edu.au/student/employment/jobs` | Allowed for public pages | Plain HTML listing with title, pay, hours, category | **APPROVED (Fixture Provided)** |
| **Monash Student Work Opportunities** | Campus / Student Jobs | `https://www.monash.edu/student-jobs/listings` | Allowed for public pages | JSON-LD `JobPosting` + HTML structure | **APPROVED (Fixture Provided)** |
| **Woolworths Group Careers** | Retail / Casual Chain | `https://www.woolworthsgroup.com.au/careers/casual` | Allowed for public job listings | JSON-LD `JobPosting` schema | **APPROVED (Fixture Provided)** |
| **GradConnection Australia** | Internships / Graduate | `https://au.gradconnection.com/internships/` | Allowed (`/internships/`) | Microdata & static HTML job listings | **APPROVED (Fixture Provided)** |
| **University of Melbourne** | Campus / Student Jobs | `https://students.unimelb.edu.au/careers/find-a-job` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |
| **University of Sydney** | Campus / Student Jobs | `https://www.sydney.edu.au/students/find-a-job.html` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |
| **University of Queensland** | Campus / Student Jobs | `https://employability.uq.edu.au/find-a-job` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |
| **UNSW** | Campus / Student Jobs | `https://www.unsw.edu.au/students/careers` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |
| **RMIT** | Campus / Student Jobs | `https://www.rmit.edu.au/students/careers` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |
| **UTS** | Campus / Student Jobs | `https://www.uts.edu.au/current-students/opportunities` | Public careers page | Shared HTML-card / JSON-LD university parser | **CONFIGURED** |

---

## Fixtures

Saved sample HTML responses are located in:
- `tests/fixtures/adelaide_uni/listing.html`
- `tests/fixtures/monash_uni/listing.html`
- `tests/fixtures/woolworths/listing.html`
- `tests/fixtures/gradconnection/listing.html`

These fixtures are used for offline parser testing and offline DB seeding without making live network requests.

## City filtering

Use `--city` with the scraper CLI to return only listings whose normalized location
matches that city:

```bash
python -m scraper.run --city Melbourne
```

The live API accepts the same filter at `POST /api/jobs/refresh-live?city=Melbourne`.
The web app sends the selected city (or the student's profile home city) when live
scraping is triggered. Scrapers still respect each site's `robots.txt`, request
delays, and retry policy.
