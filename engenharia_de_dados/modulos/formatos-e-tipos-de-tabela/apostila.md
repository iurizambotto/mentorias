---
title: "Apostila, Formatos de arquivo e tipos de tabela"
date: 2026-07-30
type: apostila
status: draft
project: zambotto-mentoria
tags: [armazenamento, iceberg]
---

# Apostila, Formatos de arquivo e tipos de tabela

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

## Sumario

- [3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC](#33-formatos-de-arquivo-csv-jsonl-parquet-e-orc)
- [3.4 Tipos de tabela: Hive, Iceberg e Delta Lake](#34-tipos-de-tabela-hive-iceberg-e-delta-lake)
- [3.5 Camadas bronze, silver e gold](#35-camadas-bronze-silver-e-gold)
- [3.6 Exercícios e entregáveis](#36-exercícios-e-entregáveis)

## Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

## 3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC

A escolha do formato de arquivo impacta diretamente o custo de processamento, a legibilidade, a capacidade de evolução do schema e a integração com diferentes ferramentas.

**CSV, Comma-Separated Values**

CSV é o mais simples e o mais universal. Qualquer ferramenta lê CSV: Python, Excel, R, Spark, bancos de dados, ferramentas SaaS. Não há dependência de ecossistema.

Características:
- Formato textual, legível por humanos.
- Sem schema embutido: os tipos precisam ser inferidos ou declarados externamente.
- Sem compressão nativa (pode ser comprimido externamente com gzip, bz2).
- Parsing é sequencial e caro para datasets grandes (leitura linha por linha).
- Não suporta tipos complexos (arrays, mapas, objetos aninhados) de forma nativa.

Quando usar:
- Ingestão inicial de dados de sistemas externos (arquivos de fornecedores, exports).
- Troca simples de dados entre sistemas sem dependência de biblioteca.
- Debugging e inspeção manual.

**JSONL, JSON Lines**

JSONL (também chamado de NDJSON, Newline-Delimited JSON) é um formato onde cada linha é um objeto JSON válido e independente. Diferente do JSON convencional (que é um único objeto ou array), JSONL é streamável: você pode processar um registro por vez sem ler o arquivo inteiro.

Características:
- Suporta tipos complexos nativamente (arrays, objetos aninhados).
- Schema flexível: cada linha pode ter campos diferentes (schema-on-read).
- Legível por humanos, mas mais verboso que CSV.
- Custo de scan maior que Parquet/ORC para analytics (precisa parsear JSON por linha).
- Ótimo para logs e eventos onde o schema pode variar.

Quando usar:
- Captura de eventos semiestruturados (logs de aplicação, eventos de API).
- Ingestão na camada bronze quando o schema ainda não está estabilizado.
- Integração com sistemas que produzem ou consomem JSON.

**Parquet, formato colunar da Apache**

Parquet é um formato binário e colunar. "Colunar" significa que os dados de cada coluna ficam armazenados juntos no arquivo, em vez de linha por linha.

Isso tem uma consequência enorme em analytics: se você tem uma tabela com 100 colunas e sua query usa apenas 5, o Parquet permite ler apenas os blocos dessas 5 colunas. Em CSV, você leria tudo.

Características:
- Compressão eficiente (Snappy, Gzip, Zstd), reduz custo de armazenamento e I/O.
- Leitura seletiva de colunas (column pruning).
- Suporte a tipos complexos.
- Schema embutido no arquivo (metadata).
- Não é legível por humanos sem ferramentas.
- Dificuldade de merge e update de registros individuais (arquivo imutável por natureza).

Quando usar:
- Camada silver e gold de um data lake.
- Qualquer carga analítica com queries que selecionam subconjunto de colunas.
- Quando custo de armazenamento e tempo de query são prioridades.

**ORC, Optimized Row Columnar**

ORC é outro formato colunar, nascido no ecossistema Apache Hive. Compartilha muitas características com Parquet, mas tem diferenças no modelo interno e em suporte de ferramentas.

Características:
- Colunar, como Parquet.
- Estatísticas internas por stripe (blocos de dados): min, max, count. Permite bloom filters e predicate pushdown mais agressivos em algumas engines.
- Compressão por coluna (Zlib, Snappy, LZO).
- Schema embutido.
- Forte integração com Hive, Spark e engines do ecossistema Hadoop.
- Menor adoção fora do ecossistema Hadoop/Spark em comparação com Parquet.

Quando usar:
- Plataformas com Hive, HiveQL ou Presto/Trino com catálogo Hive.
- Ambientes Databricks ou EMR onde ambos são suportados, a escolha depende do ecossistema da empresa.

**Tabela comparativa**

| Característica | CSV | JSONL | Parquet | ORC |
|---|---|---|---|---|
| Legível por humanos | sim | sim | não | não |
| Schema embutido | não | parcial | sim | sim |
| Tipos complexos | não | sim | sim | sim |
| Compressão nativa | não | não | sim | sim |
| Leitura colunar | não | não | sim | sim |
| Custo de scan | alto | alto | baixo | baixo |
| Facilidade de merge | alta | alta | baixa | baixa |
| Ecossistema | universal | amplo | amplo | Hadoop+ |

**Referência do livro (Cap. 8, Data Storage Design Patterns)**

O padrão *Horizontal Partitioner* descrito no Cap. 8 complementa diretamente a escolha de formato. Particionar por data no Parquet, por exemplo, é o que permite ao motor de query ignorar partições inteiras e ler apenas o intervalo de tempo relevante. Sem particionamento, até o melhor formato colunar é forçado a escanear blocos desnecessários.

## 3.4 Tipos de tabela: Hive, Iceberg e Delta Lake

Formatos de arquivo (Parquet, ORC) são diferentes de *table formats*. O table format é a camada que define como metadados, schema, transações e histórico são gerenciados por cima dos arquivos físicos.

**Hive Table, o modelo original do data lake**

O modelo Hive é o mais antigo e o mais simples. Uma tabela Hive é basicamente um diretório no HDFS ou S3 com arquivos de dados, e um catálogo (Hive Metastore) que mapeia o nome da tabela para o path físico, o schema e as partições.

Como funciona:
- Os arquivos físicos ficam em `s3://bucket/tabela/particao=data/arquivo.parquet`.
- O Hive Metastore guarda o schema e o mapeamento.
- Engines como Hive, Spark, Presto e Athena consultam o metastore para saber onde estão os dados.

Limitações:
- Sem transações ACID robustas nativamente. Dois jobs escrevendo na mesma partição ao mesmo tempo podem corromper dados.
- Evolução de schema limitada: adicionar colunas é simples, mas renomear ou mudar tipos pode quebrar leitores existentes.
- Sem time travel nativo.
- Operações de update e delete são limitadas ou ausentes.

Quando ainda faz sentido:
- Pipelines simples de append-only onde não há necessidade de update ou delete.
- Ambientes legados onde a migração para Iceberg ou Delta não vale o custo imediato.
- Quando a engine disponível não suporta os novos formatos.

**Apache Iceberg, o table format moderno e multi-engine**

Iceberg foi criado pelo Netflix e Apache para resolver as limitações do Hive. É um table format aberto, desenhado para funcionar com múltiplas engines (Spark, Flink, Trino, Athena v3, Hive).

Como funciona:
- Cada escrita gera um novo *snapshot*. Um snapshot é um arquivo de metadados que aponta para os arquivos de dados que compõem o estado atual da tabela.
- O histórico de snapshots permite *time travel*: você pode consultar o estado da tabela em qualquer ponto do passado dentro do período de retenção.
- *Schema evolution* é um cidadão de primeira classe: adicionar, renomear e deletar colunas é suportado sem quebrar leitores que usam o schema antigo.
- *Partition evolution*: você pode mudar o esquema de particionamento sem precisar reescrever os dados existentes.
- Suporte a operações ACID: escritas concorrentes são seguras.

Casos de uso ideais:
- Data lakes multi-engine onde diferentes times usam Spark, Trino ou Athena para consultar os mesmos dados.
- Tabelas que evoluem com frequência de schema.
- Pipelines que precisam de time travel para auditoria ou correção de dados históricos.
- Ambientes cloud onde o vendor-lock é uma preocupação.

**Delta Lake, o table format do ecossistema Databricks**

Delta Lake foi criado pela Databricks e é o table format nativo do ambiente Databricks. Funciona bem com Spark e Databricks, e tem suporte crescente em outras engines.

Como funciona:
- Usa um *transaction log* (`_delta_log/`) no diretório da tabela. Cada operação (write, delete, merge, optimize) gera um novo arquivo de log.
- As operações são ACID: um MERGE que processa milhões de linhas é atômico.
- *Time travel*: como o log é preservado por configuração, você pode fazer `SELECT * FROM tabela VERSION AS OF 5` ou `TIMESTAMP AS OF '2026-01-01'`.
- `MERGE INTO` é especialmente performático em Delta Lake.
- `OPTIMIZE` e `ZORDER BY` são operações de compactação e co-localização de dados que melhoram performance de queries.

Casos de uso ideais:
- Ambientes Databricks, onde Delta é nativo e tem suporte completo.
- Pipelines com mutações frequentes (merge, update, delete) onde performance transacional é crítica.

**Tabela comparativa**

| Característica | Hive | Iceberg | Delta Lake |
|---|---|---|---|
| Transações ACID | limitado | sim | sim |
| Schema evolution | básico | completo | completo |
| Partition evolution | não | sim | não |
| Time travel | não | sim | sim |
| Multi-engine | sim | sim (melhor) | crescente |
| Merge / upsert | limitado | sim | sim (otimizado) |
| Vendor | Apache | Apache (open) | Databricks/Linux |
| Melhor cenário | legado/simples | cloud multi-engine | Databricks |

**Referência do livro (Cap. 4, Merger Pattern)**

O padrão *Merger* descreve como aplicar incrementos (inserts + updates + soft deletes) de forma idempotente a um dataset existente. A operação `MERGE INTO` do Delta/Iceberg é a implementação nativa desse padrão.

## 3.5 Camadas bronze, silver e gold

A arquitetura medallion (bronze/silver/gold) é um padrão de organização do data lake em camadas com diferentes níveis de curadoria.

**Bronze, dados brutos, fidelidade máxima**

A camada bronze recebe os dados como chegam da origem, com o mínimo de transformação possível. O objetivo é preservar a fidelidade dos dados originais.

Características:
- Formato preferido: JSONL ou CSV (mantém a estrutura original, legível).
- Particionamento por data de ingestão, não de evento.
- Dados podem ter inconsistências, nulos, duplicatas, tudo é preservado.
- Sem remoção de campos, mesmo que sensíveis (com controle de acesso adequado).
- Table format: Hive simples (append-only) ou Iceberg para capturar histórico.

Analogia: é a "fita bruta" da gravação. Tudo que aconteceu está lá.

**Silver, dados curados, prontos para análise**

A camada silver aplica transformações de qualidade: limpeza de nulos, deduplicação, padronização de tipos, enriquecimento com dados de referência.

Características:
- Formato preferido: Parquet (leitura eficiente, schema embutido).
- Particionamento por data de evento (não de ingestão).
- Dados devem atender contratos de schema definidos.
- Pode incluir campos derivados simples.
- Table format: Parquet + Iceberg ou Delta, dependendo da necessidade de upsert.

Analogia: é a "edição do corte", você removeu os erros, normalizou os dados, mas ainda não produziu o produto final.

**Gold, dados agregados, prontos para consumo**

A camada gold contém datasets prontos para consumo por analistas, dashboards e modelos. São as métricas, agregados e visões de negócio.

Características:
- Formato preferido: Parquet ou Delta/Iceberg.
- Estrutura orientada ao caso de uso (tabela desnormalizada por produto, por região, por canal).
- Alta qualidade garantida.
- Pode ter SLA de atualização definido.

Analogia: é o produto final, o relatório, o dashboard, o número que o stakeholder vai olhar.

**Recomendação para o Projeto 1**

| Camada | Formato | Table Format | Justificativa |
|---|---|---|---|
| Bronze | JSONL / CSV | Hive ou Iceberg | Fidelidade máxima, ingestão direta |
| Silver | Parquet | Iceberg ou Delta | Analytics eficiente, schema estável, suporte a merge |
| Gold | Parquet | Iceberg ou Delta | Performance de query, auditabilidade, SLA |

**Referência do livro (Cap. 9, AWAP Pattern)**

O padrão *Audit-Write-Audit-Publish* encaixa na transição silver → gold: antes de promover dados para a camada gold, você valida o dataset transformado. Se passar, promove. Se não passar, você tem opções: falha o pipeline, envia para dead-letter, ou promove com anotação de incompletude.

**Referência do livro (Cap. 10, Flow Interruption Detector)**

A camada bronze é especialmente vulnerável a interrupções de fluxo. O padrão *Flow Interruption Detector* descreve como detectar quando um job parou de escrever dados sem falhar explicitamente. Implementar um detector de freshness na camada bronze previne que o silêncio de um job com bug passe despercebido por horas ou dias.

## 3.6 Exercícios e entregáveis

**Exercício 1, Matriz de decisão de orquestrador**

Objetivo: aplicar os conceitos de CDC no contexto do Projeto 1.

Dado um arquivo CSV com eventos CDC da tabela `events`:

1. Abra o arquivo com pandas.
2. Agrupe por `event_id`.
3. Ordene por `cdc_event_ts` dentro de cada grupo.
4. Implemente uma função que valida as regras de lifecycle: o primeiro evento deve ser `insert`; após `delete`, não pode haver mais eventos para aquele ID.
5. Imprima o número de IDs com violação.

Entregável: script Python + resultado da validação (número de violações esperado: 0 para o dataset gerado pelo `cdc_generator`).

---

**Exercício 2, Blueprint de camadas bronze/silver/gold**

Objetivo: definir o padrão de armazenamento do Projeto 1.

Para cada camada, defina:
- Formato de arquivo
- Table format
- Estratégia de particionamento
- Política de retenção
- Critério de promoção para a próxima camada

Entregável: tabela de decisão por camada.

---

**Exercício 3, Mini ADR de table format**

Objetivo: documentar formalmente a decisão de table format para o Projeto 1.

Escreva um mini ADR com:
- **Contexto:** qual é o problema que motivou a decisão.
- **Decisão:** qual table format foi escolhido.
- **Alternativas consideradas:** Hive, Iceberg e Delta, com prós e contras de cada um para o contexto.
- **Consequências:** o que fica mais fácil e o que fica mais difícil com a escolha feita.

Entregável: documento de 1 a 2 páginas com as quatro seções preenchidas.

---


## Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

## Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

## Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

## Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

## Glossario

Pendente. Listar os termos novos deste modulo.

## Referencias

Pendente. Documentacao oficial com data de consulta.

## Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.
