# Sessão 02 — Subir no Windows + Docker Desktop + WSL

## 1) Checklist inicial
1. Docker Desktop aberto.
2. WSL Integration habilitado para distro Ubuntu.
3. Projeto clonado dentro de `~/` no WSL.

## 2) Preparar diretórios no WSL
```bash
mkdir -p dags logs config plugins
```

## 3) Criar `.env` no WSL
```bash
echo "AIRFLOW_UID=50000" > .env
```

## 4) Inicializar e subir
```bash
docker compose up airflow-init
docker compose up -d
```

## 5) Acesso
- URL no navegador do Windows: `http://localhost:8080`
- Credenciais: `airflow` / `airflow`

## 6) Se travar
1. `wsl --shutdown` (no PowerShell).
2. Reiniciar Docker Desktop.
3. Voltar ao terminal WSL e repetir o `docker compose up -d`.
