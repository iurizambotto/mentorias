---
title: "Apostila, particionamento e performance de consultas"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, particionamento]
---

# Apostila, particionamento e performance de consultas

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. Por que particionamento importa](#3-por-que-particionamento-importa)
- [4. Como o particionamento físico funciona](#4-como-o-particionamento-físico-funciona)
- [5. Partition pruning, o mecanismo central](#5-partition-pruning-o-mecanismo-central)
- [6. Estratégias de particionamento](#6-estratégias-de-particionamento)
- [7. Cardinalidade e escolha de chave de partição](#7-cardinalidade-e-escolha-de-chave-de-partição)
- [8. Skew de partição](#8-skew-de-partição)
- [9. Hot partitions](#9-hot-partitions)
- [10. Custo contra performance](#10-custo-contra-performance)
- [11. A stack do laboratório](#11-a-stack-do-laboratório)
- [12. Laboratório](#12-laboratório)
- [13. Análise do domínio de marketing](#13-análise-do-domínio-de-marketing)
- [14. Exercícios e entregáveis](#14-exercícios-e-entregáveis)
- [15. Mini-desafio com solução](#15-mini-desafio-com-solução)
- [16. Rubrica de validação da aprendizagem](#16-rubrica-de-validação-da-aprendizagem)
- [17. Erros comuns e como corrigir](#17-erros-comuns-e-como-corrigir)
- [18. Plano de continuidade](#18-plano-de-continuidade)
- [19. Glossário](#19-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** As seções 3 a 5 constroem o mecanismo. Da 6 à 10 cada seção
trata de uma decisão de projeto com consequência de custo. A 12 é o laboratório, e
ele é o centro deste módulo.

**Revisão pontual.** Pruning na 5, escolha de chave na 7, custo na 10,
diagnóstico na 17.

**Pré-requisitos.** Os módulos de object storage e de formatos de arquivo. Este
material assume que você sabe o que é um bucket, o que é Parquet e por que formato
colunar importa.

**Este módulo tem laboratório, e ele foi executado.** MinIO, Hive Metastore e
Trino, em Docker, sem nuvem. O `lab.json` registra cada laboratório com o comando
que provou, a saída e a data.

**Uma advertência sobre escala, e ela é o próprio conteúdo.** O laboratório roda
com 15 partições e 12.000 linhas. Não é preguiça de dimensionamento: acima de
cerca de 20 partições, o Hive Metastore desta pilha trava na fase de commit de um
CTAS particionado. A medição está na seção 17, e ela é a demonstração literal do
que a seção 10 ensina sobre overhead de metadados.

**Versões.** Verificado com Trino 479, Hive 4.0.0, PostgreSQL 16, MinIO
RELEASE.2025-02-03T21-03-04Z e Docker Compose v2.39.1, em 2026-07-31.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** o que particionamento faz no nível de armazenamento, e por que o
   engine consegue não ler o que não precisa.
2. **Demonstrar** partition pruning num plano de execução real, e dizer quanto ele
   economizou.
3. **Escolher** chave e granularidade de partição a partir do padrão de acesso e
   da cardinalidade, justificando pela pergunta que o negócio faz.
4. **Prever** os três modos de falha de uma escolha errada: small files, skew e
   hot partition.
5. **Calcular** o impacto de custo de uma decisão de particionamento com o modelo
   de cobrança por dado escaneado.
6. **Reconhecer** o limite de metadados de um catálogo Hive, tendo visto ele
   acontecer.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha já tem o dado bruto no
object storage e já sabe consultar. O problema agora é o preço da resposta.

O time de marketing pergunta, todos os dias: quantos cliques por campanha na
última semana? Sem particionamento, cada uma dessas perguntas varre o histórico
inteiro. A resposta é a mesma, o custo cresce todo mês, e ninguém percebe até a
fatura chegar.

**As caixas do pipeline, e onde estamos**

```
[Origem] -> [CDC] -> [Bronze] -> [Silver] -> [Gold] -> [Consumo]
               ^
               | (o orquestrador garante a ordem e os checks)
```

| Caixa | O que resolve |
|---|---|
| CDC | Representa mudança de forma auditável |
| Bronze | Dado bruto, fidelidade máxima, sem transformação |
| Silver | Dado limpo e padronizado, pronto para análise |
| Gold | Métrica e tabela de consumo |
| Engine de consulta | Valida e explora, sem armazenar |

Este módulo mora entre bronze e silver: é ali que a decisão de particionamento é
tomada, e é ela que decide o custo de tudo que vem depois.

**A modelagem mínima que precede a decisão**

Particionamento é decisão de armazenamento, e ela depende de saber o grão.

| Entidade | Grão | Chave | Tipo de mudança | Partição sugerida |
|---|---|---|---|---|
| events | 1 evento | event_id | append-only | event_date |
| campaigns | 1 campanha | campaign_id | upsert | created_date, se existir |
| costs | 1 campanha por dia | (campaign_id, cost_date) | upsert | cost_date |
| crm | 1 usuário | user_id | upsert | updated_at, se existir |

Se houver dado pessoal, marque e restrinja o acesso antes de promover para silver
ou gold. Isso é assunto do módulo de governança, e a decisão precisa ser tomada
aqui, não lá.

**As perguntas que guiam o módulo**

- Qual coluna define o tempo do dado?
- Qual coluna aparece no filtro das queries mais caras?
- Qual o volume por partição que essa escolha produz?

## 3. Por que particionamento importa

### 3.1 O cenário sem partição

**O que é**

Imagine uma tabela de eventos com 5 bilhões de registros cobrindo três anos. Você
precisa do total de cliques da última semana. Sem particionamento, a consulta
varre os 5 bilhões para achar os que caem na janela. Isso é uma varredura completa:
caro, lento, e crescendo linearmente com o volume.

Em serviços que cobram por byte escaneado, isso aparece na fatura. A seção 10 faz
a conta com número.

**O que o particionamento faz**

Particionar é organizar fisicamente o dado em subconjuntos, pelos valores de uma
ou mais colunas. Quando a consulta filtra pela coluna de partição, o engine lê
apenas as partições relevantes e ignora o resto.

No exemplo: com os eventos particionados por data, a consulta da última semana lê
7 partições de mais de mil. Em vez de 5 bilhões de registros, ela lê os da semana.
A redução é de uma ou duas ordens de magnitude.

### 3.2 A decisão que mais mexe no custo

**O equívoco comum**

Tratar particionamento como detalhe de implementação. É frequentemente a decisão
de projeto de dados com maior impacto direto em custo, e ela é tomada uma vez e
paga todo mês.

Uma escolha errada produz um destes três resultados:

| Erro | Consequência |
|---|---|
| Partição por coluna que nenhuma consulta filtra | Toda consulta continua varrendo tudo |
| Partição por coluna de altíssima cardinalidade | Dezenas de milhares de arquivos minúsculos |
| Partição por coluna desbalanceada | Uma partição com ordens de magnitude mais dado que as outras |

Os três têm nome, e as seções 7, 8 e 9 tratam de cada um.

## 4. Como o particionamento físico funciona

### 4.1 A metáfora do armário

**O que é**

Imagine 365 pastas, uma por dia do ano. Quando alguém pede os documentos de 15 de
janeiro, você vai direto na pasta e pega. Você não abre as outras 364.

É literalmente o que o particionamento faz no armazenamento.

### 4.2 Organização em prefixos

**Como funciona na prática**

No S3, e no MinIO que implementa a mesma API, o dado particionado fica em prefixos
que seguem a convenção Hive:

```
s3://silver/marketing/events/
  event_date=2025-01-10/
    20260731_190000_00001_abcde_...
  event_date=2025-01-11/
    20260731_190000_00001_abcde_...
```

Cada subdiretório `event_date=<valor>` é uma partição, e os arquivos dentro dele
contêm só os registros daquele dia. Os nomes de arquivo acima são do formato que o
Trino gera de verdade, observado no laboratório.

### 4.3 O papel do catálogo

**O que é**

O object storage não sabe que aqueles prefixos são partições. Ele vê objetos com
nomes. Quem dá significado é o Hive Metastore, que guarda:

- que existe uma tabela `events_silver` no schema `marketing`;
- onde ela está armazenada;
- que a coluna de partição é `event_date`;
- quais partições existem.

Quando o Trino recebe uma consulta com filtro de data, ele pergunta ao metastore
quais partições existem e quais casam com o filtro, **antes** de tocar qualquer
arquivo.

**O equívoco comum**

Gravar arquivo direto no bucket e esperar que a consulta o encontre. Se a partição
não foi registrada no metastore, ela não existe para o engine.

O registro acontece de duas formas: o próprio Trino escrevendo, ou você mandando
sincronizar. E aqui há uma pegadinha de dialeto que vale saber antes de procurar
no lugar errado. O comando do Hive é `MSCK REPAIR TABLE`, e **o Trino não tem esse
comando**. No Trino é um procedimento:

<!-- verificacao: nivel 1, conferido na documentacao do conector Hive do Trino, nao executado, 2026-07-31 -->

```sql
CALL hive.system.sync_partition_metadata(
    schema_name => 'marketing',
    table_name => 'events_silver',
    mode => 'ADD');
```

O modo `ADD` acrescenta as partições que existem no storage e não estão no
catálogo. Há também `DROP` e `FULL`. Material que manda rodar `MSCK REPAIR TABLE`
no Trino está misturando os dois dialetos.

### 4.4 A coluna de partição não vive dentro do arquivo

**O que é**

A coluna de partição em geral **não** é armazenada dentro dos arquivos Parquet. O
valor está codificado no caminho do prefixo. Isso economiza espaço: `2025-01-10`
não precisa aparecer em cada linha de um arquivo que já está dentro de
`event_date=2025-01-10/`.

**Como inspecionar**

O plano de execução do Trino diz isso explicitamente. Observado no laboratório:

<!-- verificacao: nivel 3, EXPLAIN executado no Trino 479, saida real, 2026-07-31 -->

```
event_id := event_id:string:REGULAR
event_date:date:PARTITION_KEY
```

`event_id` é `REGULAR`, ou seja, lido do arquivo. `event_date` é `PARTITION_KEY`,
ou seja, reconstruído a partir do caminho. É a prova da afirmação, na saída da
própria ferramenta.

## 5. Partition pruning, o mecanismo central

### 5.1 O que é

Partition pruning é o mecanismo pelo qual o engine identifica, a partir dos
filtros, quais partições precisa ler, e descarta as demais antes de abrir arquivo.
O nome vem de podar.

### 5.2 Como funciona, passo a passo

Considere a consulta:

<!-- verificacao: nivel 3, executada no Trino 479 contra a tabela do laboratorio, 2026-07-31 -->

```sql
SELECT campaign_id, COUNT(*) AS total_clicks
FROM hive.marketing.events_silver
WHERE event_date BETWEEN DATE '2025-01-10' AND DATE '2025-01-12'
  AND stage = 'click'
GROUP BY campaign_id;
```

O que o Trino faz:

1. Analisa o predicado de `event_date`.
2. Pergunta ao metastore quais partições existem e quais caem no intervalo.
3. Recebe a lista das três partições.
4. Envia requisições ao storage apenas para os arquivos dessas três.
5. Aplica o filtro de `stage` **dentro** dos arquivos lidos, porque `stage` não é
   coluna de partição.

### 5.3 O pruning só acontece na coluna de partição

**O equívoco comum**

Achar que qualquer filtro ativa o pruning. Só a coluna de partição elimina
partição. Filtro em outra coluna é aplicado depois, dentro do que já foi lido.

A implicação prática decide o projeto: **a coluna de partição deve ser a mais usada
como filtro nas consultas mais frequentes e mais caras.**

### 5.4 Pruning e pushdown

Existe otimização em mais de um nível, e vale saber a ordem:

| Nível | O que elimina |
|---|---|
| Partition pruning | Partições inteiras, sem abrir arquivo |
| File pruning | Arquivos individuais, em formatos como Iceberg |
| Row group pruning | Blocos dentro do Parquet, por estatística de mínimo e máximo |

Este módulo trata do primeiro. Ele é o que dá o maior ganho e o único que você
controla ao decidir a chave de partição.

### 5.5 Como inspecionar, e o que o Trino 479 realmente imprime

**Como inspecionar**

Material mais antigo manda procurar a palavra `Constraint` na linha do
`TableScan`. **O Trino 479 não imprime isso.** O que ele imprime é mais direto:
a lista de partições que serão lidas.

Com pruning, observado no laboratório:

<!-- verificacao: nivel 3, EXPLAIN executado no Trino 479, saida real, 2026-07-31 -->

```
└─ TableScan[table = hive:marketing:events_silver]
       Layout: [event_id:varchar]
       event_id := event_id:string:REGULAR
       event_date:date:PARTITION_KEY
           :: [[2025-01-10]]
```

Uma partição na lista. Sem pruning, filtrando por uma coluna comum, o plano muda
de forma e lista todas:

<!-- verificacao: nivel 3, EXPLAIN executado no Trino 479, saida real, 2026-07-31 -->

```
└─ ScanFilterProject[table = hive:marketing:events_silver, filterPredicate = (channel = varchar 'organic')]
       event_date:date:PARTITION_KEY
           :: [[2025-01-01], [2025-01-02], ... [2025-01-15]]
```

Duas diferenças para ler no plano: o nó deixa de ser `TableScan` e passa a ser
`ScanFilterProject` com `filterPredicate`, e a lista de partições passa de um
valor para quinze.

### 5.6 Quanto isso economiza, medido

**Como funciona na prática**

Mesma tabela, mesmo dado, dois filtros. Números de `EXPLAIN ANALYZE` reais:

| Medida | Com pruning | Sem pruning | Fator |
|---|---|---|---|
| Linhas lidas | 800 | 12.000 | 15x |
| Bytes lidos | 50,92 kB | 761,21 kB | 15x |
| Entrada física | 8,08 kB | 120,72 kB | 14,9x |
| Splits | 1 | 15 | 15x |
| CPU | 11,85 ms | 173,42 ms | 14,6x |
| Tempo de I/O físico | 3,80 ms | 77,31 ms | 20x |

O fator 15 não é coincidência: é a contagem de partições da tabela. Uma partição
lida em vez de quinze. Numa tabela com três anos por dia, o mesmo raciocínio dá um
fator na casa do milhar.

Repare que a consulta sem pruning ainda devolve o resultado certo. Ela só custa
quinze vezes mais para chegar nele.

## 6. Estratégias de particionamento

### 6.1 Por tempo

**O que é**

A estratégia mais comum em data lake. Faz sentido quando o dado tem dimensão
temporal forte, as consultas filtram por período, e o dado chega de forma
incremental sem atualizar partição antiga.

**A granularidade decide tudo**

| Granularidade | Problema |
|---|---|
| Por ano | Partição enorme, o pruning não ajuda consulta diária |
| Por hora ou minuto | Excesso de partições e arquivos minúsculos |
| Por dia | O equilíbrio mais comum em dado transacional |

Hierarquia temporal também é possível, e é útil quando você filtra tanto por mês
quanto por dia:

```
s3://bronze/events/
  year=2026/month=01/day=10/
  year=2026/month=01/day=11/
```

### 6.2 Por chave de negócio

Usado quando as consultas importantes filtram por uma dimensão como `country`,
`channel` ou `campaign_id`.

Particionar por país faz sentido se a maioria das consultas é por mercado, se os
países têm volume parecido, e se o número deles é baixo e estável.

### 6.3 Híbrido, chave composta

Combina tempo e chave de negócio:

```
s3://bronze/events/
  event_date=2025-01-10/country=BR/
  event_date=2025-01-10/country=US/
```

O ganho: consultas que filtram por data **e** país eliminam ainda mais partições.
O risco: o número de combinações multiplica, e o número de partições explode.

Este risco não é teórico neste laboratório. Veja a seção 17: 15 partições rodam em
10 segundos, e 25 travam o metastore. Uma chave composta de 15 datas por 5 países
já daria 75.

### 6.4 Não existe estratégia universalmente correta

A decisão vem do padrão de acesso real. As quatro perguntas que a resolvem:

- Qual coluna aparece mais nos filtros das consultas mais custosas?
- Qual a cardinalidade dessa coluna?
- Há risco de distribuição desigual?
- Qual o volume por partição que isso produz?

## 7. Cardinalidade e escolha de chave de partição

### 7.1 O que é cardinalidade

Cardinalidade é o número de valores distintos de uma coluna. `user_id` com milhões
de usuários é alta. `country` com dez países é baixa.

### 7.2 Por que alta cardinalidade quebra

**O que é**

Particionar por `user_id` numa tabela de 100 milhões de usuários dá 100 milhões de
partições, cada uma com pouquíssimos registros. Três problemas ao mesmo tempo:

| Problema | Por quê |
|---|---|
| Small files | Cada partição gera arquivo minúsculo, e o storage tem custo fixo por arquivo |
| Overhead de catálogo | O metastore guarda e indexa metadado de cada partição |
| Pruning inútil | Eliminar poucas partições de milhões não reduz o scan de forma relevante |

O segundo problema é o que a seção 17 mostra acontecendo, com número.

### 7.3 A faixa que funciona

Não existe número mágico. A prática de mercado indica que partição funciona bem
com cardinalidade entre 10 e 10.000 valores distintos. Abaixo de 10 o pruning é
limitado; acima de 10.000 o risco de small files e de overhead cresce.

Para coluna de alta cardinalidade que precisa ser filtrada com frequência, a
resposta não é partição, é organização interna do arquivo, como clustering ou
ordenação multidimensional, disponíveis em formatos de tabela mais novos.

### 7.4 O caso do domínio de marketing

| Coluna | Cardinalidade estimada | Serve como partição? |
|---|---|---|
| `event_date` | 365 por ano | Sim, o padrão clássico |
| `stage` | 4 a 10 | Sim, mas avaliar desequilíbrio |
| `campaign_id` | 100 a 10.000 | Depende do volume por campanha |
| `channel` | 5 a 50 | Sim, se o volume for equilibrado |
| `user_id` | Milhões | Não |

## 8. Skew de partição

### 8.1 O que é

Skew é o desequilíbrio de tamanho entre partições. Numa tabela particionada por
`stage`, se a maioria dos eventos é impressão, aquela partição fica muito maior
que as outras.

O laboratório tem skew embutido de propósito: a campanha `cmp_001` concentra cerca
de 35 por cento do tráfego. Se você particionasse por `campaign_id`, veria o
efeito.

### 8.2 Por que é um problema

Em engine distribuído, o trabalho é dividido entre workers. Se uma partição é
muito maior, o worker dela termina muito depois dos outros, e o tempo total da
consulta é o do mais lento. Isso se chama straggler.

Além da consulta, o skew complica a operação: reprocessar a partição grande é
desproporcionalmente caro, e estimar crescimento fica difícil.

### 8.3 Como detectar

**Como inspecionar**

O Trino expõe as partições como uma tabela de sistema:

<!-- verificacao: nivel 3, executado no Trino 479 contra a tabela do laboratorio, 2026-07-31 -->

```sql
SELECT * FROM hive.marketing."events_silver$partitions";
```

Se os tamanhos variarem em ordens de magnitude, há skew. No console do MinIO, em
`http://localhost:9001`, a comparação visual dos prefixos dá a mesma pista mais
rápido.

### 8.4 O que fazer

| Estratégia | Quando |
|---|---|
| Trocar a chave | O desequilíbrio é natural na coluna escolhida |
| Sub-particionar | Uma segunda dimensão equilibra a distribuição |
| Bucketing | Distribuir em N arquivos de tamanho parecido dentro da partição |
| Aceitar | O desequilíbrio é inevitável, e você otimiza a consulta da partição grande |

A última linha é uma resposta legítima, e dizer isso por escrito vale mais que
uma otimização que não vai acontecer.

## 9. Hot partitions

### 9.1 O que é, e por que é diferente de skew

Hot partition é uma partição que recebe volume desproporcional de **escritas
simultâneas**. Acontece em tabela particionada por tempo quando vários processos
escrevem no dia de hoje ao mesmo tempo.

| Fenômeno | Natureza |
|---|---|
| Skew | Problema de leitura, a partição é grande |
| Hot partition | Problema de escrita, a partição recebe muitos writers |

### 9.2 O caso clássico

Num pipeline quase em tempo real, vários workers escrevem em
`event_date=<hoje>` ao longo do dia. Cada microbatch gera um arquivo, e ao fim do
dia a partição tem centenas ou milhares de arquivos pequenos.

### 9.3 Mitigação

| Estratégia | Como |
|---|---|
| Compactação | Job periódico une os arquivos pequenos da partição em arquivos maiores |
| Área de staging | Os jobs escrevem fora da partição final, e um merge periódico consolida |
| Serialização pelo orquestrador | O orquestrador impede writers simultâneos na partição do dia |

Formatos de tabela mais novos têm compactação nativa e transacional. No Hive
clássico, que é o deste laboratório, o processo é manual.

## 10. Custo contra performance

### 10.1 O trade-off

Particionar resolve um problema e cria outro. Menos dado lido por consulta, e mais
metadado para gerenciar. Mais partições significa mais entradas no catálogo, e
operações que percorrem o schema inteiro ficam mais lentas.

Este módulo tem a demonstração literal disso na seção 17.

### 10.2 O problema dos small files

**O que é**

Cada arquivo no object storage tem custo fixo de operação. Se uma partição tem
1.000 arquivos de 1 KB, o engine faz 1.000 requisições para ler 1 MB. Comparado a
uma requisição para um arquivo de 1 MB, o desperdício é enorme.

**A regra prática**

Arquivos entre 128 MB e 1 GB são o alvo para consulta analítica em object storage.
Abaixo de 10 MB o overhead começa a aparecer; abaixo de 1 MB é problema. Isso é
heurística de mercado, não número de documentação.

**A tensão com a granularidade**

Particionar por hora dá 24 partições por dia; com volume baixo, cada uma tem
poucos MB e você criou o problema de small files. Particionar por mês resolve os
arquivos e mata o pruning diário.

A conta que resolve: se você sabe o volume diário, sabe qual granularidade deixa
cada partição com pelo menos alguns arquivos grandes.

### 10.3 A conta de custo, com o modelo por dado escaneado

**Como funciona na prática**

Serviços que consultam direto no object storage cobram por byte escaneado. A
página de preço do Athena usa 5 dólares por terabyte como taxa ilustrativa do
exemplo dela, e é essa taxa que os exercícios deste módulo usam.

Suponha a tabela `events` com 730 dias, 10 milhões de registros por dia e 200
bytes por registro em Parquet. Total de 1,46 TB.

| Cenário | Volume lido por consulta | Custo por consulta |
|---|---|---|
| Sem partição, filtro de 7 dias | 1,46 TB | 7,30 dólares |
| Particionado por dia, filtro de 7 dias | 7 de 730, cerca de 14 GB | 0,07 dólares |

Cem consultas por dia é a diferença entre 730 dólares e 7 dólares por dia. A
decisão foi tomada uma vez, no dia em que a tabela foi criada.

### 10.4 Overhead de catálogo

O Hive Metastore guarda uma entrada no banco relacional para cada partição. Com
milhares de partições, operações como listar partições e resolver schema ficam
mais lentas.

Formatos de tabela mais novos reduzem essa dependência ao manter o próprio
catálogo em arquivos de manifesto no storage.

## 11. A stack do laboratório

**MinIO, o object storage**

Implementa a API do S3. Para qualquer cliente que use o SDK do S3, é
indistinguível dele. Roda local, sem custo e sem conta em nuvem. O laboratório
usa três buckets: `bronze`, `silver` e `gold`.

**Hive Metastore, o catálogo**

Serviço que guarda metadado de tabela: nome, schema, localização, colunas de
partição e a lista de partições. Usa um banco relacional como backend, aqui um
PostgreSQL.

**Uma correção que vale registrar.** Na AWS, o Glue Data Catalog cumpre o mesmo
**papel**, e é comum dizer que ele "fala o mesmo protocolo Thrift". Não fala. O
Glue é acessado pela API da AWS, e no Trino isso é configuração diferente:

| Catálogo | Configuração no Trino |
|---|---|
| Hive Metastore | `hive.metastore=thrift`, com `hive.metastore.uri` |
| AWS Glue | `hive.metastore=glue`, com `hive.metastore.glue.region` |

O que muda para você: trocar de um para o outro é mudança de configuração do
conector, não apenas de endereço. O conceito de catálogo é o mesmo, o mecanismo de
acesso não.

**Trino, o engine de consulta**

Engine SQL distribuído para consulta analítica sobre object storage. Ele não
armazena nada: lê e processa. Conecta ao metastore via Thrift e ao MinIO via API
do S3.

**Como os três se conectam**

```
[Consulta] --> [Trino :8090]
                    |
                    |-- (1) metadado --> [Hive Metastore :9083] -> [PostgreSQL]
                    |
                    |-- (2) arquivos --> [MinIO :9000] -> [bronze/silver/gold]
```

O fluxo: a consulta chega ao Trino, ele pede o metadado ao metastore, decide quais
partições ler com base nos predicados, lê os arquivos dessas partições no MinIO, e
processa.

**Onde o orquestrador entra**

Nesta sessão o Airflow não sobe. O desenho do DAG é suficiente para conectar as
caixas: gerar o dado, carregar no bronze, construir a silver particionada, e rodar
as consultas de validação.

## 12. Laboratório

O laboratório roda em Docker, sem nuvem. Os runbooks em
`infrastructure/runbooks/` trazem o passo a passo, inclusive o reset de estado, que
não é opcional e a seção 17 explica por quê.

**Sobre a escala.** O gerador entrega 15 partições e 12.000 linhas por padrão.
Esse número é um teto medido, não uma preferência. A seção 17 tem a tabela.

### Lab 0: Gerar o dado e carregar no bronze

Pré-condição: Docker e Docker Compose v2, e cerca de 8 GB de memória livre.

```bash
cd engenharia_de_dados/modulos/particionamento-performance
python3 scripts/gerar_dados.py --destino infrastructure/dados
cd infrastructure
docker compose up -d
```

Saída esperada do gerador:

```
events.csv: 12000 linhas
events__cdc.csv: 15566 linhas
janela: 2025-01-01 a 2025-01-15, 15 particoes de event_date
```

Depois, com a pilha de pé, envie os arquivos ao MinIO:

```bash
docker run --rm --network mentoria-sessao-04-particionamento_default \
  -v "$PWD/dados":/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-02-08T19-14-21Z \
  cp /data/events.csv local/bronze/marketing/raw/events/
```

O gerador é determinístico, com semente fixa. Rodar duas vezes produz o mesmo
arquivo, e é por isso que esta apostila pode publicar contagens e esperar que elas
se reproduzam na sua máquina.

### Lab 1: Criar o schema e a tabela bronze

```sql
CREATE SCHEMA IF NOT EXISTS hive.marketing
WITH (location = 's3://bronze/marketing/');
```

```sql
CREATE TABLE hive.marketing.events_raw (
    event_id VARCHAR, event_date VARCHAR, event_ts VARCHAR,
    user_id VARCHAR, campaign_id VARCHAR, channel VARCHAR,
    device VARCHAR, country VARCHAR, stage VARCHAR, revenue VARCHAR
)
WITH (
    format = 'CSV',
    external_location = 's3://bronze/marketing/raw/events/',
    skip_header_line_count = 1
);
```

Saída esperada da contagem: `12000`.

O formato CSV no Hive aceita apenas `VARCHAR`. A tipagem entra na silver, via
`CAST`. Isso não é limitação do laboratório, é como o formato funciona.

### Lab 2: Criar a silver particionada

```sql
CREATE TABLE hive.marketing.events_silver
WITH (
    format = 'PARQUET',
    partitioned_by = ARRAY['event_date'],
    external_location = 's3://silver/marketing/events/'
) AS
SELECT
    event_id, user_id, campaign_id, channel, device, country, stage,
    TRY_CAST(revenue AS DOUBLE) AS revenue,
    CAST(event_date AS DATE) AS event_date
FROM hive.marketing.events_raw;
```

Saída esperada: `CREATE TABLE: 12000 rows`, em cerca de 18 segundos.

Repare que `event_date` é a **última** coluna do `SELECT`. A documentação do
conector Hive registra que o Hive exige que as colunas de partição sejam as últimas
colunas da tabela, e num CTAS é a ordem do `SELECT` que define a ordem da tabela.
Por isso a coluna de partição vai no fim.

### Lab 3: Listar as partições

```sql
SELECT count(*) AS particoes FROM hive.marketing."events_silver$partitions";
```

Saída esperada: `15`.

### Lab 4: Ver o pruning acontecer

```sql
EXPLAIN ANALYZE
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10';
```

Saída esperada, na linha de entrada do plano:

```
Input: 800 rows (50.92kB), Physical input: 8.08kB, Splits: 1
```

Um split, uma partição, 800 linhas.

### Lab 5: Ver a mesma consulta sem pruning

```sql
EXPLAIN ANALYZE
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE channel = 'organic';
```

Saída esperada:

```
Input: 12000 rows (761.21kB), Filtered: 80.12%, Physical input: 120.72kB, Splits: 15
```

Quinze splits, a tabela inteira lida, e 80 por cento do que foi lido descartado
pelo filtro. Compare com o Lab 4: mesma tabela, resultado correto nos dois, e
quinze vezes o custo.

Este é o laboratório central do módulo. Se você fizer só um, faça este junto com o
Lab 4.

### Lab 6: Derrubar e resetar

```bash
docker compose down --volumes
```

A opção `--volumes` não é detalhe. Sem ela, o MinIO e o metastore guardam o estado
da execução anterior, e o `CREATE TABLE IF NOT EXISTS` da próxima vez encontra a
tabela já registrada, não faz nada, e devolve dado velho como se fosse novo. A
seção 17 conta o caso real.

## 13. Análise do domínio de marketing

Com a tabela criada, as perguntas típicas de um analista de marketing, e o que
cada uma faz com as partições.

**Cliques por campanha e por dia, a consulta frequente**

```sql
SELECT event_date, campaign_id, COUNT(*) AS total_clicks
FROM hive.marketing.events_silver
WHERE event_date BETWEEN DATE '2025-01-10' AND DATE '2025-01-12'
  AND stage = 'click'
GROUP BY event_date, campaign_id
ORDER BY event_date, campaign_id;
```

Filtro de partição em `event_date`, filtro de coluna em `stage`. O Trino poda as
partições fora do intervalo e depois aplica `stage` no que sobrou.

**Usuários únicos por campanha**

```sql
SELECT campaign_id, COUNT(DISTINCT user_id) AS unique_users
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10'
GROUP BY campaign_id;
```

**O ponto de aprendizado**

Todas as consultas de marketing são naturalmente filtradas por data. "Me dá os
dados do dia X, da semana Y" é o padrão dominante em analytics. Por isso partição
por data é a decisão padrão para tabela de evento, e a justificativa vem do padrão
de acesso, não do hábito.

**Quando particionar por campanha em vez de data**

Se a consulta dominante fosse "todos os eventos da campanha A desde sempre",
particionar por `campaign_id` faria mais sentido. Esse padrão é menos comum
porque o número de campanhas é alto e variável, e porque campanha tem ciclo de
vida curto enquanto a análise continua usando janela de tempo.

## 14. Exercícios e entregáveis

**Exercício 1: Plano de particionamento**

Objetivo: escolher chave e granularidade a partir do padrão de acesso.

Contexto: quatro tabelas do projeto.

| Tabela | Volume estimado | Consultas mais comuns |
|---|---|---|
| `events` | 10 M por dia | Por data, por campanha, por stage |
| `campaigns` | 500 por mês | Por data de criação, por status |
| `costs` | 1.000 por dia | Por data, por campanha |
| `crm` | 200 K no total, atualizado diariamente | Por segmento, por data de atualização |

Entregável: proposta por tabela com chave escolhida, justificativa pelo padrão de
acesso e pela cardinalidade, granularidade, e riscos identificados entre small
files, skew e hot partition.

**Exercício 2: Análise de custo**

Objetivo: ligar decisão técnica a linha de fatura.

Contexto: os volumes do exercício 1, e a taxa ilustrativa de 5 dólares por
terabyte escaneado.

Entregável: tabela comparativa de custo mensal por tabela, nos dois cenários, com
e sem partição, assumindo 100 consultas por dia. Diga também qual das quatro
tabelas não vale particionar, e por quê.

**Exercício 3: Medir o seu próprio pruning**

Objetivo: usar o plano de execução como instrumento, não como enfeite.

Contexto: a tabela do laboratório.

Entregável: três consultas suas, uma com pruning, uma sem, e uma com filtro
composto de partição e coluna comum. Para cada uma, o `Input`, o `Physical input`
e o número de `Splits` do `EXPLAIN ANALYZE`, mais uma frase explicando o número.

**Exercício 4: A última versão de cada evento**

Objetivo: aplicar CDC sobre dado particionado.

Contexto: o `events__cdc.csv` que o gerador produz tem um insert por evento, mais
update ou delete para parte deles. São 15.566 linhas para 12.000 eventos.

Entregável: uma tabela `events_latest` com a última versão de cada `event_id`,
descartando o que foi deletado, particionada por `event_date`. A dica está em
função de janela com `row_number()`. Diga quantas linhas sobraram e por quê.

Este exercício não é um laboratório desta apostila porque não foi executado na
verificação. Rodar é parte do exercício.

**Exercício 5: Mini ADR da estratégia**

Objetivo: registrar decisão de forma que outra pessoa entenda em seis meses.

Entregável: um ADR curto com título, status, contexto, decisão, pelo menos duas
alternativas consideradas com seus trade-offs, e consequências para o pipeline.

## 15. Mini-desafio com solução

**Enunciado**

O time quer acrescentar `country` à chave de partição, para acelerar as análises
por mercado. São 5 países no dado do laboratório e 15 datas.

Avalie a proposta. Se recomendar, diga o que muda. Se recusar, diga o que fazer no
lugar.

**Dicas**

- Multiplique antes de opinar.
- A seção 17 tem um número que decide.
- Volume por partição é o critério que ninguém lembra de aplicar.

**Gabarito comentado**

Recuso, e por dois motivos independentes.

O primeiro é aritmético e imediato: 15 datas por 5 países dá 75 partições. A
medição da seção 17 mostra que este laboratório trava acima de cerca de 20. A
proposta não roda no ambiente onde ela seria testada.

O segundo é o que importa em produção, onde o catálogo aguenta. Com 12.000 linhas
divididas em 75 partições, cada uma fica com cerca de 160 linhas, alguns kilobytes
de Parquet. A regra da seção 10 pede partição com arquivos na casa das centenas de
megabytes. Você teria criado o problema de small files para resolver um problema
de pruning que talvez não exista.

O que fazer no lugar, em ordem: primeiro, medir. Quantas das consultas realmente
filtram por país? Se for uma minoria, `country` não deveria ser partição, deveria
ser apenas uma coluna, e o filtro dela é aplicado depois do pruning por data, que
já reduziu 15 vezes.

Se a análise por mercado for dominante mesmo, a alternativa é ordenar o dado por
`country` dentro de cada partição de data, para que a estatística de mínimo e
máximo do Parquet permita pular blocos. Isso é pruning no nível de row group, da
seção 5.4, e não cria partição nova nenhuma.

**Interpretação**

A resposta fraca aceita a proposta porque "mais pruning é melhor". A resposta boa
multiplica 15 por 5 antes de responder. A excelente percebe que a pergunta certa
não é "particionar por país?", é "quantas consultas filtram por país?", e que
ninguém mediu isso.

## 16. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Mecanismo | Descreve partição como pasta | Explica o papel do catálogo no pruning | Sabe que a coluna de partição não está no arquivo, e prova no plano |
| Pruning | Acha que qualquer filtro poda | Sabe que só a coluna de partição poda | Lê o plano e diz quanto economizou |
| Escolha de chave | Escolhe por hábito | Escolhe pelo padrão de acesso e cardinalidade | Calcula o volume por partição antes de decidir |
| Modos de falha | Não distingue os três | Nomeia small files, skew e hot partition | Prevê qual deles a sua escolha vai produzir |
| Custo | Trata como assunto financeiro | Faz a conta por dado escaneado | Ordena as decisões por impacto na fatura |
| Limite de catálogo | Não sabe que existe | Sabe que muitas partições degradam | Reconhece a assinatura do travamento e sabe o teto do ambiente |
| Honestidade técnica | Publica número que não mediu | Cita fonte e data | Declara o que não foi verificado |

Checklist para a call:

- [ ] Tabela silver particionada criada a partir do dado do MinIO.
- [ ] Pruning demonstrado no `EXPLAIN ANALYZE`, com o número de splits.
- [ ] Plano de particionamento das quatro tabelas do exercício 1.
- [ ] Conta de custo feita para pelo menos uma tabela.
- [ ] Explicou por que 75 partições é uma má ideia neste ambiente.

## 17. Erros comuns e como corrigir

**A pilha trava e nenhum log diz nada**

Sintoma: um `CREATE TABLE ... AS SELECT` particionado nunca termina. A query fica
em `FINISHING`, e depois de um tempo o metastore para de responder até para um
`SHOW SCHEMAS`, com `SocketTimeoutException`. CPU e memória ociosos nos quatro
containers, e nenhum erro em nenhum log.

Causa: a fase de commit de partições do metastore. A variável é a **contagem de
partições**, não o volume de dado. Medido em 2026-07-31, mantendo as linhas fixas
para isolar:

| Partições | Linhas | Resultado |
|---|---|---|
| 5 | 1.000 | concluiu em 5 s |
| 5 | 12.000 | concluiu em 11 s |
| 15 | 12.000 | concluiu em 10 s |
| 25 | 12.000 | travou |
| 30 | 6.000 | travou |
| 30 | 60.000 | travou |

O volume de linhas variou 12 vezes sem efeito. Correção: ficar abaixo de cerca de
20 partições por CTAS neste ambiente. É por isso que o gerador entrega 15 por
padrão.

Repare no que isso significa: a seção 10 desta apostila ensina que muitas
partições sobrecarregam o catálogo. Este travamento é essa lição acontecendo no
próprio laboratório, com número. É o material mais honesto do módulo.

**O `IF NOT EXISTS` devolve dado de meses atrás**

Sintoma: o `CREATE TABLE IF NOT EXISTS` responde `CREATE TABLE: 0 rows`, e a
contagem depois não bate com a origem.

Causa: os volumes do Docker persistem entre execuções. A tabela já estava
registrada no metastore de uma sessão anterior, o comando não fez nada, e a
consulta leu o dado antigo.

Caso real: na verificação de 2026-07-31, o laboratório devolveu 2.000 linhas em 14
partições quando a origem tinha 60.000 em 30. O dado era de 2026-03-18, e as 14 de
30 partições eram justamente a assinatura do travamento acima, quatro meses antes.

Correção: `docker compose down --volumes` ao terminar, como no Lab 6. Se
desconfiar, conte as linhas e compare com o que o gerador reportou.

**A partição existe no storage e a consulta não a encontra**

Sintoma: os arquivos estão no bucket, e a consulta devolve vazio.

Causa: a partição não foi registrada no catálogo. O storage não avisa o metastore.

Correção: escrever pelo próprio engine, ou sincronizar com
`CALL hive.system.sync_partition_metadata(..., mode => 'ADD')`. No Trino não existe
`MSCK REPAIR TABLE`, que é o comando equivalente do Hive.

**A consulta filtra e continua caríssima**

Sintoma: você acrescentou `WHERE` e o custo não caiu.

Causa: o filtro não é na coluna de partição. Ele é aplicado depois, no dado já
lido.

Correção: conferir o plano. Se o nó é `ScanFilterProject` com `filterPredicate` e a
lista de `PARTITION_KEY` traz todas as partições, não houve pruning.

**Muitos arquivos minúsculos**

Sintoma: a consulta é lenta apesar do pruning funcionar.

Causa: granularidade fina demais, ou muitos writers na mesma partição.

Correção: compactar, e reavaliar a granularidade contra o volume diário real.

**A coluna de partição na posição errada no CTAS**

Sintoma: erro ao criar a tabela particionada.

Causa: no Trino, num CTAS particionado, a coluna de partição precisa ser a última
do `SELECT`.

Correção: mover a coluna para o fim da lista, como está no Lab 2.

## 18. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 1 e 3. O terceiro exige rodar o laboratório, e é o que fixa o
plano de execução como instrumento.

**O que estudar em seguida, dentro da trilha**

O módulo de formatos e tipos de tabela é o par natural deste: formatos de tabela
mais novos resolvem parte do que aqui é manual, da compactação ao catálogo. O
módulo de cloud para dados retoma a conta de custo desta seção 10 com as classes
de armazenamento.

O módulo de transformação com dbt é onde essas decisões passam a viver em código
versionado, com a materialização escolhida por custo e frequência.

**O que aprofundar por conta**

Rode o laboratório com 25 partições e veja o travamento com os seus olhos. Saber
reconhecer a assinatura vale mais que evitar o caso.

**O que não perseguir agora**

Ajuste fino de configuração do metastore e bucketing no Hive. Os dois são
trabalho de plataforma, e o retorno para você hoje é menor que dominar a escolha
de chave.

## 19. Glossário

| Termo | Significado |
|---|---|
| Bucketing | Distribuição do dado em N arquivos de tamanho parecido dentro da partição |
| Cardinalidade | Número de valores distintos de uma coluna |
| Catálogo | Serviço que guarda metadado de tabela e de partição |
| Compactação | Processo que une arquivos pequenos de uma partição em arquivos maiores |
| CTAS | `CREATE TABLE AS SELECT`, cria a tabela a partir do resultado de uma consulta |
| Full scan | Varredura completa da tabela, sem eliminar partição |
| Hot partition | Partição que recebe volume desproporcional de escritas simultâneas |
| Partição | Subconjunto físico do dado, definido pelo valor de uma ou mais colunas |
| Partition pruning | Eliminação de partições a partir dos filtros, antes de abrir arquivo |
| Pushdown | Empurrar o filtro para o nível mais baixo possível de leitura |
| Row group | Bloco interno de um arquivo Parquet, com estatística de mínimo e máximo |
| Skew | Desequilíbrio de tamanho entre partições |
| Small files | Excesso de arquivos minúsculos, que anula o ganho do particionamento |
| Split | Unidade de trabalho de leitura que o engine distribui entre workers |
| Straggler | Worker que termina muito depois dos outros e atrasa a consulta inteira |

## Referências

Documentação oficial, consultada em 2026-07-31:

- Conector Hive do Trino: https://trino.io/docs/current/connector/hive.html
- Documentação do MinIO: https://min.io/docs/
- Preço do Amazon Athena, origem da taxa ilustrativa por terabyte: https://aws.amazon.com/athena/pricing/

Leitura complementar, não conferida nesta revisão:

- Data Storage Design Patterns, capítulo sobre tabela particionada e o trade-off
  entre granularidade e overhead.
- Data Observability Design Patterns, capítulo sobre métricas operacionais de
  partição, como tamanho e número de arquivos.

## Fontes verificadas (2026-07-31)

- Toda a pilha do laboratório foi executada de verdade em 2026-07-31, com Trino
  479, Hive 4.0.0, PostgreSQL 16, MinIO RELEASE.2025-02-03T21-03-04Z e Docker
  Compose v2.39.1. Os laboratórios 0 a 6 estão registrados no `lab.json` com o
  comando que provou cada um e a saída observada.
- O ganho do partition pruning foi medido com `EXPLAIN ANALYZE` na mesma tabela,
  variando apenas o filtro: com pruning, 800 linhas e 50,92 kB em 1 split; sem
  pruning, 12.000 linhas e 761,21 kB em 15 splits. O fator 15 corresponde à
  contagem de partições da tabela.
- O plano de execução do Trino 479 classifica `event_date` como `PARTITION_KEY` e
  `event_id` como `REGULAR`, o que confirma que a coluna de partição é
  reconstruída do caminho e não lida do arquivo Parquet.
- O Trino 479 **não** imprime `Constraint` no `TableScan`, ao contrário do que
  material mais antigo afirma. Ele imprime a lista de partições sob
  `event_date:date:PARTITION_KEY`, e troca o nó por `ScanFilterProject` quando o
  filtro é de coluna comum. As duas saídas estão transcritas na seção 5.5, como
  observadas.
- O teto de partições deste ambiente foi medido isolando a variável: 5 partições
  com 1.000 e com 12.000 linhas concluíram em 5 e 11 segundos; 15 partições com
  12.000 linhas concluíram em 10 segundos; 25 partições com 12.000 linhas, 30 com
  6.000 e 30 com 60.000 travaram na fase de commit, com o metastore deixando de
  responder. O volume de linhas variou 12 vezes sem efeito.
- O caso do `IF NOT EXISTS` devolvendo dado antigo foi observado: os volumes
  persistidos de 2026-03-18 fizeram o comando responder `CREATE TABLE: 0 rows` e a
  consulta devolver 2.000 linhas em 14 partições, quando a origem tinha 60.000 em
  30 partições.
- A taxa de 5 dólares por terabyte escaneado usada nas contas da seção 10 e do
  exercício 2 é a taxa ilustrativa que a própria página de preço do Athena usa no
  exemplo dela. O preço por região não foi conferido nesta data e não é afirmado
  aqui. https://aws.amazon.com/athena/pricing/
- A faixa de 128 MB a 1 GB por arquivo e a faixa de cardinalidade entre 10 e
  10.000 valores são heurísticas de mercado, não números de documentação, e estão
  declaradas como tal no texto.
- A documentação do conector Hive do Trino registra que o Hive exige que as colunas
  de partição sejam as últimas colunas da tabela. O CTAS do Lab 2 respeita isso, e
  foi executado com sucesso. O comportamento ao inverter a ordem **não** foi
  testado, e por isso esta apostila não afirma qual erro aparece.
  https://trino.io/docs/current/connector/hive.html
- O Trino não tem `MSCK REPAIR TABLE`. O equivalente é o procedimento
  `system.sync_partition_metadata`, com modos `ADD`, `DROP` e `FULL`, sendo o `ADD`
  o que acrescenta partições presentes no storage e ausentes no catálogo. Conferido
  na documentação e não executado.
  https://trino.io/docs/current/connector/hive.html
- O AWS Glue Data Catalog **não** é acessado pelo protocolo Thrift do Hive
  Metastore. No Trino, os dois são tipos distintos de metastore:
  `hive.metastore=thrift`, com `hive.metastore.uri`, contra
  `hive.metastore=glue`, com `hive.metastore.glue.region`. A versão anterior desta
  apostila afirmava que o Glue era compatível com o mesmo protocolo Thrift na
  porta 9083, e isso está errado.
  https://trino.io/docs/current/object-storage/metastores.html
- O exercício 4, de aplicar CDC sobre dado particionado, **não** foi executado na
  verificação, e por isso não é um laboratório desta apostila. O arquivo de CDC que
  o gerador produz tem 15.566 linhas para 12.000 eventos, número que foi conferido
  na geração.
