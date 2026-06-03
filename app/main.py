"""
Pramo-ao — API principal
FastAPI + rotas REST para produtos, preços, alertas e ofertas.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
from pydantic import BaseModel
from app.models import Oferta, Categoria
from app.scrapers.mercadolivre import MercadoLivreScraper
from app.scrapers.kabum import KabumScraper
from app.score import calcular_score
from app.alertas import enviar_alerta
import asyncio

app = FastAPI(
    title="Pramo-ao API",
    description="Buscador inteligente de promoções com Score ICO",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Modelos de request/response
# ──────────────────────────────────────────────

class BuscaRequest(BaseModel):
    termo: str
    fontes: List[str] = ["mercadolivre", "kabum"]
    score_minimo: float = 0.0


class OfertaComScore(BaseModel):
    oferta: Oferta
    score: float
    classificacao: str


# ──────────────────────────────────────────────
# Rotas
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><body style="font-family:sans-serif;padding:2rem">
    <h1>🎯 Pramo-ao API</h1>
    <p>Buscador inteligente de promoções</p>
    <ul>
      <li><a href="/docs">Swagger UI</a></li>
      <li><a href="/redoc">ReDoc</a></li>
      <li><a href="/api/deals">Top ofertas agora</a></li>
    </ul>
    </body></html>
    """


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/products/search", response_model=List[OfertaComScore])
async def buscar_produtos(req: BuscaRequest):
    """
    Busca produtos em múltiplas lojas e retorna com score ICO.
    """
    scrapers = []
    if "mercadolivre" in req.fontes:
        scrapers.append(MercadoLivreScraper())
    if "kabum" in req.fontes:
        scrapers.append(KabumScraper())

    if not scrapers:
        raise HTTPException(400, "Nenhuma fonte válida informada.")

    # Coleta paralela
    tarefas = [s.buscar(req.termo) for s in scrapers]
    resultados_raw = await asyncio.gather(*tarefas, return_exceptions=True)

    todas: List[Oferta] = []
    for r in resultados_raw:
        if isinstance(r, list):
            todas.extend(r)

    # Calcular score ICO para cada oferta
    com_score = []
    for oferta in todas:
        resultado = calcular_score(
            preco_atual=oferta.preco_atual,
            desconto_pct=oferta.desconto_pct,
            historico_precos=[],   # Fase 2: virá do banco
            loja=oferta.loja,
            score_minimo_alerta=req.score_minimo,
        )
        oferta.score_ico = resultado.score
        com_score.append(OfertaComScore(
            oferta=oferta,
            score=resultado.score,
            classificacao=resultado.classificacao,
        ))

    # Ordenar por score decrescente
    com_score.sort(key=lambda x: x.score, reverse=True)
    return com_score


@app.get("/api/deals", response_model=List[OfertaComScore])
async def top_deals(
    categoria: Optional[Categoria] = None,
    score_minimo: float = Query(default=60.0, ge=0, le=100),
    limite: int = Query(default=20, ge=1, le=100),
):
    """
    Retorna as melhores ofertas do momento (score ICO acima do mínimo).
    """
    termos = {
        Categoria.ELETRONICOS: ["smartphone", "notebook", "tv samsung"],
        Categoria.SEGURANCA: ["camera ip", "nvr hikvision", "switch poe"],
    }

    categoria_busca = categoria or Categoria.ELETRONICOS
    lista_termos = termos.get(categoria_busca, ["smartphone"])

    todas: List[OfertaComScore] = []
    for termo in lista_termos[:2]:  # limitar para não sobrecarregar
        req = BuscaRequest(termo=termo, score_minimo=score_minimo)
        resultado = await buscar_produtos(req)
        todas.extend(resultado)

    todas = [o for o in todas if o.score >= score_minimo]
    todas.sort(key=lambda x: x.score, reverse=True)
    return todas[:limite]


@app.post("/api/alerts/send")
async def enviar_alerta_manual(oferta: Oferta, score: float = 80.0):
    """Envia alerta manual via Telegram."""
    sucesso = await enviar_alerta(oferta, score)
    if not sucesso:
        raise HTTPException(500, "Falha ao enviar alerta. Verifique TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")
    return {"status": "enviado"}
