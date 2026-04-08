# Sessão 07 — Testes e logs

## Smoke tests
```bash
curl -I http://localhost:8086
curl -I http://localhost:8087
```

## Logs
- Master:
```bash
docker compose logs -f spark-master
```
- Worker:
```bash
docker compose logs -f spark-worker-1
```

## Teardown
```bash
docker compose down
```
