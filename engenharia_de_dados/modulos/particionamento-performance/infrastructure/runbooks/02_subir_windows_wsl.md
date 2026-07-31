---
title: "Subir o ambiente no Windows com WSL"
date: 2026-07-30
type: runbook
status: active
tags: [docker, mentoria, particionamento, windows]
---

# Subir no Windows + Docker Desktop + WSL

## Pre-requisitos
- Docker Desktop instalado com integracao WSL habilitada.
- Distro Ubuntu configurada no WSL 2.
- `.wslconfig` com memoria/processadores configurados (minimo 12 GB para esta sessao).
- Codigo no filesystem Linux da distro (`~/...`), nao em `/mnt/c/...`.

---

## 1) Abrir terminal WSL na pasta da 

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
```

## 2) Subir a stack completa

```bash
docker compose up -d
```

O `hive-metastore` vai baixar o driver JDBC do PostgreSQL e inicializar o schema. Acompanhe:

```bash
docker compose logs -f hive-metastore
```

Aguardar `Starting Hive Metastore Server` ou `Metastore service started` antes de continuar.

## 3) Confirmar servicos

```bash
docker compose ps
```

Resultado esperado:

| Container | Status |
|---|---|
| mentoria-s04-minio | Up (healthy) |
| mentoria-s04-minio-init | Exited (0), correto |
| mentoria-s04-metastore-db | Up (healthy) |
| mentoria-s04-hive-metastore | Up |
| mentoria-s04-trino | Up |

## 4) Smoke tests

```bash
# MinIO API (via WSL)
curl -I http://localhost:9000/minio/health/live

# Trino UI (via WSL)
curl -I http://localhost:8090
```

No browser Windows, acessar diretamente:
- MinIO Console: `http://localhost:9001`, login `minioadmin` / `minioadmin`
- Trino UI: `http://localhost:8090`

## 5) Conectar ao Trino CLI

```bash
docker exec -it mentoria-s04-trino trino
```

## 6) Executar laboratorio

Ver roteiro completo em:
`engenharia_de_dados/modulos/particionamento-performance/apostila.md`, secao 10.

## 7) Teardown

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
docker compose down
```

Para remover os volumes junto:
```bash
docker compose down -v
```
