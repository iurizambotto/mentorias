# Runbook de testes — Sessão 02+03 (Airflow + CDC lab)

## Objetivo
Validar que os serviços do stack de Airflow + CDC lab estão operacionais.

## Escopo
- Airflow API Server
- Scheduler
- Worker
- Triggerer
- DAG Processor
- Redis
- Postgres
- CDC lab

## Pré-requisitos
- Docker e Docker Compose v2 funcionando.
- Stack subida com:
  ```bash
  docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab up -d
  ```

## 1) Verificar status dos containers
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab ps
```

**Esperado**
- `airflow-apiserver`: healthy
- `airflow-scheduler`: healthy
- `airflow-worker`: healthy (pode demorar alguns minutos)
- `airflow-triggerer`: healthy
- `airflow-dag-processor`: healthy
- `redis`: healthy
- `postgres`: healthy
- `cdc-lab`: Up

## 2) Smoke HTTP (Airflow API)
```bash
curl -f http://localhost:8081/api/v2/version
```

**Esperado**: JSON com `version`.

## 3) Airflow UI (manual)
1. Abrir `http://localhost:8081` no browser.
2. Confirmar que a UI carrega e lista DAGs.

## 4) Redis (ping)
```bash
docker exec mentoria-sessao-02-03-airflow-cdc-redis-1 redis-cli ping
```

**Esperado**: `PONG`.

## 5) Postgres (readiness)
```bash
docker exec mentoria-sessao-02-03-airflow-cdc-postgres-1 pg_isready -U airflow
```

**Esperado**: `accepting connections`.

## 6) CDC lab (container ativo)
```bash
docker exec mentoria-s02s03-cdc-lab python --version
```

**Esperado**: versão do Python.

## 7) Teardown (quando necessário)
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab down
```

## Troubleshooting rápido

**Airflow API não responde**
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab logs airflow-apiserver | tail -50
```

**Worker não fica healthy**
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab logs airflow-worker | tail -50
```

**Redis/Postgres não ficam healthy**
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab logs redis | tail -50
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml -f docker-compose.yml --profile lab logs postgres | tail -50
```
