import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings

WIKI_BASE_URL = settings.WIKI_BASE_URL

async def fetch_html(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def extract_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/wiki/") and not any(href.startswith(p) for p in (
            "/wiki/Special:", "/wiki/Help:", "/wiki/Category:",
            "/wiki/File:", "/wiki/Template:", "/wiki/Portal:", "/wiki/Talk:"
        )):
            full_url = WIKI_BASE_URL + href
            links.append(full_url)
    return list(set(links))


def extract_title_and_content(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("h1").text.strip()
    content_div = soup.find("div", {"id": "bodyContent"})
    content = content_div.get_text(separator="\n").strip() if content_div else ""
    return title, content
