# Arquitetura de Engenharia de Dados

Materiais executaveis da trilha de arquitetura de engenharia de dados:
scripts Python para geracao de dados sinteticos com CDC e infraestrutura Docker das sessoes praticas.

## Estrutura

```
arquitetura/
├── python/
│   └── cdc_generator/     — gerador de dados sinteticos orientado por dominio YAML
└── sessoes/
    ├── sessao-02-orquestracao-airflow/infrastructure/
    ├── sessao-02-03-airflow-cdc-tipos-tabelas/infrastructure/
    ├── sessao-04-particionamento/infrastructure/
    ├── sessao-05-infraestrutura/infrastructure/
    ├── sessao-06-ingestao-minio-airbyte/infrastructure/
    ├── sessao-07-processamento-distribuido/infrastructure/
    ├── sessao-08-nosql-governanca/infrastructure/
    ├── sessao-09-plataforma-marketing/infrastructure/
    └── sessao-10-streaming/infrastructure/
```

## Pre-requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (`pip install uv` ou `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker + Docker Compose

## Quickstart — cdc_generator

```bash
cd python/cdc_generator

# Instalar dependencias
uv sync

# Gerar datasets com CDC para o dominio marketing
uv run python scripts/generate_domain_data.py \
  --config config/domains/marketing.yaml \
  --output data \
  --formats csv,jsonl \
  --with-cdc

# Rodar testes
uv run pytest
```

Os arquivos gerados ficam em `data/generated/marketing/`.

## Quickstart — infraestrutura das sessoes

Cada sessao tem sua propria pasta `infrastructure/` com `docker-compose.yml` e runbooks:

```bash
# Exemplo: sessao 04 (MinIO + Hive + Trino)
cd sessoes/sessao-04-particionamento/infrastructure
docker compose up -d

# Acompanhar logs
docker compose logs -f

# Teardown
docker compose down
```

Para a sessao 02+03 (Airflow + CDC lab), siga o runbook em:
`sessoes/sessao-02-03-airflow-cdc-tipos-tabelas/infrastructure/runbooks/01_subir_ubuntu.md`

> **Nota Airflow**: antes de subir a sessao 02, copie o arquivo de configuracao:
> `cp sessoes/sessao-02-orquestracao-airflow/infrastructure/.env.example sessoes/sessao-02-orquestracao-airflow/infrastructure/.env`

## Runbooks por sessao

Cada pasta `infrastructure/runbooks/` contem:

| Arquivo | Descricao |
|---|---|
| `00_pre_requisitos.md` | Verificacoes antes de subir |
| `01_subir_ubuntu.md` | Passo a passo no Ubuntu/Linux |
| `02_subir_windows_wsl.md` | Passo a passo no Windows com WSL2 |
| `03_testar_logs.md` | Smoke tests e verificacao de logs |
