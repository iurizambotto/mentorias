# Sessão 05 — Testes e logs

## Smoke tests
```bash
curl -f http://localhost:9090/-/healthy
curl -f http://localhost:3000/api/health
curl -f http://localhost:3100/ready
```

## Logs
- Prometheus:
```bash
docker compose logs -f prometheus
```
- Loki:
```bash
docker compose logs -f loki
```
- Promtail:
```bash
docker compose logs -f promtail
```
- Grafana:
```bash
docker compose logs -f grafana
```

## Teardown
```bash
docker compose down
```
