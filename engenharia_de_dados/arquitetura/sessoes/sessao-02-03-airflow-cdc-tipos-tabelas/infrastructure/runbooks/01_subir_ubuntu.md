# Sessao 02+03 — Subir no Ubuntu

## Pre-requisitos

Clone o repositorio e navegue ate a pasta raiz da sessao antes de executar os comandos:

```bash
# A partir do clone do repositorio:
# engenharia_de_dados/arquitetura/sessoes/sessao-02-03-airflow-cdc-tipos-tabelas/infrastructure/
```

## 1) Subir Airflow base (Sessao 02)

A partir da pasta raiz do clone, navegue ate a infra do Airflow:

```bash
cd sessao-02-orquestracao-airflow/infrastructure
docker compose up airflow-init
docker compose up -d
```

Aguardar todos os containers ficarem `healthy` antes de prosseguir:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep mentoria-sessao-02
```

## 2) Subir laboratorio CDC (Sessao 02+03)

O container `cdc-lab` deve ser subido de forma isolada, a partir do compose proprio da sessao 02+03.
Nao mesclar com o compose do Airflow.

A partir da pasta deste runbook (`sessao-02-03-airflow-cdc-tipos-tabelas/infrastructure/`):

```bash
docker compose --profile lab up -d
```

Confirmar que o container subiu:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cdc-lab
```

## 3) Instalar dependencias no container

Obrigatorio antes de rodar qualquer script Python dentro do container:

```bash
docker exec mentoria-s02s03-cdc-lab pip install -e /workspace/python/cdc_generator
```

## 4) Gerar artefatos da aula
```bash
docker exec mentoria-s02s03-cdc-lab python /workspace/python/cdc_generator/scripts/build_session_03_assets.py --debug
```

## 5) Gerar datasets + CDC completo
```bash
docker exec mentoria-s02s03-cdc-lab python /workspace/python/cdc_generator/scripts/generate_domain_data.py \
  --config /workspace/python/cdc_generator/config/domains/marketing.yaml \
  --output /workspace/python/cdc_generator/data/generated/marketing \
  --formats csv,jsonl \
  --with-cdc \
  --debug
```

Os arquivos gerados ficam em:
```
python/cdc_generator/data/generated/marketing/
  users.csv, users.jsonl, users__cdc.csv, users__cdc.jsonl
  campaigns.csv, campaigns.jsonl, campaigns__cdc.csv, campaigns__cdc.jsonl
  events.csv, events.jsonl, events__cdc.csv, events__cdc.jsonl
  costs.csv, costs.jsonl, costs__cdc.csv, costs__cdc.jsonl
  crm.csv, crm.jsonl, crm__cdc.csv, crm__cdc.jsonl
```
