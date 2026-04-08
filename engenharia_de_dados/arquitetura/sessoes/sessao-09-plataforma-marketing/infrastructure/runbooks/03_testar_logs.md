# Sessão 09 — Testes e logs

## Smoke test
```bash
docker compose exec marketing-lab python -c "print('ok')"
```

## Logs
```bash
docker compose logs -f marketing-lab
```

## Teardown da sessão 09
```bash
docker compose down
```
