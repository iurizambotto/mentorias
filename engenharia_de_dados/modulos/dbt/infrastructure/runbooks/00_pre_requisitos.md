---
title: "Pre-requisitos do laboratorio de dbt"
date: 2026-07-31
type: runbook
status: active
tags:
  - dbt
  - laboratorio
---

# Pré-requisitos do laboratório de dbt

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## O que precisa estar instalado

Apenas Docker. O dbt, o adapter e o banco vivem dentro da imagem, logo você não
precisa de Python nem de DuckDB na sua máquina.

| Ferramenta | Versão usada na verificação |
|---|---|
| Docker Engine | 28.3.3 |
| Docker Compose | v2.39.1 |

Versão mais nova costuma funcionar. Versão anterior ao Compose v2 não, porque o
arquivo usa a sintaxe sem a chave `version:`.

## Conferir o que você tem

```bash
docker --version
docker compose version
```

Se o segundo comando responder "is not a docker command", você está no Compose
v1, que lê `docker-compose` com hífen. Atualize antes de seguir.

## Onde o laboratório vive

```bash
cd engenharia_de_dados/modulos/dbt/infrastructure
ls
```

Você deve ver `Dockerfile`, `docker-compose.yml`, `projeto_dbt/` e `runbooks/`.

## O que o laboratório não exige

Nenhuma credencial de nuvem. O banco é um arquivo DuckDB criado dentro de
`projeto_dbt/`, e ele nasce e morre no seu disco. Nada sai da sua máquina.

Próximo passo: [01_subir_ambiente.md](01_subir_ambiente.md).
