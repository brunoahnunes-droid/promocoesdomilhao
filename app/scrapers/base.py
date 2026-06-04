import re
import urllib.parse
from abc import ABC, abstractmethod
from typing import List
import httpx
from bs4 import BeautifulSoup
from app.models import Oferta

_DOMINIOS_PERMITIDOS = {
    "lista.mercadolivre.com.br",
    "www.mercadolivre.com.br",
    "mercadolivre.com.br",
    "www.kabum.com.br",
    "kabum.com.br",
    "serpapi.com",
}


class BaseScraper(ABC):
    nome: str
    url_base: str

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    @staticmethod
    def sanitizar_termo(termo: str) -> str:
        """Remove chars fora do conjunto seguro e URL-encoda o restante."""
        limpo = re.sub(r"[^\w\s\-]", "", termo, flags=re.UNICODE).strip()[:100]
        return urllib.parse.quote(limpo, safe="-_ ")

    async def _get_soup(self, url: str) -> BeautifulSoup:
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname not in _DOMINIOS_PERMITIDOS:
            raise ValueError(f"Domínio não permitido: {parsed.hostname}")

        async with httpx.AsyncClient(
            timeout=25,
            headers=self.HEADERS,
            follow_redirects=True,  # ML e KaBuM fazem redirect — necessário
        ) as client:
            resp = await client.get(url)
            # Valida domínio final após redirects (proteção SSRF mantida)
            final_host = urllib.parse.urlparse(str(resp.url)).hostname or ""
            if final_host not in _DOMINIOS_PERMITIDOS:
                raise ValueError(f"Redirect para domínio não permitido: {final_host}")
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")

    @abstractmethod
    async def buscar(self, termo: str) -> List[Oferta]:
        ...
