# Exemplo prático — Sessão 02 (Airflow)

## Subir o ambiente
```bash
docker compose up airflow-init
docker compose up -d
```

## Acessar
- URL: http://localhost:8080
- Usuário: `admin`
- Senha: `admin`

## Validar estrutura do compose
```bash
docker compose config
```

## Testar assets (fora do Docker)
```bash
pytest docs/sessions/sessao-02-orquestracao-airflow/exemplos/airflow/tests/test_airflow_assets.py
```
