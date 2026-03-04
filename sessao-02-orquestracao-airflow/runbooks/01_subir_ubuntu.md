# Sessão 02 — Subir no Ubuntu

## 1) Preparar diretórios
```bash
mkdir -p dags logs config plugins
```

## 2) Criar `.env`
```bash
echo "AIRFLOW_UID=$(id -u)" > .env
```

## 3) Inicializar Airflow
```bash
docker compose up airflow-init
```

## 4) Subir stack
```bash
docker compose up -d
```

## 5) Acessar UI
- URL: `http://localhost:8080`
- Usuário: `airflow`
- Senha: `airflow`
