---
title: Sessao 11 — Pre-requisitos
date: 2026-06-29
type: runbook
status: active
tags: [kafka, mentoria, pre-requisitos]
---

# Sessao 11 — Pre-requisitos

## Requisitos de maquina

- Docker + Docker Compose v2 instalados.
- Pelo menos 4 GB de RAM livres (stack leve, apenas Kafka + kafka-ui).
- Python 3.10+.
- Porta 9092 e 8080 livres.

## Verificar Docker

```bash
docker version
docker compose version
```

## Verificar Python

```bash
python3 --version
```

## Criar ambiente virtual e instalar dependencias

```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate         # Linux/Mac
# .venv\Scripts\activate          # Windows PowerShell

pip install -r requirements.txt
```

## Verificar portas livres

```bash
# Linux/Mac
lsof -i :9092
lsof -i :8080

# Windows (PowerShell)
netstat -ano | findstr :9092
netstat -ano | findstr :8080
```

Se alguma porta estiver ocupada, encerrar o processo ou mudar o mapeamento no docker-compose.yml.
