from abc import ABC, abstractmethod
from typing import List
import httpx
from bs4 import BeautifulSoup
from app.models import Oferta


class BaseScraper(ABC):
    nome: str
    url_base: str

    # User-Agent neutro para evitar bloqueios básicos
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async def _get_soup(self, url: str) -> BeautifulSoup:
        async with httpx.AsyncClient(
            timeout=25,
            headers=self.HEADERS,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    @abstractmethod
    async def buscar(self, termo: str) -> List[Oferta]:
        ...
