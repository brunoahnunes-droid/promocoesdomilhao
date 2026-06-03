"""
Motor de Score ICO (Índice de Confiança da Oferta).

Fórmula:
    score = desconto_pct * 0.30
          + preco_minimo_historico * 0.35
          + confiabilidade_loja * 0.20
          + tendencia * 0.15

Classificação:
    0–40   → Ruim
    40–60  → Normal
    60–80  → Boa oferta
    80–100 → Imperdível 🔥
"""
from dataclasses import dataclass
from typing import Optional


LOJAS_CONFIAVEIS = {
    "Amazon": 0.95,
    "Mercado Livre": 0.85,
    "Magazine Luiza": 0.90,
    "KaBuM!": 0.92,
    "Pichau": 0.90,
    "Terabyte Shop": 0.90,
}


@dataclass
class ResultadoScore:
    score: float
    classificacao: str
    deve_alertar: bool
    detalhes: dict


def classificar(score: float) -> str:
    if score < 40:
        return "Ruim"
    elif score < 60:
        return "Normal"
    elif score < 80:
        return "Boa oferta"
    else:
        return "Imperdível 🔥"


def calcular_score(
    preco_atual: float,
    desconto_pct: Optional[float],
    historico_precos: list[float],
    loja: str,
    score_minimo_alerta: float = 75.0,
) -> ResultadoScore:
    # Componente 1: desconto percentual (0-100 → 0-30)
    # Normaliza fração decimal (0.0-1.0) para percentual (0-100)
    desc_raw = desconto_pct or 0
    if 0 < desc_raw <= 1.0:
        desc_raw = desc_raw * 100
    desc = min(desc_raw, 100)
    comp_desconto = desc * 0.30

    # Componente 2: posição em relação ao mínimo histórico (0-35)
    if historico_precos:
        minimo = min(historico_precos)
        media = sum(historico_precos) / len(historico_precos)
        if media > 0:
            intervalo = media - minimo
            if intervalo > 0:
                # ratio = 1 quando preco == minimo (ótimo), 0 quando preco == media
                ratio = 1 - (preco_atual - minimo) / intervalo
            else:
                # todos os preços históricos são iguais
                ratio = 1.0 if preco_atual <= minimo else 0.0
            comp_historico = max(0, min(ratio, 1)) * 35
        else:
            comp_historico = 0
    else:
        comp_historico = 17.5  # neutro enquanto histórico não é coletado (Fase 1)

    # Componente 3: confiabilidade da loja (0-20)
    confiabilidade = LOJAS_CONFIAVEIS.get(loja, 0.75)
    comp_loja = confiabilidade * 20

    # Componente 4: tendência — neutro na Fase 1, regressão linear na Fase 2
    comp_tendencia = 7.5

    score = comp_desconto + comp_historico + comp_loja + comp_tendencia
    score = round(min(score, 100), 1)

    return ResultadoScore(
        score=score,
        classificacao=classificar(score),
        deve_alertar=score >= score_minimo_alerta,
        detalhes={
            "comp_desconto": round(comp_desconto, 2),
            "comp_historico": round(comp_historico, 2),
            "comp_loja": round(comp_loja, 2),
            "comp_tendencia": round(comp_tendencia, 2),
        }
    )
