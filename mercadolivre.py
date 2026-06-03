from typing import List
from app.models import Oferta, Categoria
from app.scrapers.base import BaseScraper


class MercadoLivreScraper(BaseScraper):
    nome = "Mercado Livre"
    url_base = "https://lista.mercadolivre.com.br"

    async def buscar(self, termo: str) -> List[Oferta]:
        slug = termo.replace(" ", "-")
        url = f"{self.url_base}/{slug}"
        soup = await self._get_soup(url)
        resultados = []

        for item in soup.select("li.ui-search-layout__item")[:12]:
            try:
                titulo_el = item.select_one("h2.ui-search-item__title")
                if not titulo_el:
                    continue

                frac = item.select_one("span.andes-money-amount__fraction")
                if not frac:
                    continue

                preco_atual = float(frac.text.replace(".", "").replace(",", ""))
                cents_el = item.select_one("span.andes-money-amount__cents")
                if cents_el:
                    preco_atual += float(cents_el.text) / 100

                preco_original = None
                orig_el = item.select_one("s.andes-money-amount")
                if orig_el:
                    orig_frac = orig_el.select_one("span.andes-money-amount__fraction")
                    if orig_frac:
                        preco_original = float(orig_frac.text.replace(".", "").replace(",", ""))

                desconto = None
                desc_el = item.select_one("span.andes-money-amount__discount")
                if desc_el:
                    desconto = float(desc_el.text.replace("% OFF", "").strip())
                elif preco_original and preco_original > preco_atual:
                    desconto = round((1 - preco_atual / preco_original) * 100, 1)

                link_el = item.select_one("a.ui-search-link")
                url_produto = link_el["href"].split("?")[0] if link_el else ""

                img_el = item.select_one("img.ui-search-result-image__element")
                imagem = None
                if img_el:
                    imagem = img_el.get("data-src") or img_el.get("src")

                resultados.append(Oferta(
                    titulo=titulo_el.text.strip(),
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
