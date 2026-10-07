"""Polite HTTP Fetcher module for GradGuide Job Discovery Tool.

Handles User-Agent configuration, rate-limiting delays, exponential backoff retries,
robots.txt policy checking, response HTML disk caching, and offline fixture simulation.
"""

from dataclasses import dataclass
import hashlib
import logging
import os
import time
from typing import Optional
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    url: str
    status_code: int
    html: str
    fetched_at: float
    from_cache: bool = False
    error: Optional[str] = None


class Fetcher:
    """Polite HTTP fetcher enforcing delays, backoff, robots.txt, and caching."""

    def __init__(
        self,
        user_agent: str = "GradGuideStudentJobTool/0.1 (educational project)",
        delay_seconds: float = 1.5,
        max_retries: int = 3,
        cache_dir: str = "data/raw",
        offline: bool = False,
    ):
        self.user_agent = user_agent
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.cache_dir = cache_dir
        self.offline = offline
        self.last_fetch_time: float = 0.0
        self._robot_parsers: dict[str, RobotFileParser] = {}
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def is_allowed_by_robots(self, url: str) -> bool:
        """Check host robots.txt policy for the given URL."""
        if self.offline:
            return True

        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"

        if host not in self._robot_parsers:
            robots_url = urljoin(host, "/robots.txt")
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception as err:
                logger.warning(f"Could not fetch robots.txt for {host}: {err}")
                # Default to allowing if robots.txt cannot be fetched or parsed
            self._robot_parsers[host] = rp

        rp = self._robot_parsers[host]
        return rp.can_fetch(self.user_agent, url)

    def fetch(self, url: str, fixture_path: Optional[str] = None) -> FetchResult:
        """Fetch URL content respecting rules or load from offline fixture/cache."""

        # Offline / Fixture mode
        if self.offline or fixture_path:
            if fixture_path and os.path.exists(fixture_path):
                with open(fixture_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return FetchResult(
                    url=url,
                    status_code=200,
                    html=content,
                    fetched_at=time.time(),
                    from_cache=True,
                )
            return FetchResult(
                url=url,
                status_code=404,
                html="",
                fetched_at=time.time(),
                error="Offline mode enabled and no fixture found",
            )

        # Robots check
        if not self.is_allowed_by_robots(url):
            logger.info(f"URL disallowed by robots.txt: {url}")
            return FetchResult(
                url=url,
                status_code=403,
                html="",
                fetched_at=time.time(),
                error="Disallowed by robots.txt",
            )

        # Rate limiting delay
        elapsed = time.time() - self.last_fetch_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

        # Retry loop with backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=10)
                self.last_fetch_time = time.time()

                if response.status_code == 200:
                    self._save_to_cache(url, response.text)
                    return FetchResult(
                        url=url,
                        status_code=200,
                        html=response.text,
                        fetched_at=self.last_fetch_time,
                    )
                elif response.status_code in (429, 500, 502, 503, 504):
                    time.sleep(2**attempt)
                    continue
                else:
                    return FetchResult(
                        url=url,
                        status_code=response.status_code,
                        html=response.text,
                        fetched_at=self.last_fetch_time,
                        error=f"HTTP Error {response.status_code}",
                    )
            except Exception as err:
                logger.warning(
                    f"Attempt {attempt} failed for {url}: {err}"
                )
                if attempt == self.max_retries:
                    return FetchResult(
                        url=url,
                        status_code=0,
                        html="",
                        fetched_at=time.time(),
                        error=str(err),
                    )
                time.sleep(2**attempt)

        return FetchResult(
            url=url,
            status_code=0,
            html="",
            fetched_at=time.time(),
            error="Max retries reached",
        )

    def _save_to_cache(self, url: str, html: str) -> None:
        """Save HTML response to disk cache for auditing."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc.replace(":", "_")
            host_dir = os.path.join(self.cache_dir, host)
            os.makedirs(host_dir, exist_ok=True)

            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"{timestamp}_{url_hash}.html"

            with open(
                os.path.join(host_dir, filename), "w", encoding="utf-8"
            ) as f:
                f.write(html)
        except Exception as err:
            logger.warning(f"Failed to cache HTML for {url}: {err}")
