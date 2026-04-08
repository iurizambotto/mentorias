# Sessão 10 — Testes e logs

## Smoke tests
```bash
curl -f http://localhost:8080/api/v2/version
curl -f http://localhost:9000/minio/health/live
curl -f http://localhost:8090
curl -f http://localhost:8585
curl -f http://localhost:9090/-/healthy
curl -f http://localhost:3000/api/health
```

## Logs por domínio
- Orquestração:
```bash
docker compose logs -f airflow-apiserver airflow-scheduler airflow-worker
```
- Lakehouse:
```bash
docker compose logs -f minio hive-metastore trino
```
- Governança:
```bash
docker compose logs -f openmetadata-server openmetadata-ingestion openmetadata-elasticsearch
```
- Observabilidade:
```bash
docker compose logs -f prometheus loki grafana
```

## Teardown
```bash
docker compose down
```
