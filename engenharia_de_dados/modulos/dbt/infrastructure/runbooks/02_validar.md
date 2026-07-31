---
title: "Validar e derrubar o laboratorio de dbt"
date: 2026-07-31
type: runbook
status: active
tags:
  - dbt
  - laboratorio
---

# Validar e derrubar o laboratório de dbt

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.
Este runbook assume o [01_subir_ambiente.md](01_subir_ambiente.md) concluído.

## 1. Rodar o projeto inteiro

```bash
cd engenharia_de_dados/modulos/dbt/infrastructure
docker compose run --rm dbt build
```

Saída esperada, na última linha:

```
Done. PASS=22 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=22
```

Os 22 nós são 1 seed, 3 models de staging em view, 1 model de mart em table,
1 model incremental, 1 snapshot, 14 data tests e 1 unit test.

## 2. Ler o resultado

```bash
docker compose run --rm dbt show --inline "select grupo_de_canal, sum(custo) as custo, sum(conversoes) as conversoes, round(sum(custo) / nullif(sum(conversoes), 0), 2) as custo_por_conversao from {{ ref('fct_desempenho_campanha') }} group by grupo_de_canal order by custo_por_conversao"
```

Saída esperada:

```
| grupo_de_canal |   custo | conversoes | custo_por_conversao |
| -------------- | ------- | ---------- | ------------------- |
| Social         | 4,747.9 |          7 |              678.27 |
| Search         | 4,126.8 |          5 |              825.36 |
```

## 3. Quando algo falha

**O seed não encontra o próprio CSV.** A mensagem cita um caminho absoluto que
não existe dentro do container. Isso acontece quando o `target/` foi escrito por
uma execução fora do Docker: o manifesto guardou o caminho da sua máquina e o
parse parcial o reaproveitou.

```bash
docker compose run --rm dbt clean
docker compose run --rm dbt build
```

**Um teste falha e o build para.** Essa é a função do teste. Leia a linha de
ERROR, que diz qual teste falhou e onde ele está declarado, e abra o SQL
compilado que o dbt aponta em `target/compiled/`.

## 4. Derrubar o ambiente

```bash
docker compose run --rm dbt clean
docker compose down --rmi local
```

A ordem importa. O `clean` apaga o `target/` e precisa da imagem ainda de pé; o
`down --rmi local` remove o container e a imagem construída aqui. Invertendo,
o segundo comando reconstrói a imagem que você acabou de apagar.

O arquivo `campanhas.duckdb` continua no disco de propósito, porque ele é o
resultado do seu trabalho. Apague quando quiser começar do zero.
