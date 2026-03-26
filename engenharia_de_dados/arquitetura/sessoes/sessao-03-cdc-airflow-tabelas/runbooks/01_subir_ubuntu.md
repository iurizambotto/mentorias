# Sessão 03 — Subir no Ubuntu

## 1) Subir Airflow + laboratório CDC
```bash
docker compose \
  -f ../sessao-02-orquestracao-airflow/docker-compose.yml \
  -f docker-compose.yml \
  --profile lab \
  up -d
```

## 2) Gerar arquivos da sessão 03
```bash
docker compose run --rm cdc-lab python scripts/build_session_03_assets.py
```
