# Sessao 04 — Testes e logs

## Smoke tests

### MinIO
```bash
curl -I http://localhost:9000/minio/health/live
# Esperado: HTTP/1.1 200 OK
```

### Trino
```bash
curl -I http://localhost:8090
# Esperado: HTTP/1.1 200 OK
```

### Metastore Thrift (via Trino)
```bash
docker exec -it mentoria-s04-trino trino --execute "SHOW CATALOGS;"
# Esperado: linha com 'hive'
```

### Buckets MinIO
```bash
docker exec mentoria-s04-minio-init mc ls local/
# Esperado: bronze, silver, gold
```

---

## Logs por servico

### MinIO
```bash
docker compose logs -f minio
```

### MinIO Init (bootstrap de buckets)
```bash
docker compose logs minio-init
```

### Metastore DB
```bash
docker compose logs -f metastore-db
```

### Hive Metastore
```bash
docker compose logs -f hive-metastore
```
Para filtrar erros:
```bash
docker compose logs hive-metastore 2>&1 | grep -i "error\|exception\|failed"
```

### Trino
```bash
docker compose logs -f trino
```

---

## Verificar particoes criadas no laboratorio

```bash
docker exec -it mentoria-s04-trino trino --execute \
  "SELECT * FROM hive.marketing.\"\$partitions\";"
```

## Verificar arquivos no MinIO (estrutura de particoes)

```bash
docker exec mentoria-s04-minio-init mc ls --recursive local/bronze/marketing/events/
```

---

## Teardown

```bash
# Apenas containers
docker compose down

# Containers + volumes (apaga todos os dados do lab)
docker compose down -v
```
