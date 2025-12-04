# src/rag/scraper.py

import asyncio
import httpx
from bs4 import BeautifulSoup
import re


class SimpleScraper:
    def __init__(self, max_chars=20000):
        self.max_chars = max_chars

    async def fetch(self, client, url):
        try:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
        except Exception:
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove junk
        for tag in soup(["script", "style", "img", "footer", "nav", "header"]):
            tag.decompose()

        # Prefer article / main content
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find(class_=re.compile("content|article|post|body", re.I))
        )

        text = (
            main.get_text(" ", strip=True) if main else soup.get_text(" ", strip=True)
        )

        text = re.sub(r"\s{2,}", " ", text).strip()
        return text[: self.max_chars]

    async def scrape(self, urls):
        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [self.fetch(client, u) for u in urls]
            results = await asyncio.gather(*tasks)

        docs = {}
        for url, text in zip(urls, results):
            if text:
                text = text.lower()
                text = text.strip()
                docs[url] = text
        return docs
