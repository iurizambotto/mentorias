# Sessao 04 — Subir no Ubuntu

## Stack da sessao
- MinIO (object storage): `http://localhost:9000` (API) e `http://localhost:9001` (Console)
- Hive Metastore: `thrift://localhost:9083`
- Trino (engine SQL): `http://localhost:8090`

## Recursos necessarios
- Minimo 12 GB de RAM livre no host.
- Nao rodar junto com o Airflow da sessao 02 (sem necessidade para esta sessao).

---

## 1) Subir a stack completa

```bash
cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-04-particionamento
docker compose up -d
```

O `hive-metastore` vai:
1. Baixar o driver JDBC do PostgreSQL (~1 MB).
2. Executar `schematool -initSchema` para criar as tabelas do metastore no PostgreSQL.
3. Subir o servico Metastore na porta 9083.

Este processo leva entre 1 e 2 minutos. Acompanhe os logs:

```bash
docker compose logs -f hive-metastore
```

Aguardar a mensagem `Starting Hive Metastore Server` ou `Metastore service started` antes de continuar.

## 2) Confirmar servicos

```bash
docker compose ps
```

Resultado esperado:

| Container | Status |
|---|---|
| mentoria-s04-minio | Up (healthy) |
| mentoria-s04-minio-init | Exited (0) — correto |
| mentoria-s04-metastore-db | Up (healthy) |
| mentoria-s04-hive-metastore | Up |
| mentoria-s04-trino | Up |

## 3) Smoke tests

```bash
# MinIO API
curl -I http://localhost:9000/minio/health/live
# Esperado: HTTP/1.1 200 OK

# Trino UI
curl -I http://localhost:8090
# Esperado: HTTP/1.1 200 OK
```

## 4) Acessos

- MinIO Console: `http://localhost:9001` — login `minioadmin` / `minioadmin`
- Trino UI: `http://localhost:8090`
- Trino CLI:
  ```bash
  docker exec -it mentoria-s04-trino trino
  ```

## 5) Executar laboratorio

Ver roteiro completo em:
`docs/sessions/sessao-04-particionamento/apostila-sessao-04-ultra-detalhada.md` — secao 10.

## 6) Teardown

```bash
cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-04-particionamento
docker compose down
```

Para remover os volumes (dados persistidos) junto:
```bash
docker compose down -v
```
