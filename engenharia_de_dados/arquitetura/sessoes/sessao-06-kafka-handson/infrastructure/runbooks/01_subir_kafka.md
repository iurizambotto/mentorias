---
title: Sessao 11 — Subir o Kafka
date: 2026-06-29
type: runbook
status: active
tags: [kafka, docker, mentoria]
---

# Sessao 11 — Subir o Kafka

## 1) Entrar na pasta de infraestrutura

A partir da raiz do repositório clonado (`mentorias/`):

```bash
cd engenharia_de_dados/arquitetura/sessoes/sessao-11-kafka-handson/infrastructure
```

## 2) Subir os containers

```bash
docker compose up -d
```

## 3) Verificar status

```bash
docker compose ps
```

Resultado esperado:
```
NAME                      STATUS
mentoria-s11-kafka        running
mentoria-s11-kafka-ui     running
```

## 4) Verificar logs do Kafka (aguardar "ready")

```bash
docker compose logs -f kafka
```

Procurar a linha:
```
[KafkaServer id=1] started
```

Pressionar Ctrl+C para sair dos logs.

## 5) Acessar kafka-ui

Abrir no navegador: http://localhost:8080

Deve aparecer o cluster "local" com status "online".

## 6) Encerrar stack (ao final da sessao)

```bash
docker compose down
```
