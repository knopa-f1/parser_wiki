from typing import List
from urllib.parse import unquote

import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings

EXCLUDED_PREFIXES = {
    '/wiki/Категория:',
    '/wiki/Википедия:',
    '/wiki/Служебная:',
    '/wiki/Файл:',
    '/wiki/Обсуждение:',
    '/wiki/Шаблон:',
    '/wiki/Участник:',
    '/wiki/Справка:',
    '/wiki/Портал:',
    '/wiki/Проект:',
    '/wiki/Архив:',
    '/wiki/Category:',
    '/wiki/Wikipedia:',
    '/wiki/Help:',
    '/wiki/Template:',
    '/wiki/File:',
    '/wiki/MediaWiki:',
    '/wiki/Draft:',
    '/wiki/Talk:',
    '/wiki/User:',
    '/wiki/Portal:',
    '/wiki/Project:',
    '/wiki/Special:',
    '/wiki/Main_Page',
    '/wiki/Module:',
    '/wiki/Book:',
    '/wiki/Education_Program:',
    '/wiki/TimedText:',
    '/wiki/Gadget:',
    '/wiki/Gadget_Definition:',
    '/wiki/w/index.php',
    '/wiki/Special:Search',
    '/wiki/Special:RecentChanges'
}


class WikiParser:
    def __init__(self, base_url: str = settings.WIKI_BASE_URL):
        self.base_url = base_url

    async def fetch_html(self, url: str, session: aiohttp.ClientSession) -> str:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    def extract_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            decoded_href = unquote(href)
            if (decoded_href.startswith("/wiki/") and not any(decoded_href.startswith(p) for p in EXCLUDED_PREFIXES) and
                    not decoded_href.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))):
                full_url = self.base_url + href
                links.append(full_url)
        return list(set(links))

    def extract_title_and_content(self, html: str) -> tuple[str, str]:
        soup = BeautifulSoup(html, "lxml")
        title = soup.find("h1").text.strip()
        content_div = soup.find("div", {"id": "bodyContent"})
        content = content_div.get_text(separator="\n").strip() if content_div else ""
        return title, content
