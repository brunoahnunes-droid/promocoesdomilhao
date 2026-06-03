"""
Módulo de alertas via Telegram (MarkdownV2).
Requer TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env.
"""
import os
import re
import httpx
from app.models import Oferta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Caracteres especiais que devem ser escapados no MarkdownV2
_MDV2_CHARS = r"_[]()~`>#+-=|{}.!"


def _escapar_mdv2(texto: str) -> str:
    return re.sub(r"([" + re.escape(_MDV2_CHARS) + r"])", r"\\\1", str(texto))


async def enviar_alerta(oferta: Oferta, score: float) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    emoji = "🔥" if score >= 80 else "✅"
    preco_fmt = _escapar_mdv2(f"{oferta.preco_atual:,.2f}")
    titulo = _escapar_mdv2(oferta.titulo)
    loja = _escapar_mdv2(oferta.loja)
    score_fmt = _escapar_mdv2(f"{score:.0f}")

    linhas = [
        f"{emoji} *{titulo}*",
        f"💰 R$ {preco_fmt}",
    ]
    if oferta.desconto_pct:
        linhas[1] += f" \\(\\-{_escapar_mdv2(f'{oferta.desconto_pct:.0f}')}%\\)"
    if oferta.preco_original:
        linhas.append(f"~De R$ {_escapar_mdv2(f'{oferta.preco_original:,.2f}')}~")
    linhas += [
        f"📊 Score ICO: *{score_fmt}/100*",
        f"🏪 {loja}",
        f"🔗 [Ver oferta]({oferta.url})",
    ]

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "\n".join(linhas),
        "parse_mode": "MarkdownV2",
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
