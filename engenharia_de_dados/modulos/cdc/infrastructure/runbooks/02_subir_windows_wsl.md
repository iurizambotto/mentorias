---
title: "Subir o ambiente no Windows com WSL"
date: 2026-07-30
type: runbook
status: active
tags: [cdc, docker, mentoria, windows]
---

# Subir no Windows + Docker Desktop + WSL

## 1) Abrir terminal WSL na pasta do modulo de orquestracao

A partir da raiz do repositorio clonado (`mentorias/`):

```bash
cd engenharia_de_dados/modulos/orquestracao-airflow/infrastructure
```

## 2) Subir Airflow base
```bash
docker compose up airflow-init
docker compose up -d
```

Aguardar todos os containers ficarem `healthy` antes de prosseguir:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep mentoria-sessao-02
```

## 3) Subir laboratorio CDC (isolado)

O container `cdc-lab` deve ser subido de forma isolada, a partir do compose proprio da sessao 02+03.
Nao mesclar com o compose do Airflow.

```bash
cd engenharia_de_dados/modulos/cdc/infrastructure
docker compose --profile lab up -d
```

Confirmar que o container subiu:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cdc-lab
```

## 4) Instalar dependencias no container

Obrigatorio antes de rodar qualquer script Python dentro do container:

```bash
docker exec mentoria-s02s03-cdc-lab pip install -e /workspace
```

## 5) Gerar artefatos

> **Pendente.** O gerador de dados sinteticos com CDC foi retirado deste repositorio e sera
> reintroduzido como laboratorio proprio, ja verificado. Ate la, esta secao nao tem comando
> executavel, e nao ha instrucao valida para gerar os artefatos por aqui.

Quando o gerador voltar, os arquivos esperados por esta sessao sao:

```
users.csv, users.jsonl, users__cdc.csv, users__cdc.jsonl
campaigns.csv, campaigns.jsonl, campaigns__cdc.csv, campaigns__cdc.jsonl
events.csv, events.jsonl, events__cdc.csv, events__cdc.jsonl
  costs.csv, costs.jsonl, costs__cdc.csv, costs__cdc.jsonl
  crm.csv, crm.jsonl, crm__cdc.csv, crm__cdc.jsonl
```
