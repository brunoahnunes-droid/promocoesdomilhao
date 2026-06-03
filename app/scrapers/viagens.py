"""
Módulo de scraping de viagens.
Estrutura preparada para integração com:
  - SerpAPI (Google Flights)
  - Skyscanner API
  - Scraping direto de companhias aéreas

Por ora implementa coleta via SerpAPI (requer SERPAPI_KEY no .env).
"""
import os
from typing import List
import httpx
from app.models import Oferta, Categoria


SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


class ViagensScraper:
    nome = "Google Flights"

    async def buscar_passagens(
        self,
        origem: str,
        destino: str,
        data_ida: str,
        data_volta: str | None = None,
    ) -> List[Oferta]:
        """
        Busca passagens via SerpAPI (Google Flights).
        Args:
            origem: código IATA (ex: GRU)
            destino: código IATA (ex: MIA)
            data_ida: formato YYYY-MM-DD
            data_volta: formato YYYY-MM-DD (opcional)
        """
        if not SERPAPI_KEY:
            raise RuntimeError("SERPAPI_KEY não configurado no .env")

        params = {
            "engine": "google_flights",
            "departure_id": origem,
            "arrival_id": destino,
            "outbound_date": data_ida,
            "currency": "BRL",
            "hl": "pt",
            "api_key": SERPAPI_KEY,
        }
        if data_volta:
            params["return_date"] = data_volta
            params["type"] = "1"  # ida e volta
        else:
            params["type"] = "2"  # só ida

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get("https://serpapi.com/search", params=params)
            resp.raise_for_status()
            data = resp.json()

        resultados = []
        voos = data.get("best_flights", []) + data.get("other_flights", [])

        for voo in voos[:10]:
            try:
                preco = float(voo.get("price", 0))
                if preco <= 0:
                    continue

                legs = voo.get("flights", [{}])
                primeira_perna = legs[0] if legs else {}
                companhia = primeira_perna.get("airline", "Desconhecida")
                numero_voo = primeira_perna.get("flight_number", "")

                titulo = f"{origem} → {destino} | {companhia} {numero_voo} | {data_ida}"
                if data_volta:
                    titulo += f" a {data_volta}"

                resultados.append(Oferta(
                    titulo=titulo,
                    preco_atual=preco,
                    loja=companhia,
                    url=f"https://www.google.com/flights?q={origem}+{destino}",
                    categoria=Categoria.VIAGENS,
                ))
            except Exception:
                continue

        return resultados


class CruzeirosScraper:
    """
    Placeholder para o módulo de cruzeiros.
    Será implementado com scraping de MSC, Costa e Royal Caribbean.
    """
    nome = "Cruzeiros"

    async def buscar(self, roteiro: str) -> List[Oferta]:
        # TODO: implementar scraping MSC / Costa / Royal Caribbean
        return []
