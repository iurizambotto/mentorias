# Runbook de testes — Sessão 04 (MinIO + Hive Metastore + Trino)

## Objetivo
Validar que todos os serviços da sessão 04 estão funcionando e que o fluxo mínimo de consulta no Trino está operacional.

## Escopo
- MinIO (API + Console)
- Metastore DB (PostgreSQL)
- Hive Metastore
- Trino

## Pré-requisitos
- Docker e Docker Compose v2 funcionando.
- Stack da sessão 04 subida via `docker compose up -d`.

## 1) Verificar status dos containers
```bash
docker compose ps
```

**Esperado**
- `minio`: healthy
- `metastore-db`: healthy
- `hive-metastore`: Up
- `trino`: healthy

## 2) Smoke HTTP (MinIO e Trino)
```bash
curl -I http://localhost:9000/minio/health/live
curl -I http://localhost:8090
```

**Esperado**
- MinIO: HTTP 200 OK
- Trino: HTTP 303 (redirect para `/ui`)

## 3) MinIO Console e buckets
1. Abrir `http://localhost:9001` no browser.
2. Login: `minioadmin` / `minioadmin`.
3. Confirmar buckets: `bronze`, `silver`, `gold`.

## 4) Teste funcional no Trino (catálogo + escrita mínima)
```bash
docker exec mentoria-s04-trino trino --execute "SHOW CATALOGS;"
```

**Esperado**: catálogo `hive` disponível.

### 4.1 Criar schema e tabela de validação
```bash
docker exec mentoria-s04-trino trino --execute "CREATE SCHEMA IF NOT EXISTS hive.validation WITH (location = 's3://bronze/validation/');"

docker exec mentoria-s04-trino trino --execute "CREATE TABLE IF NOT EXISTS hive.validation.validation_events (event_id VARCHAR, event_date DATE) WITH (format = 'PARQUET', partitioned_by = ARRAY['event_date'], external_location = 's3://bronze/validation/validation_events/');"

docker exec mentoria-s04-trino trino --execute "INSERT INTO hive.validation.validation_events VALUES ('v001', DATE '2025-01-10'), ('v002', DATE '2025-01-11');"
```

### 4.2 Validar partições e pruning
```bash
docker exec mentoria-s04-trino trino --execute "SELECT * FROM hive.validation.\"validation_events\$partitions\";"

docker exec mentoria-s04-trino trino --execute "EXPLAIN SELECT * FROM hive.validation.validation_events WHERE event_date = DATE '2025-01-10';"
```

**Esperado**
- Retorno das partições `2025-01-10` e `2025-01-11`.
- `EXPLAIN` com constraint da partição `event_date`.

## 5) Hive Metastore (logs)
```bash
docker compose logs -n 200 hive-metastore
```

**Esperado**: mensagens indicando que o serviço iniciou (ex.: `Metastore service started`).

## 6) Metastore DB (health)
```bash
docker compose ps metastore-db
```

**Esperado**: status `healthy`.

## 7) Teardown (quando necessário)
```bash
docker compose down
```

## Troubleshooting rápido

**MinIO não responde**
```bash
docker compose logs minio | tail -50
```

**Trino não responde**
```bash
docker compose logs trino | tail -50
```

**Hive Metastore não sobe / erro de JDBC**
```bash
docker compose logs hive-metastore | grep -i "error\|exception\|failed"
```

Se o erro for `ClassNotFoundException: org.postgresql.Driver`, o download do JDBC falhou.

**Portas em uso**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```
