"""
Celery worker — tarefas agendadas de scraping e alertas.
Executa a cada 30 min buscando ofertas e disparando alertas Telegram.
"""
import asyncio
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("pramoao", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.beat_schedule = {
    "scrape-eletronicos": {
        "task": "app.worker.scrape_e_alertar",
        "schedule": 1800.0,  # 30 minutos
        "args": (["smartphone", "notebook", "tv", "camera ip"],),
    },
}
celery_app.conf.timezone = "America/Sao_Paulo"


@celery_app.task(name="app.worker.scrape_e_alertar")
def scrape_e_alertar(termos: list[str]) -> dict:
    """Executa scraping e envia alertas para ofertas com score >= 80."""
    from app.scrapers.mercadolivre import MercadoLivreScraper
    from app.score import calcular_score
    from app.alertas import enviar_alerta

    scraper = MercadoLivreScraper()
    alertas_enviados = 0

    for termo in termos:
        ofertas = asyncio.run(scraper.buscar(termo))
        for oferta in ofertas:
            resultado = calcular_score(
                preco_atual=oferta.preco_atual,
                desconto_pct=oferta.desconto_pct,
                historico_precos=[],
                loja=oferta.loja,
            )
            if resultado.deve_alertar:
                asyncio.run(enviar_alerta(oferta, resultado.score))
                alertas_enviados += 1

    return {"termos": termos, "alertas_enviados": alertas_enviados}
