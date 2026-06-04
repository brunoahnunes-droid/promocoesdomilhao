"""
Scraper do Mercado Livre.

Fase 1: requer ML_ACCESS_TOKEN no .env (App Token do portal de devs).
Obter em: https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br

Fase 2: suporte a refresh automático via OAuth2.
"""
import os
import httpx
from typing import List
from app.scrapers.base import BaseScraper
from app.models import Oferta, Categoria

_ML_API = "https://api.mercadolibre.com/sites/MLB/search"
_ML_ACCESS_TOKEN = os.getenv("ML_ACCESS_TOKEN", "")


class MercadoLivreScraper(BaseScraper):
    nome = "Mercado Livre"
    url_base = "https://lista.mercadolivre.com.br"

    async def buscar(self, termo: str) -> List[Oferta]:
        if not _ML_ACCESS_TOKEN:
            # Sem token: retorna vazio sem erro — não quebra o endpoint
            return []

        termo_limpo = self.sanitizar_termo(termo)
        headers = {
            "Authorization": f"Bearer {_ML_ACCESS_TOKEN}",
            "User-Agent": "Pramo-ao/1.0",
        }
        resultados: List[Oferta] = []

        async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
            resp = await client.get(
                _ML_API,
                params={"q": termo_limpo, "limit": 20, "condition": "new"},
            )
            if resp.status_code == 401:
                # Token expirado — retorna vazio silenciosamente
                return []
            resp.raise_for_status()
            data = resp.json()

        for item in data.get("results", []):
            try:
                preco_atual = float(item.get("price") or 0)
                if preco_atual <= 0:
                    continue

                preco_original = item.get("original_price")
                if preco_original:
                    preco_original = float(preco_original)

                desconto = None
                if preco_original and preco_original > preco_atual:
                    desconto = round((1 - preco_atual / preco_original) * 100, 1)

                resultados.append(Oferta(
                    titulo=item["title"],
                    preco_atual=preco_atual,
                    preco_original=preco_original,
                    desconto_pct=desconto,
                    loja=self.nome,
                    url=item.get("permalink", "https://www.mercadolivre.com.br"),
                    imagem=item.get("thumbnail"),
                    categoria=Categoria.ELETRONICOS,
                ))
            except Exception:
                continue

        return resultados
