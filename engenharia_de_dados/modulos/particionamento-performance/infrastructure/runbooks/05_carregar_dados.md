---
title: "Gerar e carregar os dados do laboratorio"
date: 2026-07-31
type: runbook
status: active
tags:
  - particionamento
  - dados
---

# Gerar e carregar os dados do laboratório

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.
Este runbook assume a pilha de pé, conforme o runbook de subir o ambiente do seu
sistema operacional.

Ele fecha a lacuna entre "os serviços subiram" e "a apostila tem dado para
consultar".

## 1. Gerar os dados

```bash
cd engenharia_de_dados/modulos/particionamento-performance
python3 scripts/gerar_dados.py --destino infrastructure/dados
```

Saída esperada:

```
events.csv: 12000 linhas
events__cdc.csv: 15566 linhas
janela: 2025-01-01 a 2025-01-15, 15 particoes de event_date
```

Precisa apenas de Python 3.11 ou superior, sem instalar nada. O gerador tem
semente fixa: rodar duas vezes produz o mesmo arquivo, e é por isso que a
apostila pode publicar contagens e esperar que elas se reproduzam aqui.

## 2. Por que 15 partições, e não 30

Esse número é um teto medido, não uma preferência.

Acima de cerca de 20 partições, o Hive Metastore desta pilha trava na fase de
commit de um `CREATE TABLE AS SELECT` particionado: a consulta fica em
`FINISHING` para sempre, o metastore para de responder até para um
`SHOW SCHEMAS`, e nenhum log registra erro. Medido em 2026-07-31:

| Partições | Linhas | Resultado |
|---|---|---|
| 5 | 1.000 | concluiu em 5 s |
| 5 | 12.000 | concluiu em 11 s |
| 15 | 12.000 | concluiu em 10 s |
| 25 | 12.000 | travou |
| 30 | 6.000 | travou |

Se você quiser ver o travamento, gere com `--dias 25` e rode o Lab 2 da apostila.
É um exercício legítimo, e reconhecer a assinatura vale mais que evitá-la.

## 3. Carregar no bucket bronze

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v "$PWD/dados":/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-02-08T19-14-21Z \
  cp /data/events.csv local/bronze/marketing/raw/events/
```

E o arquivo de CDC, usado pelo exercício de última versão por evento:

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v "$PWD/dados":/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-02-08T19-14-21Z \
  cp /data/events__cdc.csv local/bronze/marketing/raw/events_cdc/
```

A tag da imagem do cliente é a mesma que o `docker-compose.yml` usa. Manter as
duas iguais evita a situação em que o laboratório funciona com uma versão e
falha com outra sem ninguém entender por quê.

## 4. Conferir o que chegou

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-02-08T19-14-21Z \
  ls -r local/bronze/marketing/
```

Saída esperada: dois objetos, `raw/events/events.csv` e
`raw/events_cdc/events__cdc.csv`.

Você também pode conferir pelo console do MinIO, em `http://localhost:9001`, com
usuário e senha `minioadmin`. É credencial de laboratório e não serve para nada
fora dele.

## 5. O passo que não é opcional: resetar ao terminar

```bash
cd engenharia_de_dados/modulos/particionamento-performance/infrastructure
docker compose down --volumes
```

A opção `--volumes` existe por um motivo concreto, observado nesta pilha.

Os volumes do MinIO e do metastore sobrevivem a um `docker compose down` comum.
Na próxima execução, o `CREATE TABLE IF NOT EXISTS` da apostila encontra a tabela
já registrada, responde `CREATE TABLE: 0 rows`, não faz nada, e a consulta devolve
o dado da sessão anterior como se fosse novo.

Isso aconteceu de verdade: em 2026-07-31 o laboratório devolveu 2.000 linhas em 14
partições quando a origem tinha 60.000 em 30, e o dado era de quatro meses antes.
Parecia ter funcionado.

**Como desconfiar.** Conte as linhas depois de criar a tabela e compare com o que o
gerador reportou. Se não bater, você está lendo estado velho.
