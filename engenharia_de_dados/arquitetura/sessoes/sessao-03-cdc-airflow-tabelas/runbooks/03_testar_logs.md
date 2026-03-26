# Sessão 03 — Testes e logs

## Testes sugeridos
1. Conferir arquivos gerados:
```bash
ls ../../docs/sessions/sessao-03-cdc-airflow-tabelas/exemplos/output
```
2. Validar que o container de laboratório está ativo:
```bash
docker compose ps cdc-lab
```

## Logs
- CDC lab:
```bash
docker compose logs -f cdc-lab
```
- Airflow (quando necessário):
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
