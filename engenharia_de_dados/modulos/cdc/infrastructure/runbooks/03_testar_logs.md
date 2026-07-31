---
title: "Testar os logs dos servicos"
date: 2026-07-30
type: runbook
status: active
tags: [cdc, docker, mentoria, observabilidade]
---

# Testes e logs

## Smoke tests
1. Airflow API:
```bash
curl -f http://localhost:8081/api/v2/version
```

2. Verificar cdc-lab:
```bash
docker compose ps cdc-lab
```

3. Verificar outputs do cdc_generator (a partir da raiz do clone):
```bash
ls python/cdc_generator/data/generated/marketing
```

## Logs
- CDC lab:
```bash
docker compose logs -f cdc-lab
```

- Airflow scheduler:
```bash
docker compose -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml logs -f airflow-scheduler
```

## Teardown
```bash
docker compose \
  -f ../../../sessao-02-orquestracao-airflow/infrastructure/docker-compose.yml \
  -f docker-compose.yml \
  down
```
