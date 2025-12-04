# src/scraper_agent.py
import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import random
from urllib.parse import urlparse
import logging
from typing import List, Dict, Optional
import urllib.robotparser as robotparser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WebScraperAgent:
    UNWANTED_TEXT_KEYWORDS = [
        "cookie",
        "gdpr",
        "accept all",
        "reject all",
        "cart",
        "checkout",
        "quantity",
        "subtotal",
        "sign up",
        "subscribe",
        "newsletter",
    ]

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(
        self, max_output_chars=15000, concurrency_limit=10, preview_chars=500, retries=2
    ):
        self.max_output_chars = max_output_chars
        self.preview_chars = preview_chars
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.retries = retries

    def _get_headers(self):
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    def _extract_clean_text(self, html: str, url: str) -> str:
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")

        for tag in soup(
            [
                "script",
                "style",
                "img",
                "video",
                "noscript",
                "iframe",
                "svg",
                "header",
                "footer",
                "nav",
                "form",
                "button",
                "aside",
                "ad",
            ]
        ):
            tag.decompose()

        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find(class_=re.compile(r"(content|article|post|entry|body)", re.I))
            or soup.find(id=re.compile(r"(content|article|main|post|body)", re.I))
            or soup.find("div", class_=re.compile(r"container|wrapper", re.I))
        )

        if not main_content or len(main_content.get_text(strip=True)) < 200:
            paragraphs = soup.find_all("p")
            big_p = [
                p.get_text(strip=True)
                for p in paragraphs
                if len(p.get_text(strip=True)) > 40
            ]
            text = "\n".join(big_p[:25])
        else:
            text = main_content.get_text(separator="\n", strip=True)

        lines = text.splitlines()
        filtered = []
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 15 and not any(
                kw in line_clean.lower() for kw in self.UNWANTED_TEXT_KEYWORDS
            ):
                filtered.append(line_clean)

        clean_text = "\n".join(filtered)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text).strip()
        return clean_text[: self.max_output_chars]

    async def _fetch_once(self, client: httpx.AsyncClient, url: str, timeout: float):
        resp = await client.get(
            url, headers=self._get_headers(), timeout=timeout, follow_redirects=True
        )
        resp.raise_for_status()
        return resp.text

    async def _fetch(self, client: httpx.AsyncClient, url: str, timeout: float = 8):
        async with self.semaphore:
            last_exc = None
            for attempt in range(self.retries + 1):
                try:
                    html = await self._fetch_once(client, url, timeout)
                    text = self._extract_clean_text(html, url)
                    if len(text) < 100:
                        logger.warning(f"Short content {len(text)} for {url}")
                        return url, text if text else None
                    logger.info("Scraped %s (%d chars)", url, len(text))
                    return url, text
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    last_exc = e
                    wait = 0.5 * (2**attempt) + random.random() * 0.2
                    logger.debug("Retrying %s after %.2fs: %s", url, wait, str(e)[:120])
                    await asyncio.sleep(wait)
                except asyncio.TimeoutError:
                    logger.warning("Timeout %s", url)
                    return url, None
            logger.error("Failed %s after retries: %s", url, str(last_exc)[:150])
            return url, None

    def _allowed_by_robots(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            rp = robotparser.RobotFileParser()
            rp.set_url(base + "/robots.txt")
            rp.read()
            return rp.can_fetch("*", url)
        except Exception:
            return True  # if robots can't be read, be permissive but you may log

    async def scrape_multiple(
        self, urls: List[str], timeout_per_url=8, global_timeout=35
    ) -> Dict[str, str]:
        if not urls:
            return {}

        # Filter via robots.txt
        allowed_urls = [u for u in urls if self._allowed_by_robots(u)]
        disallowed = set(urls) - set(allowed_urls)
        for u in disallowed:
            logger.info("Skipped by robots.txt: %s", u)

        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            timeout=httpx.Timeout(timeout_per_url, connect=5.0),
        ) as client:
            tasks = [
                asyncio.create_task(self._fetch(client, url, timeout_per_url))
                for url in allowed_urls
            ]
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=global_timeout,
                )
            except asyncio.TimeoutError:
                logger.warning("Global timeout %ds", global_timeout)
                results = [t.result() for t in tasks if t.done() and not t.cancelled()]

            scraped = {}
            for r in results:
                if isinstance(r, tuple) and r[1]:
                    scraped[r[0]] = r[1]
            return scraped

    def scrape_url_sync(self, url: str, timeout=8) -> Optional[str]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                asyncio.wait_for(
                    self.scrape_multiple([url], timeout_per_url=timeout),
                    timeout=timeout + 2,
                )
            )
            return result.get(url)
        finally:
            loop.close()
