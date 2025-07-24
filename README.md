# Frankenstein v2.1 Skeleton

Estructura base para el bot de trading cripto con Freqtrade + FreqAI, ingestores, dashboard y gateway API.

## Pasos rápidos

```bash
cp .env.example .env   # rellena claves
docker compose build
docker compose up -d
```

- Dashboard: http://localhost:8501
- Gateway API: http://localhost:8000/status
- Freqtrade API: http://localhost:8080 (user/pass en .env)
