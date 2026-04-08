# Sessao 02+03 - Subir no Windows + Docker Desktop + WSL

## 1) Abrir terminal WSL na pasta da sessao 02
```bash
cd ~/zambotto_new/projects/zambotto-mentoria/docs/mentees/aurelius/sessions/sessao-02-orquestracao-airflow/infrastructure
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
cd ~/zambotto_new/projects/zambotto-mentoria/docs/mentees/aurelius/sessions/sessao-02-03-airflow-cdc-tipos-tabelas/infrastructure
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
```bash
docker exec mentoria-s02s03-cdc-lab python /workspace/docs/mentees/aurelius/python/cdc_generator/scripts/build_session_03_assets.py --debug

docker exec mentoria-s02s03-cdc-lab python /workspace/docs/mentees/aurelius/python/cdc_generator/scripts/generate_domain_data.py \
  --config /workspace/docs/mentees/aurelius/python/cdc_generator/config/domains/marketing.yaml \
  --output /workspace/docs/mentees/aurelius/python/cdc_generator/data/generated/marketing \
  --formats csv,jsonl \
  --with-cdc \
  --debug
```

Os arquivos gerados ficam em:
```
projects/zambotto-mentoria/docs/mentees/aurelius/python/cdc_generator/data/generated/marketing/
  users.csv, users.jsonl, users__cdc.csv, users__cdc.jsonl
  campaigns.csv, campaigns.jsonl, campaigns__cdc.csv, campaigns__cdc.jsonl
  events.csv, events.jsonl, events__cdc.csv, events__cdc.jsonl
  costs.csv, costs.jsonl, costs__cdc.csv, costs__cdc.jsonl
  crm.csv, crm.jsonl, crm__cdc.csv, crm__cdc.jsonl
```
