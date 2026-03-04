# Sessão 02 — Pré-requisitos

## Objetivo
Garantir que Airflow 3.1.x suba sem erro em Ubuntu e Windows + WSL.

## Requisitos mínimos
- Docker Engine / Docker Desktop com Compose v2.
- 8 GB de RAM livres para a sessão.
- 4 vCPUs recomendados.

## Ubuntu
1. Confirmar versões:
   - `docker --version`
   - `docker compose version`
2. Criar diretórios locais da sessão:
   - `dags/`, `logs/`, `config/`, `plugins/`
3. Definir UID em `.env`:
   - `AIRFLOW_UID=$(id -u)`

## Windows + Docker Desktop + WSL
1. Confirmar integração da distro Ubuntu no Docker Desktop.
2. Executar comandos no terminal WSL (não no PowerShell).
3. Manter o projeto em `~/...` dentro do WSL, evitando `/mnt/c/...`.
4. Definir `AIRFLOW_UID=50000` no `.env` da sessão.
