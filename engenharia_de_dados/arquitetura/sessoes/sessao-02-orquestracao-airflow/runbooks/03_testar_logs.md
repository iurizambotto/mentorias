# Sessão 02 — Testes e logs

## Smoke tests
1. Verificar status:
```bash
docker compose ps
```
2. Verificar API do Airflow:
```bash
curl -f http://localhost:8080/api/v2/version
```
3. Verificar scheduler:
```bash
docker compose exec airflow-scheduler airflow jobs check --job-type SchedulerJob --hostname "$HOSTNAME"
```

## Logs por ferramenta
- Airflow API:
```bash
docker compose logs -f airflow-apiserver
```
- Airflow Scheduler:
```bash
docker compose logs -f airflow-scheduler
```
- Airflow Worker:
```bash
docker compose logs -f airflow-worker
```
- PostgreSQL:
```bash
docker compose logs -f postgres
```
- Redis:
```bash
docker compose logs -f redis
```

## Teardown
```bash
docker compose down
```
