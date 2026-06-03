# Referências GitHub — Pramo-ao

Projetos open source e recursos catalogados para cada fase do roadmap.

---

## Scraping & Price Tracking

| Projeto | O que aproveitar |
|---------|-----------------|
| [linces/MercadoScraper](https://github.com/linces/MercadoScraper) | Seletores CSS atualizados do ML, técnicas anti-bloqueio |
| [rhanyele/mercadolivre-scraping-kafka](https://github.com/rhanyele/mercadolivre-scraping-kafka) | Arquitetura ML + PostgreSQL + Kafka para escala |
| [Crinibus/scraper](https://github.com/Crinibus/scraper) | Padrão de histórico de preços + visualização |
| [omkarcloud/botasaurus](https://github.com/omkarcloud/botasaurus) | Framework anti-detecção para Fase 3 (KaBuM, Pichau) |
| [arjun-sha/XDriver](https://github.com/arjun-sha/XDriver) | Playwright stealth para scraping de páginas com JS |

## Telegram Bots & Alertas

| Projeto | O que aproveitar |
|---------|-----------------|
| [nuhmanpk/PriceTrackerBot](https://github.com/nuhmanpk/PriceTrackerBot) | Fluxo de alerta Telegram + assinatura por produto |
| [jadia/amazon-price-notify](https://github.com/jadia/amazon-price-notify) | Formatação de mensagem de queda de preço |
| [hschickdevs/Telegram-Crypto-Alerts](https://github.com/hschickdevs/Telegram-Crypto-Alerts) | Gestão de múltiplos alertas por usuário |

## Templates FastAPI + Stack Produção

| Projeto | O que aproveitar |
|---------|-----------------|
| [alperencubuk/fastapi-celery-redis-postgres-docker-rest-api](https://github.com/alperencubuk/fastapi-celery-redis-postgres-docker-rest-api) | Estrutura Docker Compose + Celery pronta para produção |
| [FastAPI-MEA/fastapi-template](https://github.com/FastAPI-MEA/fastapi-template) | Template FastAPI + Redis + PostgreSQL com boas práticas |
| [andgineer/fastapi-celery](https://github.com/andgineer/fastapi-celery) | FastAPI + SQLAlchemy + Celery + nginx |

## Agendamento de Tarefas

| Projeto | Quando usar |
|---------|-------------|
| [agronholm/apscheduler](https://github.com/agronholm/apscheduler) | **Fase 1** — agendamento in-process, simples, sem Redis |
| Celery + Redis (já no stack) | **Fase 2+** — distribuído, tolerante a falhas, monitorável via Flower |

## CI/CD & DevOps

| Ferramenta | Quando usar |
|---------|-------------|
| GitHub Actions (nativo) | **Fase 1-2** — CI/CD gratuito no mesmo repo |
| [harness/harness](https://github.com/harness/harness) | **Fase 3+** — plataforma DevOps completa (SCM + CI/CD + Environments + Registry) |

---

## UX/UI — Referências de Design

### Princípios adotados para o Pramo-ao

1. **Countdown em cada oferta** — mostrar quando a promoção expira reduz abandono
2. **Score ICO visível acima da dobra** — junto ao preço e foto, antes do scroll
3. **Filtro por categoria + score mínimo** — navegação em "promoções reais" sem ruído
4. **Desconto verificado em destaque** — diferencial: não é só % anunciado, é ICO calculado
5. **Personalização futura (Fase 4)** — histórico de busca → "Recomendado para você"

### Fontes UX
- [Baymard Institute — 10 Sales UX Best Practices](https://baymard.com/blog/10-sales-ux-best-practices)
- [Voucherify — Coupons & Promotions UI/UX Best Practices](https://www.voucherify.io/blog/coupon-promotions-ui-ux-best-practices-inspirations)
- [Dealavo — How to display prices in e-commerce](https://dealavo.com/en/how-to-display-prices/)

---

## Gestão do Projeto

### Modelo adotado: GitHub Projects + Milestones por Fase

Cada fase do roadmap vira um **Milestone** no GitHub com issues vinculadas:

| Milestone | Prazo | Issues principais |
|-----------|-------|-------------------|
| Fase 1 — MVP | 30 dias | `#scrapers`, `#score-ico`, `#telegram-alert`, `#docker` |
| Fase 2 — Histórico | 60 dias | `#price-history-db`, `#score-v2`, `#scheduler` |
| Fase 3 — IA | 90 dias | `#fake-deal-detection`, `#ml-model`, `#anti-bot` |
| Fase 4 — Personalização | 120 dias | `#user-profile`, `#recommendations` |
| Fase 5 — Bot Telegram | 150 dias | `#telegram-bot-commands`, `#subscriptions` |
| Fase 6 — Dashboard | 180 dias | `#frontend`, `#charts`, `#realtime` |

### Referências de gestão
- [GitHub Best Practices for Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
- [How to Build a Product Roadmap in GitHub](https://www.ideaplan.io/guides/how-to-build-a-roadmap-in-github)
