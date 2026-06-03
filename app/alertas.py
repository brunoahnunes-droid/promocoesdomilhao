"""
Módulo de alertas via Telegram.
Requer TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env.
"""
import os
import httpx
from app.models import Oferta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


async def enviar_alerta(oferta: Oferta, score: float) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    emoji = "🔥" if score >= 80 else "✅"
    linhas = [
        f"{emoji} *{oferta.titulo}*",
        f"💰 R$ {oferta.preco_atual:,.2f}",
    ]
    if oferta.desconto_pct:
        linhas[1] += f" (-{oferta.desconto_pct:.0f}%)"
    if oferta.preco_original:
        linhas.append(f"~~De R$ {oferta.preco_original:,.2f}~~")
    linhas += [
        f"📊 Score ICO: *{score:.0f}/100*",
        f"🏪 {oferta.loja}",
        f"🔗 [Ver oferta]({oferta.url})",
    ]

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "\n".join(linhas),
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json=payload,
            )
            return resp.status_code == 200
    except Exception:
        return False
