# Sessão 03 — Subir no Windows + Docker Desktop + WSL

## 1) Abrir terminal WSL na pasta da sessão
```bash
cd ~/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-03-cdc-airflow-tabelas
```

## 2) Subir stack combinada
```bash
docker compose \
  -f ../sessao-02-orquestracao-airflow/docker-compose.yml \
  -f docker-compose.yml \
  --profile lab \
  up -d
```

## 3) Gerar artefatos CDC
```bash
docker compose run --rm cdc-lab python scripts/build_session_03_assets.py
```
