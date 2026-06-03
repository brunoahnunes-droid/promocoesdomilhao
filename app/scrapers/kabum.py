from typing import List
from app.models import Oferta, Categoria
from app.scrapers.base import BaseScraper


class KabumScraper(BaseScraper):
    nome = "KaBuM!"
    url_base = "https://www.kabum.com.br/busca"

    async def buscar(self, termo: str) -> List[Oferta]:
        slug = termo.replace(" ", "%20")
        url = f"{self.url_base}/{slug}"
        soup = await self._get_soup(url)
        resultados = []

        for item in soup.select("article.productCard")[:12]:
            try:
                titulo_el = item.select_one("span.nameCard")
                if not titulo_el:
                    continue

                preco_el = item.select_one("span.priceCard")
                if not preco_el:
                    continue

                preco_txt = (
                    preco_el.text.strip()
                    .replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )
                preco_atual = float(preco_txt)

                link_el = item.select_one("a")
                url_produto = (
                    f"https://www.kabum.com.br{link_el['href']}" if link_el else ""
                )

                img_el = item.select_one("img")
                imagem = img_el.get("src") if img_el else None

                desconto = None
                desc_el = item.select_one("span.discountCard")
                if desc_el:
                    try:
                        desconto = float(
                            desc_el.text.strip().replace("%", "").replace("-", "").strip()
                        )
                    except ValueError:
                        pass

                preco_original = None
                orig_el = item.select_one("span.oldPriceCard")
                if orig_el:
                    try:
                        preco_original = float(
                            orig_el.text.strip()
                            .replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )
                    except ValueError:
                        pass

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
