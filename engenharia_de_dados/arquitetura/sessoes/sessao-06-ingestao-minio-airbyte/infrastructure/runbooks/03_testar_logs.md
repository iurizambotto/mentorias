# Sessão 06 — Testes e logs

## Smoke tests
```bash
docker compose ps
curl -I http://localhost:9100
curl -I http://localhost:9101
```

## Logs (dependências locais)
- MinIO:
```bash
docker compose logs -f minio
```
- PostgreSQL destino:
```bash
docker compose logs -f destination-postgres
```

## Operação Airbyte (`abctl`)
- Status:
```bash
abctl local status
```
- Remoção sem apagar dados:
```bash
abctl local uninstall
```

## Teardown compose da sessão
```bash
docker compose down
```
