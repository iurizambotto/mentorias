---
title: "Cloud para dados"
date: 2026-07-31
type: modulo
status: publicado
tags: [cloud, mentoria]
---

# Cloud para dados

O que muda quando o pipeline sai da sua máquina: o que você aluga, o que
continua sendo sua responsabilidade e onde o dinheiro vai embora.

## Estado

Status na trilha: **publicado**. A ordem recomendada vive em `trilha.yml`, na
raiz da trilha. Seu roteiro pode cursar este módulo em outra posição.

## O que tem aqui

- `apostila.md`, o material de estudo do módulo
- `scripts/verificar_blocos.py`, a verificação de nível 2 dos blocos de código

## O que ainda não existe

Este módulo declara `lab: false` no `trilha.yml`, logo não tem `lab.json` nem
`infrastructure/`. O motivo é deliberado: subir recurso de verdade numa nuvem
custa dinheiro e exige credencial, e a trilha não pede que você abra conta.

Diretórios opcionais ausentes, declarados aqui de propósito:

- `exercicios/` ausente, os enunciados vivem dentro da apostila
- `diagramas/` ausente

## Como verificar os blocos de código

O que dá para provar sem conta e sem rede é a sintaxe, e isso está provado. A
partir deste diretório:

```bash
python3 scripts/verificar_blocos.py
```

Saída esperada: sete linhas começando com `OK` e a linha final
`7 checagem(ns), todas em nivel 2`.

O script confere o SQL com sqlglot, a política IAM com o parser de JSON e os
comandos da AWS CLI em modo esqueleto e em modo de ensaio. Ele não cria recurso,
não executa query e não faz chamada de rede. Requer `sqlglot` e a AWS CLI v2 no
PATH; a ausência de qualquer um dos dois é reportada como falha, nunca como
aprovação.

## Módulos vizinhos

Quase todo assunto tratado aqui tem dono em outro módulo, e a apostila diz qual.
O object storage é do módulo de object storage com MinIO, os formatos de arquivo
e tipos de tabela são do módulo de formatos, o particionamento é do módulo de
particionamento e performance, e o provisionamento é do módulo de infraestrutura
como código.
