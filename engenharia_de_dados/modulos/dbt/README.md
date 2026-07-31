---
title: "Transformacao com dbt"
date: 2026-07-31
type: modulo
status: publicado
tags: [dbt, mentoria]
---

# Transformação com dbt

Como transformar dado bruto em modelo confiável usando SQL, com versionamento,
teste e documentação no mesmo lugar.

## Estado

Status na trilha: **publicado**. A ordem recomendada vive em `trilha.yml`, na
raiz da trilha. Seu roteiro pode cursar este módulo em outra posição.

## O que tem aqui

- `apostila.md`, o material de estudo do módulo
- `infrastructure/`, o ambiente do laboratório em Docker Compose
- `infrastructure/projeto_dbt/`, o projeto dbt completo do laboratório
- `infrastructure/runbooks/`, o passo a passo para subir, validar e derrubar
- `lab.json`, o manifesto de verificação, nível 3, em 2026-07-31

## O que ainda não existe

Diretórios opcionais ausentes neste módulo, declarados aqui de propósito:

- `scripts/` ausente
- `exercicios/` ausente, os enunciados vivem dentro da apostila
- `diagramas/` ausente

## Como rodar

Siga os runbooks em ordem, a partir da raiz do repositório clonado:

```bash
cat engenharia_de_dados/modulos/dbt/infrastructure/runbooks/00_pre_requisitos.md
```

O laboratório roda inteiro em Docker, com DuckDB como banco. Não precisa de
conta em nuvem nem de Python instalado na sua máquina.
