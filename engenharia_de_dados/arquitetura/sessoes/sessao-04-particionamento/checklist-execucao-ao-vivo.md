# Checklist de execução ao vivo — Sessão 04 (integrada)

## Duração da sessão
- **Base:** 60 minutos (1h).
- **Máximo:** 90 minutos (1h30).

## Recursos necessários no host
- Pelo menos 12 GB de RAM livres (ver `infrastructure/resource-budget.md`).
- Docker e Docker Compose v2 funcionando.
- Não subir outras sessões em paralelo.

---

## Ordem de execução

### 1) Verificar pré-requisitos
- [ ] Docker rodando:
  ```bash
  docker --version
  docker compose version
  ```
- [ ] Memória disponível:
  ```bash
  free -h
  ```
- [ ] Nenhum container antigo consumindo recursos desnecessários:
  ```bash
  docker ps --format "table {{.Names}}\t{{.Status}}"
  ```

### 2) Desenhar o mapa do pipeline (5–10 min)
- [ ] Origem → CDC → bronze → silver → gold → consumo.
- [ ] Definir onde entra o Airflow (orquestração).
- [ ] Registrar grão e chaves principais das tabelas (events, campaigns, costs, crm).

### 3) Subir stack da sessão 04
- [ ] Entrar na pasta:
  ```bash
  cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-04-particionamento
  ```
- [ ] Subir todos os serviços:
  ```bash
  docker compose up -d
  ```
- [ ] Acompanhar o hive-metastore (download do JDBC + initSchema leva ~1-2 min):
  ```bash
  docker compose logs -f hive-metastore
  ```
  Aguardar a mensagem: `Starting Hive Metastore Server` ou `Metastore service started`.

### 4) Confirmar que todos os serviços estão rodando
- [ ] Verificar status:
  ```bash
  docker compose ps
  ```
  Esperado: `minio` healthy, `metastore-db` healthy, `hive-metastore` Up, `trino` Up.
  O `minio-init` deve aparecer como `Exited (0)` — e o comportamento correto.

### 5) Smoke tests
- [ ] Testar MinIO API:
  ```bash
  curl -I http://localhost:9000/minio/health/live
  # Esperado: HTTP/1.1 200 OK
  ```
- [ ] Testar Trino:
  ```bash
  curl -I http://localhost:8090
  # Esperado: HTTP/1.1 200 OK
  ```
- [ ] Verificar buckets criados no MinIO Console:
  - Abrir `http://localhost:9001` no browser.
  - Login: `minioadmin` / `minioadmin`.
  - Confirmar existência dos buckets `bronze`, `silver` e `gold`.

### 6) Carregar dados de marketing no MinIO (bronze)
- [ ] Usar o MinIO Client via Docker (sem instalar nada no host):
  ```bash
  docker run --rm \
    --network mentoria-sessao-04-particionamento_default \
    -v /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/data/generated/marketing:/data \
    -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
    minio/mc:RELEASE.2025-08-13T08-35-41Z \
    cp /data/events.csv local/bronze/marketing/raw/events/

  docker run --rm \
    --network mentoria-sessao-04-particionamento_default \
    -v /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/data/generated/marketing:/data \
    -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
    minio/mc:RELEASE.2025-08-13T08-35-41Z \
    cp /data/events__cdc.csv local/bronze/marketing/raw/events_cdc/
  ```

### 7) Conectar ao Trino CLI
- [ ] Abrir o CLI do Trino:
  ```bash
  docker exec -it mentoria-s04-trino trino
  ```
- [ ] Verificar catálogos disponíveis:
  ```sql
  SHOW CATALOGS;
  ```
  Esperado: linha com `hive`.

### 8) Criar schema e tabela bronze (raw)
- [ ] Criar schema:
  ```sql
  CREATE SCHEMA IF NOT EXISTS hive.marketing
  WITH (location = 's3://bronze/marketing/');
  ```
- [ ] Criar tabela raw (CSV) **somente com VARCHAR** (limitação do Hive CSV no Trino):
  ```sql
  CREATE TABLE IF NOT EXISTS hive.marketing.events_raw (
      event_id    VARCHAR,
      event_date  VARCHAR,
      event_ts    VARCHAR,
      user_id     VARCHAR,
      campaign_id VARCHAR,
      channel     VARCHAR,
      device      VARCHAR,
      country     VARCHAR,
      stage       VARCHAR,
      revenue     VARCHAR
  )
  WITH (
      format = 'CSV',
      external_location = 's3://bronze/marketing/raw/events/',
      skip_header_line_count = 1
  );
  ```
  **Nota:** CSV no Hive/Trino suporta apenas VARCHAR. Tipos são aplicados na tabela silver.

### 9) Criar tabela silver particionada
- [ ] Criar tabela `events_silver` (Parquet + partição):
  ```sql
  CREATE TABLE IF NOT EXISTS hive.marketing.events_silver
  WITH (
      format = 'PARQUET',
      partitioned_by = ARRAY['event_date'],
      external_location = 's3://silver/marketing/events/'
  ) AS
  SELECT
      event_id,
      user_id,
      campaign_id,
      channel,
      device,
      country,
      stage,
      TRY_CAST(revenue AS DOUBLE) AS revenue,
      CAST(event_date AS DATE) AS event_date
  FROM hive.marketing.events_raw;
  ```

### 10) Validar partições e pruning
- [ ] Listar partições:
  ```sql
  SELECT * FROM hive.marketing."events_silver$partitions";
  ```
- [ ] Query com pruning + EXPLAIN:
  ```sql
  EXPLAIN
  SELECT * FROM hive.marketing.events_silver
  WHERE event_date = DATE '2025-01-10';
  ```
- [ ] Query sem pruning + EXPLAIN:
  ```sql
  EXPLAIN
  SELECT * FROM hive.marketing.events_silver
  WHERE channel = 'organic';
  ```

### 11) Extensões opcionais (se houver tempo)
- [ ] Criar tabela `events_cdc_raw` e demonstrar última versão por `event_id`.
- [ ] Demonstrar alta cardinalidade e small files.
- [ ] Testar particionamento híbrido (event_date + campaign_id).

### 12) Validar arquivos no MinIO
- [ ] Abrir `http://localhost:9001` no browser.
- [ ] Navegar até `silver/marketing/events/`.
- [ ] Confirmar estrutura:
  ```
  silver/marketing/events/
    event_date=2025-01-10/
    event_date=2025-01-11/
    ...
  ```

### 13) Encerrar ambiente
- [ ] Sair do CLI do Trino:
  ```
  quit
  ```
- [ ] Teardown da stack:
  ```bash
  cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-04-particionamento
  docker compose down
  ```
- [ ] Confirmar que os containers foram removidos:
  ```bash
  docker ps | grep mentoria-s04
  ```

---

## Troubleshooting rápido

**hive-metastore não sobe / erro de JDBC:**
```bash
docker compose logs hive-metastore | grep -i "error\|exception\|failed"
```
Se o erro for `ClassNotFoundException: org.postgresql.Driver`, o download do JDBC falhou.
Verificar conectividade do container com a internet:
```bash
docker exec mentoria-s04-hive-metastore curl -I https://jdbc.postgresql.org
```

**Trino não responde:**
```bash
docker compose logs trino | tail -30
```
O Trino leva ~30-60 segundos para inicializar completamente após o container subir.

**Erro ao criar tabela no Trino (permission denied):**
Verificar se `hive.non-managed-table-writes-enabled=true` está em `trino/catalog/hive.properties`.

**MinIO Console inacessível:**
```bash
docker compose logs minio | tail -20
```
Verificar se a porta 9001 não está em uso por outra aplicação.
