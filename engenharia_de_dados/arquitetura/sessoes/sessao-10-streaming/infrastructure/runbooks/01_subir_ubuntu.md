# Sessão 10 — Subir no Ubuntu

## 1) Preparar diretórios do Airflow
```bash
mkdir -p airflow/dags airflow/logs
```

## 2) Subir stack completa
```bash
docker compose up -d
```

## 3) Acessos principais
- Airflow: `http://localhost:8080`
- MinIO Console: `http://localhost:9001`
- Trino: `http://localhost:8090`
- OpenMetadata: `http://localhost:8585`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
