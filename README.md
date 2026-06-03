# Pramo-ao 🎯

**Buscador Inteligente de Promoções com Score ICO**

> O diferencial não é mostrar descontos — é identificar se a oferta é real.

## Conceito

```
CAPTURA → ANÁLISE → CLASSIFICAÇÃO → ALERTA
```

Cada oferta recebe um **Índice de Confiança da Oferta (ICO)** de 0 a 100:

| Score | Classificação | Ação |
|-------|--------------|------|
| 0–40  | Ruim         | Ignorar |
| 40–60 | Normal       | Monitorar |
| 60–80 | Boa oferta   | Avaliar |
| 80–100 | Imperdível 🔥 | Alertar via Telegram |

## Roadmap

| Fase | Objetivo | Prazo |
|------|----------|-------|
| 1 — MVP | Coletar e alertar | 30 dias |
| 2 — Inteligência | Score com histórico real | 60 dias |
| 3 — IA | Detectar promoções falsas | 90 dias |
| 4 — Personalização | Perfil de usuário | 120 dias |
| 5 — Alertas | Telegram bot completo | 150 dias |
| 6 — Dashboard | Interface web | 180 dias |

## Quickstart

```bash
# 1. Clonar e configurar
cp .env.example .env
# Editar .env com suas credenciais

# 2. Subir com Docker
docker-compose up -d

# 3. Acessar
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Estrutura

```
app/
├── main.py          # FastAPI + rotas
├── models.py        # Pydantic models
├── score.py         # Motor de Score ICO
├── alertas.py       # Telegram alerts
└── scrapers/
    ├── base.py      # Classe base abstrata
    ├── mercadolivre.py
    ├── kabum.py
    └── viagens.py   # Google Flights + Cruzeiros
```

## Categorias Monitoradas (Fase 1)

- **Eletrônicos**: Smartphones, TVs, Notebooks, Impressoras 3D
- **Segurança**: Câmeras IP, NVRs, Controladoras, Switches PoE
- **Viagens**: Passagens aéreas, Hotéis
- **Cruzeiros**: MSC, Costa, Royal Caribbean

## Fontes de Dados

- Mercado Livre (API pública)
- KaBuM! (scraping)
- Magazine Luiza (scraping — em breve)
- Pichau (scraping — em breve)
- Google Flights via SerpAPI (requer chave)
