# Sessão 02+03 — Testes e logs

## Smoke tests
1. Airflow API:
```bash
curl -f http://localhost:8080/api/v2/version
```

2. Verificar cdc-lab:
```bash
docker compose ps cdc-lab
```

3. Verificar outputs da sessão:
```bash
ls ../../docs/sessions/sessao-03-cdc-airflow-tabelas/exemplos/output
ls ../../data/generated/marketing
```

## Logs
- CDC lab:
```bash
docker compose logs -f cdc-lab
```

- Airflow scheduler:
```bash
docker compose -f ../sessao-02-orquestracao-airflow/docker-compose.yml logs -f airflow-scheduler
```

## Teardown
```bash
docker compose \
  -f ../sessao-02-orquestracao-airflow/docker-compose.yml \
  -f docker-compose.yml \
  down
```
