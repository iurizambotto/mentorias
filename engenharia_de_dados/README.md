---
title: "Engenharia de Dados"
date: 2026-07-31
type: trilha
status: active
tags: [mentoria, trilha]
---

# Engenharia de Dados

> Arquivo gerado a partir do `trilha.yml`. Nao edite a mao: rode `gerar_trilha.py` novamente, senao a edicao se perde e o documento diverge.

4 de 20 modulos publicados.

A ordem abaixo e a recomendada. Ela nao e obrigacao de percurso: cada
mentorado tem um roteiro proprio, que seleciona e reordena modulos sem
alterar este repositorio.

## Bloco A, Fundamentos

| Modulo | Status | Lab |
|---|---|---|
| [Introducao a engenharia de dados e diagnostico](modulos/introducao-engenharia-dados/) | rascunho | nao |
| [SQL com foco em JOINs](modulos/sql-joins/) | publicado | nao |
| Docker e ambiente local | planejado | sim |

## Bloco B, Armazenamento

| Modulo | Status | Lab |
|---|---|---|
| Object storage e data lake com MinIO | planejado | sim |
| [Formatos de arquivo e tipos de tabela](modulos/formatos-e-tipos-de-tabela/) | rascunho | nao |
| [Particionamento e performance de consultas](modulos/particionamento-performance/) | publicado | sim |
| NoSQL, quando o relacional nao serve | planejado | nao |

## Bloco C, Pipeline e ingestao

| Modulo | Status | Lab |
|---|---|---|
| [Orquestracao com Apache Airflow](modulos/orquestracao-airflow/) | rascunho | sim |
| [Fontes, arquitetura e contratos de dados](modulos/fontes-arquitetura-contratos/) | publicado | nao |
| [Change Data Capture](modulos/cdc/) | rascunho | sim |
| Ingestao com Airbyte | planejado | sim |
| Web scraping | planejado | sim |

## Bloco D, Transformacao

| Modulo | Status | Lab |
|---|---|---|
| [Transformacao com dbt](modulos/dbt/) | rascunho | sim |

## Bloco E, Nuvem e escala

| Modulo | Status | Lab |
|---|---|---|
| [Cloud para dados](modulos/cloud-para-dados/) | rascunho | nao |
| [Infraestrutura como codigo](modulos/infraestrutura-como-codigo/) | rascunho | sim |
| Processamento distribuido, Spark, PySpark e Databricks | planejado | sim |
| [Streaming com Apache Kafka](modulos/streaming-kafka/) | publicado | sim |
| [Kubernetes para engenharia de dados](modulos/kubernetes/) | rascunho | sim |

## Bloco F, Transversal e fecho

| Modulo | Status | Lab |
|---|---|---|
| Governanca, qualidade e LGPD | planejado | nao |
| Projeto de engenharia | planejado | capstone |

## Como usar

Cada modulo tem o proprio `README.md` com o que existe ali e como rodar.
Modulos com laboratorio trazem `lab.json`, o manifesto que registra o que
foi verificado, com qual comando e em que data.
