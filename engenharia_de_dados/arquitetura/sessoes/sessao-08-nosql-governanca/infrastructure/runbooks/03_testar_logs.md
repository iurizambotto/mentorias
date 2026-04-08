# Sessão 08 — Testes e logs

## Smoke tests
```bash
curl -f http://localhost:8585
curl -f http://localhost:9200
```

## Logs
- MongoDB:
```bash
docker compose logs -f mongodb
```
- OpenMetadata server:
```bash
docker compose logs -f openmetadata-server
```
- OpenMetadata ingestion:
```bash
docker compose logs -f openmetadata-ingestion
```
- Elasticsearch:
```bash
docker compose logs -f openmetadata-elasticsearch
```

## Teardown
```bash
docker compose down
```
