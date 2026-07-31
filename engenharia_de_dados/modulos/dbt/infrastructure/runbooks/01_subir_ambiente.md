---
title: "Subir o ambiente do laboratorio de dbt"
date: 2026-07-31
type: runbook
status: active
tags:
  - dbt
  - laboratorio
---

# Subir o ambiente do laboratório de dbt

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## 1. Entrar no diretório do laboratório

```bash
cd engenharia_de_dados/modulos/dbt/infrastructure
```

## 2. Declarar seu usuário

O container escreve `target/` e `logs/` dentro do projeto, que fica montado a
partir do seu disco. Sem isso, os arquivos nascem como root e você precisa de
`sudo` para apagar depois.

```bash
export DBT_UID=$(id -u)
export DBT_GID=$(id -g)
```

Rode isso em cada terminal novo. Se preferir, escreva as duas linhas num
arquivo `.env` ao lado do `docker-compose.yml`, que o Compose lê sozinho.

## 3. Construir a imagem

```bash
docker compose build
```

A primeira execução baixa a imagem base e instala o dbt, o que leva alguns
minutos. As seguintes reaproveitam o cache.

Saída esperada, na última linha:

```
 mentoria-dbt:1.12.0  Built
```

## 4. Conferir a conexão

```bash
docker compose run --rm dbt debug
```

Saída esperada, nas duas últimas linhas:

```
  Connection test: [OK connection ok]

All checks passed!
```

O `dbt debug` confere o `dbt_project.yml`, o `profiles.yml`, as dependências e
a conexão com o banco. Quando ele reclama, o problema está antes do seu SQL.

Próximo passo: [02_validar.md](02_validar.md).
