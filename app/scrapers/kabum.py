"""
Scraper do KaBuM via API interna JSON (catalog/v2/products).
Não requer autenticação — descoberta por análise da SPA.
"""
import httpx
from typing import List
from app.models import Oferta, Categoria

_KABUM_API = "https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products"
_KABUM_BASE = "https://www.kabum.com.br/produto"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://www.kabum.com.br",
    "Referer": "https://www.kabum.com.br/",
}


class KabumScraper:
    nome = "KaBuM!"

    async def buscar(self, termo: str) -> List[Oferta]:
        resultados: List[Oferta] = []

        async with httpx.AsyncClient(timeout=20, headers=_HEADERS, follow_redirects=True) as client:
            resp = await client.get(
                _KABUM_API,
                params={
                    "page": 1,
                    "page_size": 20,
                    "smarthint-channel": "search",
                    "smarthint-query": termo,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        for item in data.get("data", []):
            try:
                attrs = item.get("attributes", {})
                if not attrs.get("available", False):
                    continue

                preco_atual = float(attrs.get("price") or 0)
                if preco_atual <= 0:
                    continue

                old_price = float(attrs.get("old_price") or 0)
                preco_original = old_price if old_price > preco_atual else None

                desconto = attrs.get("discount_percentage")
                if desconto:
                    desconto = float(desconto)
                elif preco_original:
                    desconto = round((1 - preco_atual / preco_original) * 100, 1)

                produto_id = item.get("id", "")
                slug = attrs.get("product_link", "")
                url_produto = f"{_KABUM_BASE}/{produto_id}/{slug}"

                fotos = attrs.get("photos", {})
                imagem = None
                if fotos.get("m"):
                    imagem = fotos["m"][0]
                elif fotos.get("p"):
                    imagem = fotos["p"][0]

                resultados.append(Oferta(
                    titulo=attrs["title"],
                    preco_atual=preco_atual,
                    preco_original=preco_original,
                    desconto_pct=desconto,
                    loja=self.nome,
                    url=url_produto,
                    imagem=imagem,
                    categoria=Categoria.ELETRONICOS,
                ))
            except Exception:
                continue

        return resultados
