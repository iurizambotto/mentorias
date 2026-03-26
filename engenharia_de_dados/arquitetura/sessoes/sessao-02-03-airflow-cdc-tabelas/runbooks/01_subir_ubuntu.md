# Sessao 02+03 - Subir no Ubuntu

## 1) Subir Airflow base (Sessao 02)
```bash
cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-02-orquestracao-airflow
docker compose up airflow-init
docker compose up -d
```

Aguardar todos os containers ficarem `healthy` antes de prosseguir:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep mentoria-sessao-02
```

## 2) Subir laboratorio CDC (Sessao 02+03)

O container `cdc-lab` deve ser subido de forma isolada, a partir do compose proprio da sessao 02+03.
Nao mesclar com o compose do Airflow — isso causaria uma segunda instancia desnecessaria.

```bash
cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-02-03-airflow-cdc-tabelas
docker compose --profile lab up -d
```

Confirmar que o container subiu:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep cdc-lab
```

## 3) Instalar dependencias no container

Obrigatorio antes de rodar qualquer script Python dentro do container:

```bash
docker exec mentoria-s02s03-cdc-lab pip install -e /workspace
```

## 4) Gerar artefatos da aula
```bash
docker exec mentoria-s02s03-cdc-lab python /workspace/scripts/build_session_03_assets.py --debug
```

## 5) Gerar datasets + CDC completo
```bash
docker exec mentoria-s02s03-cdc-lab python /workspace/scripts/generate_domain_data.py \
  --config /workspace/config/domains/marketing.yaml \
  --output /workspace/data/generated/marketing \
  --formats csv,jsonl \
  --with-cdc \
  --debug
```

Os arquivos gerados ficam em:
```
projects/zambotto-mentoria/data/generated/marketing/
  users.csv, users.jsonl, users__cdc.csv, users__cdc.jsonl
  campaigns.csv, campaigns.jsonl, campaigns__cdc.csv, campaigns__cdc.jsonl
  events.csv, events.jsonl, events__cdc.csv, events__cdc.jsonl
  costs.csv, costs.jsonl, costs__cdc.csv, costs__cdc.jsonl
  crm.csv, crm.jsonl, crm__cdc.csv, crm__cdc.jsonl
```
