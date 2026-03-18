# Apostila — Sessão 04: Particionamento + integração do pipeline

> Estratégias de particionamento, partition pruning, skew e laboratório integrado com CDC, Trino, MinIO e Hive Metastore.
> Conduzida por Iuri Zambotto com Paulo Shindi. Mentorado: Aurelius Oliveira.

---

## Sumário

0. Visão integrada do Projeto 1 (as caixinhas)
0.1 Modelagem mínima antes do particionamento
1. Por que particionamento importa
2. Como o particionamento físico funciona
3. Partition pruning — o mecanismo central
4. Estratégias de particionamento
5. Cardinalidade e escolha de chave de partição
6. Skew de partição
7. Hot partitions
8. Custo versus performance
9. A stack do laboratório: MinIO, Hive Metastore, Trino e o papel do Airflow
10. Laboratório integrado: CDC → MinIO → Trino → particionamento
11. Análise do domínio de marketing
12. Exercícios e entregáveis

---

## 0. Visão integrada do Projeto 1 (as caixinhas)

Antes de escolher partição, o mentorado precisa enxergar o projeto como um todo.

**Mapa simplificado do pipeline**

```
[Origem] -> [CDC] -> [Bronze] -> [Silver] -> [Gold] -> [Consumo]
               ^
               | (Airflow orquestra a ordem e os checks)
```

**O que cada caixa resolve**

- **CDC**: representa mudanças (insert/update/delete) de forma auditável.
- **Bronze**: dados brutos, sem transformação (fidelidade máxima).
- **Silver**: dados limpos e padronizados (prontos para análise).
- **Gold**: métricas e tabelas de consumo.
- **Trino**: motor de consulta para validar e explorar.

**Perguntas guia (pensar o todo)**

- Qual problema de negócio estamos resolvendo?
- Qual o grão de cada tabela?
- Onde os dados nascem e onde precisam chegar?
- O que precisa ser idempotente (e onde)?
- Qual coluna define o tempo do dado (event_date, updated_at)?

## 0.1 Modelagem mínima antes do particionamento

Particionamento é decisão de armazenamento. Antes disso, precisamos do básico da modelagem.

| Entidade | Grão | Chave principal | Tipo de mudança | Camada base | Partição sugerida |
|---|---|---|---|---|---|
| events | 1 evento | event_id | append-only | bronze/silver | event_date |
| campaigns | 1 campanha | campaign_id | upsert | bronze/silver | created_date (se existir) |
| costs | 1 campanha x dia | (campaign_id, cost_date) | upsert | bronze/silver | cost_date |
| crm | 1 usuário | user_id | upsert | bronze/silver | updated_at (se existir) |
| users | 1 usuário | user_id | upsert | bronze/silver | updated_at (se existir) |

**Nota de PII:** se existir dado sensível (ex.: email, telefone), marcar e limitar acesso antes de promover para silver/gold.

---

## 1. Por que particionamento importa

Antes de falar sobre técnica, vale entender o problema que o particionamento resolve.

**O cenário sem particionamento**

Imagine uma tabela de eventos de uma plataforma de e-commerce com 5 bilhões de registros, cobrindo três anos de histórico. Você precisa calcular o total de cliques da última semana. Sem particionamento, a query precisa varrer todos os 5 bilhões de registros para encontrar os que caem na janela de tempo solicitada. Isso é um *full table scan*: caro, lento, e que cresce linearmente com o volume de dados.

Em sistemas como Athena (serviço gerenciado da AWS sobre o Presto/Trino), você paga por byte escaneado. Um full scan em 5 bilhões de registros pode custar dezenas de dólares por consulta. Multiplique isso por centenas de consultas por dia e o custo torna-se inviável.

**O que o particionamento faz**

Particionamento é a prática de organizar fisicamente os dados em subconjuntos (partições) com base nos valores de uma ou mais colunas. Quando o engine de consulta precisa responder a uma query com filtro sobre a coluna de partição, ele consulta apenas as partições relevantes, ignorando todo o resto.

No exemplo acima: se os eventos estão particionados por data, a query da última semana lê apenas 7 partições de 3 anos (mais de 1000 partições). Em vez de varrer 5 bilhões de registros, o engine lê apenas os da última semana — talvez 30 ou 40 milhões. A redução de custo e de latência é de uma ou duas ordens de magnitude.

**A decisão que mais impacta o custo do datalake**

Particionamento é, frequentemente, a decisão de design de dados com maior impacto direto em custo. Uma escolha errada de chave de partição pode:

- Fazer com que todas as queries continuem sendo full scans (partição com alta cardinalidade que nenhuma query usa como filtro).
- Gerar dezenas de milhares de arquivos minúsculos (small files), degradando o próprio mecanismo que deveria melhorar a performance.
- Criar desequilíbrio de tamanho entre partições (*skew*), onde uma partição tem 1000x mais dados que outra.

Esta sessão cobre essas decisões em detalhe, com laboratório prático.

**Referência do livro (Cap. 8 — Data Storage Design Patterns)**

O capítulo 8 descreve o padrão *Partitioned Table* como fundamento de qualquer estratégia de storage em larga escala. A premissa é simples: o acesso aos dados deve ser O(1) em relação ao volume total sempre que possível. Particionar por uma coluna que é filtrada sistematicamente é a forma mais direta de atingir isso.

---

## 2. Como o particionamento físico funciona

**A metáfora do armário de arquivos**

Antes de entrar no modelo S3/MinIO, vale a metáfora de um armário físico de arquivos. Imagine que você tem 365 pastas, uma para cada dia do ano. Quando alguém pede os documentos de 15 de janeiro, você vai diretamente na pasta "2026-01-15" e pega. Você não abre cada pasta do ano para procurar.

Isso é exatamente o que o particionamento faz no nível de storage.

**Organização em diretórios no S3/MinIO**

Em sistemas como o S3 (e o MinIO, que é compatível com S3), os dados particionados ficam organizados em prefixos de caminho que seguem a convenção Hive. Por exemplo, uma tabela de eventos particionada por `event_date` seria armazenada assim:

```
s3://bronze/marketing/events/
  event_date=2026-01-10/
    part-00000-abc123.parquet
    part-00001-def456.parquet
  event_date=2026-01-11/
    part-00000-ghi789.parquet
  event_date=2026-01-12/
    part-00000-jkl012.parquet
```

Cada subdiretório `event_date=<valor>` é uma partição. Os arquivos dentro dele contêm apenas os registros daquele dia específico.

**O papel do Hive Metastore**

O S3 não sabe que aqueles diretórios são partições de uma tabela. Ele enxerga apenas objetos com prefixos de caminho. Quem dá significado a essa estrutura é o Hive Metastore.

O Hive Metastore é um serviço que mantém um catálogo de metadados. Ele sabe:

- Que existe uma tabela chamada `events` no schema `marketing`.
- Que essa tabela está armazenada em `s3://bronze/marketing/events/`.
- Que a coluna de partição é `event_date`.
- Quais partições existem, com seus caminhos e estatísticas.

Quando o Trino recebe uma query como `SELECT * FROM hive.marketing.events WHERE event_date = '2026-01-10'`, ele consulta o Hive Metastore para descobrir quais partições existem e quais se encaixam no filtro antes de tocar qualquer arquivo no MinIO.

**Registro de partições**

Para que o Metastore saiba que uma partição existe, ela precisa ser registrada. Isso acontece de forma automática quando:

- Você usa `INSERT INTO` via Trino (o Trino registra a partição no metastore após gravar os arquivos).
- Você executa `MSCK REPAIR TABLE` manualmente (escaneia o S3 e registra partições existentes).

Se você gravar arquivos diretamente no S3 sem registrar no metastore, as queries não encontrarão os dados.

**O arquivo Parquet e a coluna de partição**

Um detalhe importante: a coluna de partição (`event_date`, neste exemplo) geralmente **não é armazenada dentro dos arquivos Parquet de cada partição**. Ela está codificada no próprio caminho do diretório. Isso economiza espaço e evita redundância — o valor `2026-01-10` não precisa aparecer em cada linha de um arquivo que já está dentro de `event_date=2026-01-10/`.

Quando o engine faz o merge dos dados com o metadado de partição ao retornar resultados, ele reconstrói a coluna automaticamente a partir do caminho.

---

## 3. Partition pruning — o mecanismo central

**O que é partition pruning**

Partition pruning (ou partition elimination) é o mecanismo pelo qual o engine de consulta identifica, a partir dos filtros da query, quais partições precisam ser lidas e descarta todas as demais antes de tocar qualquer arquivo.

O nome "pruning" vem de "podar" — como podar galhos desnecessários de uma árvore.

**Como funciona na prática**

Considere a query:

```sql
SELECT campaign_id, COUNT(*) AS total_clicks
FROM hive.marketing.events
WHERE event_date BETWEEN DATE '2026-01-10' AND DATE '2026-01-12'
  AND event_type = 'click'
GROUP BY campaign_id;
```

O Trino processa esta query assim:

1. Analisa o predicado `event_date BETWEEN ...`.
2. Consulta o Hive Metastore: quais partições existem e quais caem no intervalo?
3. Recebe a lista: `event_date=2026-01-10`, `event_date=2026-01-11`, `event_date=2026-01-12`.
4. Ignora todas as outras partições e envia requests ao MinIO apenas para os arquivos dessas três partições.
5. Aplica o filtro `event_type = 'click'` dentro dos arquivos lidos (filtro de coluna, não de partição).

Resultado: em vez de ler todos os dados históricos, o engine lê apenas 3 dias.

**Pruning só funciona na coluna de partição**

Um equívoco comum é achar que qualquer filtro ativa o pruning. Só a coluna de partição pode ativar o pruning. Filtros em outras colunas (`event_type`, `user_id`, `campaign_id`) não eliminam partições — eles aplicam filtros dentro dos arquivos já carregados.

Isso tem uma implicação prática importante: a coluna de partição deve ser aquela mais usada como filtro nas queries mais frequentes e mais caras do sistema.

**Pruning e Pushdown — conceitos relacionados**

Em engines modernos como o Trino, existe também o *pushdown* de predicados para o nível de arquivo. O Parquet, por exemplo, armazena estatísticas de min/max por *row group*. O Trino pode usar essas estatísticas para pular row groups inteiros dentro de um arquivo Parquet, mesmo após o pruning de partições.

A hierarquia de otimização é:

1. Partition pruning: elimina partições inteiras (não toca os arquivos).
2. File pruning: em formatos como Iceberg, elimina arquivos individuais.
3. Row group pruning: usa estatísticas de min/max dentro de arquivos Parquet.

Para a sessão 04, o foco é no nível de partição.

**Como inspecionar o pruning com EXPLAIN**

No Trino, você pode usar `EXPLAIN` para ver se o engine está fazendo pruning:

```sql
EXPLAIN
SELECT *
FROM hive.marketing.events
WHERE event_date = DATE '2026-01-10';
```

A saída mostra o plano de execução. Quando o pruning acontece, você vê algo como:

```
TableScan[hive:marketing:events]
    Constraint: event_date IN (2026-01-10)
```

Isso confirma que o engine só vai ler a partição `event_date=2026-01-10`.

---

## 4. Estratégias de particionamento

**Particionamento por tempo**

A estratégia mais comum em datalakes. Faz sentido quando:

- Os dados têm uma dimensão temporal forte (eventos, transações, logs).
- As queries mais frequentes filtram por período de tempo (dia, semana, mês).
- Os dados chegam de forma incremental e nunca são atualizados em partições antigas.

A granularidade do particionamento por tempo deve ser escolhida com cuidado:

- **Muito grosso (por ano):** cada partição acumula volume enorme, reduzindo o benefício do pruning para queries diárias.
- **Muito fino (por hora ou por minuto):** gera excesso de partições e arquivos minúsculos, aumentando overhead de metadados.
- **Por dia:** o equilíbrio mais comum para dados transacionais. Uma partição por dia é gerenciável, e a maioria das queries operacionais filtra por dia ou intervalos de dias.

Exemplo de hierarquia temporal:

```
s3://bronze/events/
  year=2026/month=01/day=10/
  year=2026/month=01/day=11/
  year=2026/month=02/day=01/
```

Esta hierarquia é útil quando você frequentemente filtra por mês (poda todas as partições de outros meses) ou por dia (poda até o nível mais granular).

**Particionamento por chave de negócio**

Usado quando as queries mais importantes filtram por uma dimensão de negócio específica, como `country`, `category`, `channel` ou `campaign_id`.

Por exemplo, em uma plataforma multi-país, particionar por `country` faz sentido se:

- A maioria das queries é scoped por país (analytics por mercado).
- Cada país tem volume similar (sem skew).
- O número de países é fixo e baixo (poucos valores, portanto poucos arquivos por partição).

**Particionamento híbrido (chave composta)**

Combina duas dimensões, tipicamente tempo + chave de negócio:

```
s3://bronze/events/
  event_date=2026-01-10/country=BR/
  event_date=2026-01-10/country=US/
  event_date=2026-01-11/country=BR/
```

O benefício: queries que filtram por data **e** país eliminam ainda mais partições. O risco: se o número de combinações for grande, o número de partições pode explodir, criando overhead de metadados.

**Não existe estratégia universalmente correta**

A decisão de particionamento deve ser orientada pelos padrões de acesso reais do sistema. Perguntas que guiam a decisão:

- Qual coluna aparece mais frequentemente nos filtros das queries mais custosas?
- Qual a cardinalidade dessa coluna? (número de valores distintos)
- Há risco de skew? (valores com distribuição muito desigual)
- Qual o volume médio por partição? (objetivo: partições entre 128 MB e 1 GB)

---

## 5. Cardinalidade e escolha de chave de partição

**O que é cardinalidade**

Cardinalidade é o número de valores distintos de uma coluna. Alta cardinalidade significa muitos valores distintos (ex: `user_id` com milhões de usuários). Baixa cardinalidade significa poucos valores (ex: `country` com 10 países, `event_type` com 5 tipos).

**Por que alta cardinalidade é problemática para partição**

Se você particionar por `user_id` em uma tabela de 100 milhões de usuários distintos, terá 100 milhões de partições. Cada partição terá, em média, pouquíssimos registros. Os problemas resultantes são:

- **Small files problem:** cada partição gera um ou mais arquivos minúsculos. O S3 e o HDFS têm overhead fixo por arquivo (requests, metadata lookups). Milhões de arquivos pequenos degradam drasticamente a performance de qualquer operação sobre o dataset.
- **Overhead de metastore:** o Hive Metastore precisa armazenar e indexar os metadados de cada partição. Com 100 milhões de partições, o metastore fica lento e instável.
- **Pruning ineficaz:** em alta cardinalidade, o pruning reduz pouco o scan (você elimina poucas partições do total). O custo de gerenciar as partições supera o benefício.

**A faixa ideal de cardinalidade para partição**

Não existe um número mágico, mas a prática do mercado indica que partições funcionam bem com cardinalidade entre 10 e 10.000 valores distintos. Abaixo de 10, o pruning é limitado. Acima de 10.000, o risco de small files e overhead de metadados cresce.

Para colunas de alta cardinalidade que precisam ser filtradas com frequência, a solução adequada não é a partição, mas o *clustering* ou o *Z-ordering* (disponível em formatos como Delta e Iceberg) — técnicas que organizam os dados dentro de arquivos para melhorar o pruning a nível de row group.

**Exemplos do domínio de marketing**

| Coluna | Cardinalidade estimada | Adequada para partição? |
|---|---|---|
| `event_date` | 365 por ano | Sim — padrão clássico |
| `event_type` | 5 a 10 | Sim, mas avaliar skew |
| `campaign_id` | 100 a 10.000 | Depende do volume por campanha |
| `user_id` | Milhões | Não — alta cardinalidade |
| `country` | 10 a 50 | Sim, se volume equilibrado |

---

## 6. Skew de partição

**O que é skew**

Skew (distorção) é o desequilíbrio de tamanho entre partições. Em uma tabela particionada por `event_type`, se 90% dos eventos são do tipo `view` e os outros tipos somam 10%, a partição `event_type=view` será 9 vezes maior que todas as outras juntas.

**Por que skew é um problema**

Em engines distribuídos como o Trino ou o Spark, o trabalho é dividido entre workers. Se uma partição é muito maior que as demais, o worker responsável por ela termina muito depois dos outros. O tempo total da query é limitado pelo worker mais lento. Esse fenômeno é chamado de *stragglers* ou *tail latency*.

Além do impacto em queries, o skew complica o gerenciamento operacional:

- Backups e reprocessamentos da partição grande são desproporcionalmente caros.
- Estimar o tamanho de novos dados fica difícil (a distribuição é imprevisível).
- Monitorar o crescimento da tabela torna-se mais complexo.

**Como detectar skew**

No Trino, você pode inspecionar as estatísticas de partições:

```sql
-- Lista todas as partições e seus tamanhos estimados
SELECT partition_key, row_count, data_size
FROM hive.marketing."$partitions";
```

Se os valores de `data_size` variarem em ordens de magnitude, há skew.

Uma forma prática de detectar durante o desenvolvimento: olhar o tamanho dos arquivos no MinIO Console (`http://localhost:9001`) e comparar visualmente as partições.

**Estratégias para lidar com skew**

- **Mudar a chave de partição:** se a coluna de partição tem skew natural, avaliar uma chave mais equilibrada.
- **Sub-particionar:** adicionar uma segunda dimensão que equilibre a distribuição (ex: `event_type` + `event_date`).
- **Bucketing:** dentro de uma partição, distribuir os dados em N arquivos (buckets) de tamanho similar. O Hive e o Spark suportam bucketing. O Trino suporta leitura de tabelas com bucket, mas a criação é via Hive.
- **Aceitar o skew:** em alguns casos, o skew é inevitável e o correto é aceitá-lo e otimizar as queries para a partição grande especificamente (ex: via pushdown de row group ou Z-ordering no Iceberg).

---

## 7. Hot partitions

**O que são hot partitions**

Hot partition é o fenômeno em que uma partição específica recebe um volume desproporcional de escritas simultâneas. Acontece com frequência em tabelas particionadas por tempo quando vários processos escrevem para o "dia de hoje" ao mesmo tempo.

**Por que é um problema diferente do skew**

Skew é um problema de leitura: a partição é grande e demora para ser lida. Hot partition é um problema de escrita: a partição recebe muitos writes concorrentes, o que pode:

- Causar conflitos de arquivo (especialmente em formatos sem controle de concorrência como Hive clássico).
- Gerar muitos arquivos pequenos porque cada processo escreve um arquivo separado.
- Sobrecarregar o metastore com atualizações de metadados da partição atual.

**O caso clássico: partição do dia atual**

Em um pipeline de eventos com processamento quase em tempo real, vários workers escrevem para `event_date=2026-03-03` ao longo do dia. Cada job de microbatch gera um arquivo. Ao fim do dia, a partição pode ter centenas ou milhares de arquivos pequenos.

**Estratégias de mitigação**

- **Compaction (compactação):** um job periódico (ex: rodando via Airflow a cada hora ou uma vez por dia) lê todos os arquivos pequenos de uma partição, une-os em arquivos maiores e sobrescreve. O Iceberg e o Delta Lake têm compaction nativo e transacional. No Hive clássico, o processo é manual.
- **Staging area:** em vez de escrever diretamente na partição final, os jobs escrevem em uma área de staging (`s3://bronze/events_staging/`). Um job de merge periódico move os dados para a partição oficial com compaction automática.
- **Controle de concorrência via orquestrador:** o Airflow pode serializar as escritas para a partição do dia atual, evitando múltiplos writers simultâneos.

---

## 8. Custo versus performance

**O trade-off fundamental**

Particionar resolve um problema, mas cria outro. A redução de custo e latência de queries vem com um custo de overhead de gerenciamento: mais partições = mais metadados = mais overhead do metastore = maior latência para operações que valem o schema inteiro.

**O problema dos small files**

Cada arquivo no S3 tem um custo fixo de operação: um GET request para abrir, um PUT para escrever. Em um Parquet típico, o overhead de abertura é de dezenas de milissegundos. Se uma partição tem 1000 arquivos de 1 KB cada, o engine faz 1000 GETs para ler 1 MB de dados. Comparado a 1 GET para um arquivo de 1 MB, o overhead é enorme.

A regra prática: arquivos entre **128 MB e 1 GB** são o ideal para queries analíticas em S3. Abaixo de 10 MB, o overhead começa a ser perceptível. Abaixo de 1 MB, é um problema.

**Granularidade de partição versus tamanho de arquivo**

Há uma tensão direta entre granularidade de partição e tamanho de arquivo:

- Particionar por hora gera 24 partições por dia. Se o volume de dados for baixo, cada partição pode ter poucos MB, gerando small files.
- Particionar por mês resolve o small files problem, mas reduz drasticamente o benefício do pruning para queries diárias.

A decisão correta depende do volume de dados. A regra de ouro: **cada partição deve ter pelo menos alguns arquivos de 128 MB ou mais**. Se você sabe o volume diário de dados, você consegue calcular qual granularidade é adequada.

**Overhead de metadados no Hive Metastore**

O Hive Metastore guarda uma entrada no banco (PostgreSQL, neste lab) para cada partição. Com milhares de partições, operações como `SHOW PARTITIONS`, `DESCRIBE`, e o próprio processo de resolução de schema ficam mais lentos.

Formatos como Iceberg resolvem parte desse problema ao usar um catálogo próprio baseado em arquivos de manifesto, reduzindo a dependência do Hive Metastore para listagem de partições.

**Referência do livro (Cap. 8 e 10)**

O Cap. 8 cobre o padrão *Partitioned Table* com discussão explícita do trade-off entre granularidade e overhead. O Cap. 10 (Data Observability) menciona a importância de monitorar o tamanho de partições e o número de arquivos como métricas operacionais fundamentais de um datalake.

---

## 9. A stack do laboratório: MinIO, Hive Metastore, Trino e o papel do Airflow

Esta seção explica o papel de cada componente antes do laboratório prático.

**MinIO — Object Storage S3-compatible**

O MinIO é um servidor de object storage de código aberto que implementa a API do Amazon S3. Ele funciona idêntico ao S3 para qualquer cliente que usa o SDK ou API do S3: você cria buckets, faz PUT de objetos, faz GET, lista prefixos.

A diferença em relação ao S3 real: o MinIO roda localmente, sem custo e sem precisar de conta na AWS. Para fins de laboratório e desenvolvimento, é indistinguível do S3.

Nesta sessão, o MinIO tem três buckets:

- `bronze`: dados brutos, particionados por data.
- `silver`: dados curados e transformados.
- `gold`: dados agregados para consumo analítico.

**Hive Metastore — Catálogo de tabelas**

O Hive Metastore é um serviço independente que armazena metadados de tabelas: nome, schema (colunas e tipos), localização no S3, colunas de partição, lista de partições existentes e estatísticas.

Ele usa um banco relacional como backend. Neste lab, o backend é um PostgreSQL. Em produção na AWS, o serviço equivalente é o AWS Glue Data Catalog, que é totalmente compatível com o protocolo Thrift do Hive Metastore.

A comunicação entre o Trino e o Hive Metastore é via protocolo Thrift na porta 9083. O Trino consulta o metastore sempre que precisa resolver metadados de uma tabela.

**Trino — Engine de consulta SQL**

O Trino (anteriormente PrestoSQL) é um engine de consulta SQL distribuído, desenhado para consultas analíticas de alta performance sobre dados em object storage. Ele não armazena dados: apenas os lê e os processa.

O Trino se conecta ao Hive Metastore via conector Hive (configurado em `catalog/hive.properties`) e ao MinIO via protocolo S3 (com endpoint override apontando para `http://minio:9000`).

Para o usuário final, o Trino aparece como um banco SQL padrão. Você conecta via CLI, UI web ou JDBC, e escreve queries SQL normais.

**Como os três se conectam**

```
[Usuário / Query] --> [Trino :8090]
                           |
                           |-- (1) Consulta metadados --> [Hive Metastore :9083]
                           |                                     |
                           |                               [PostgreSQL :5432]
                           |
                           |-- (2) Lê arquivos ----------> [MinIO :9000]
                                                              |
                                                         [bronze/silver/gold]
```

O fluxo de uma query:

1. O usuário envia a query para o Trino.
2. O Trino consulta o Hive Metastore para obter metadados da tabela (schema, localização, partições).
3. Com base nos predicados da query, o Trino determina quais partições ler (partition pruning).
4. O Trino lê os arquivos Parquet das partições selecionadas diretamente do MinIO via API S3.
5. O Trino processa e retorna o resultado.

**Onde o Airflow entra**

O Airflow orquestra a sequência das etapas, mas nesta sessão ele não precisa subir. O desenho do DAG é suficiente para conectar as caixinhas:

- `generate_cdc` → gera eventos (ou captura CDC real)
- `load_bronze` → envia arquivos para o MinIO (bronze)
- `build_silver` → cria ou atualiza tabela particionada
- `validate_queries` → roda queries de validação e EXPLAIN

---

## 10. Laboratório integrado: CDC → MinIO → Trino → particionamento

Esta seção conecta CDC, storage e consulta. Vamos usar os dados sintéticos já gerados em `data/generated/marketing`.

**Conectar ao Trino via CLI**

```bash
docker exec -it mentoria-s04-trino trino
```

Você verá o prompt `trino>`. A partir daqui, todos os comandos são SQL.

**Verificar o catálogo disponível**

```sql
SHOW CATALOGS;
```

Deve retornar pelo menos: `hive` (configurado em `hive.properties`).

---

### Lab 0: Carregar dados no MinIO (bronze)

Usaremos o MinIO Client via Docker (sem instalar nada no host):

```bash
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/data/generated/marketing:/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events.csv local/bronze/marketing/raw/events/

docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/data/generated/marketing:/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events__cdc.csv local/bronze/marketing/raw/events_cdc/
```

Isso cria dois prefixos no bucket `bronze`: `raw/events/` e `raw/events_cdc/`.

---

### Lab 1: Criar schema e tabela bronze (raw)

**Criar schema no bucket bronze**

```sql
CREATE SCHEMA IF NOT EXISTS hive.marketing
WITH (location = 's3://bronze/marketing/');
```

**Criar tabela raw (CSV) — somente VARCHAR**

```sql
CREATE TABLE IF NOT EXISTS hive.marketing.events_raw (
    event_id    VARCHAR,
    event_date  VARCHAR,
    event_ts    VARCHAR,
    user_id     VARCHAR,
    campaign_id VARCHAR,
    channel     VARCHAR,
    device      VARCHAR,
    country     VARCHAR,
    stage       VARCHAR,
    revenue     VARCHAR
)
WITH (
    format = 'CSV',
    external_location = 's3://bronze/marketing/raw/events/',
    skip_header_line_count = 1
);
```

**Nota importante**: o formato CSV no Hive/Trino aceita apenas VARCHAR. Tipos são aplicados na tabela silver via CAST.

**(Opcional) Criar tabela CDC raw**

```sql
CREATE TABLE IF NOT EXISTS hive.marketing.events_cdc_raw (
    event_id         VARCHAR,
    event_date       DATE,
    event_ts         DATE,
    user_id          VARCHAR,
    campaign_id      VARCHAR,
    channel          VARCHAR,
    device           VARCHAR,
    country          VARCHAR,
    stage            VARCHAR,
    revenue          DOUBLE,
    cdc_op           VARCHAR,
    cdc_event_ts     TIMESTAMP(3),
    cdc_source_table VARCHAR
)
WITH (
    format = 'CSV',
    external_location = 's3://bronze/marketing/raw/events_cdc/',
    skip_header_line_count = 1
);
```

---

### Lab 2: Criar tabela silver particionada

```sql
CREATE TABLE IF NOT EXISTS hive.marketing.events_silver
WITH (
    format = 'PARQUET',
    partitioned_by = ARRAY['event_date'],
    external_location = 's3://silver/marketing/events/'
) AS
SELECT
    event_id,
    user_id,
    campaign_id,
    channel,
    device,
    country,
    stage,
    TRY_CAST(revenue AS DOUBLE) AS revenue,
    CAST(event_date AS DATE) AS event_date
FROM hive.marketing.events_raw;
```

**Nota:** no Trino, a coluna de partição precisa estar na lista de colunas e, no CTAS, deve aparecer no SELECT.

---

### Lab 3: Listar partições

```sql
SELECT * FROM hive.marketing."events_silver$partitions";
```

---

### Lab 4: Query com partition pruning

```sql
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10';
```

**Verificar o plano de execução:**

```sql
EXPLAIN
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10';
```

No plano retornado, procure por `Constraint` na linha do `TableScan`. Deve mostrar `event_date IN (2025-01-10)`.

---

### Lab 5: Query sem partition pruning (full scan)

```sql
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE channel = 'organic';
```

**Verificar o plano:**

```sql
EXPLAIN
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE channel = 'organic';
```

No plano, a linha do `TableScan` não terá `Constraint` de partição.

---

### Lab 6 (opcional): CDC aplicado (última versão por event_id)

```sql
CREATE TABLE IF NOT EXISTS hive.marketing.events_latest
WITH (
    format = 'PARQUET',
    partitioned_by = ARRAY['event_date'],
    external_location = 's3://silver/marketing/events_latest/'
) AS
SELECT
    event_id,
    user_id,
    campaign_id,
    channel,
    device,
    country,
    stage,
    revenue,
    event_date
FROM (
    SELECT
        *,
        row_number() OVER (PARTITION BY event_id ORDER BY cdc_event_ts DESC) AS rn
    FROM hive.marketing.events_cdc_raw
    WHERE cdc_op <> 'delete'
) t
WHERE rn = 1;
```

---

### Lab 7 (opcional): Alta cardinalidade e particionamento híbrido

Use os labs de alta cardinalidade e particionamento híbrido como extensão (ver checklist e exemplos da sessão 02+03).

---

## 11. Análise do domínio de marketing

Com a tabela de eventos criada no lab, podemos fazer as perguntas típicas de um analista de marketing e observar o impacto do particionamento.

**Agregação diária de cliques por campanha (query frequente)**

```sql
SELECT
    event_date,
    campaign_id,
    COUNT(*) AS total_clicks
FROM hive.marketing.events_silver
WHERE event_date >= DATE '2025-01-10'
  AND event_date <= DATE '2025-01-12'
  AND stage = 'click'
GROUP BY event_date, campaign_id
ORDER BY event_date, campaign_id;
```

Esta query usa o filtro de `event_date` (coluna de partição) e um filtro adicional de `stage` (filtro de coluna). O Trino faz pruning de partições fora do intervalo e depois aplica o filtro de `stage` dentro das partições lidas.

**Total de eventos por tipo na semana**

```sql
SELECT
    stage,
    COUNT(*) AS total
FROM hive.marketing.events_silver
WHERE event_date BETWEEN DATE '2025-01-10' AND DATE '2025-01-12'
GROUP BY stage
ORDER BY total DESC;
```

**Usuários únicos por campanha (métrica de alcance)**

```sql
SELECT
    campaign_id,
    COUNT(DISTINCT user_id) AS unique_users
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10'
GROUP BY campaign_id;
```

**Ponto de aprendizado**: todas essas queries de marketing são naturalmente filtradas por data. Isso é o padrão dominante no domínio de analytics: "me dá os dados do dia X, da semana Y, do mês Z". Por isso, particionar por data é a decisão padrão e correta para tabelas de eventos.

**Quando particionar por campanha em vez de data?**

Se as queries mais comuns fossem "me dá todos os eventos da campanha A desde o início dos tempos", particionar por `campaign_id` faria mais sentido. Mas esse padrão é menos comum porque:

- O número de campanhas pode ser alto e variável (risco de skew e muitas partições).
- Campanhas têm ciclos de vida curtos — a maioria das análises ainda usa janelas de tempo.

A decisão final deve vir dos padrões de acesso reais, não de suposições.

---

## 12. Exercícios e entregáveis

### Exercício 1: Mapa do pipeline + contrato mínimo

**Objetivo:** conectar as caixinhas do Projeto 1.

**Entregável esperado:** diagrama com:
- origem, CDC, bronze, silver, gold e consumo;
- onde entra o Airflow (orquestração);
- contratos básicos (granularidade e chaves).

---

### Exercício 2: Modelagem mínima

**Objetivo:** definir o grão e as chaves de cada entidade.

**Entregável esperado:** tabela com entidade, grão, chave principal e tipo de mudança (append/upsert).

---

### Exercício 3: Plano de particionamento

**Contexto:** você está projetando a camada bronze e silver para o Projeto 1 (plataforma de marketing analytics).

**Tabelas a planejar:**

| Tabela | Volume estimado | Padrões de query mais comuns |
|---|---|---|
| `events` | 10 M registros/dia | Por data, por campanha, por stage |
| `campaigns` | 500 registros/mês | Por data de criação, por status |
| `costs` | 1000 registros/dia | Por data, por campanha |
| `crm` | 200 K registros total, com atualizações diárias | Por segmento, por data de última atualização |

**Entregável esperado:** proposta de particionamento para cada tabela com:
- Chave de partição escolhida.
- Justificativa (padrões de acesso, cardinalidade esperada).
- Granularidade (diária, mensal, etc.).
- Riscos identificados (skew, small files, hot partitions).

---

### Exercício 4: Análise de custo

**Contexto:** a tabela `events` tem 2 anos de histórico (730 dias) e 10 M registros por dia, totalizando 7,3 bilhões de registros. Cada registro ocupa 200 bytes em Parquet, totalizando 1,46 TB.

**Cenário A — Sem partição:**
- Uma query que filtra os últimos 7 dias varre todos 1,46 TB.
- Custo estimado no Athena: 1,46 TB x $5/TB = $7,30 por query.

**Cenário B — Particionado por dia:**
- A mesma query lê apenas 7 partições de 730.
- Volume lido: 7/730 x 1,46 TB = ~14 GB.
- Custo estimado no Athena: 14 GB x $5/TB = $0,07 por query.

**Entregável esperado:** tabela comparativa de custo para as tabelas do Exercício 3, usando os volumes estimados e o modelo de precificação do Athena ($5/TB). Calcule o custo mensal assumindo 100 queries/dia para cada tabela nos dois cenários (sem partição vs com partição).

---

### Exercício 5: Mini ADR de estratégia de partição

**ADR** (Architecture Decision Record) é um documento curto que registra uma decisão técnica com contexto, alternativas consideradas e justificativa.

**Entregável esperado:** ADR com:
- **Título:** Estratégia de particionamento para tabela de eventos.
- **Status:** Proposta.
- **Contexto:** o que motivou a decisão.
- **Decisão:** qual estratégia foi escolhida.
- **Alternativas consideradas:** pelo menos 2 outras estratégias com seus trade-offs.
- **Consequências:** o que muda no pipeline com essa decisão.

---

## Checklist de validação da sessão

- [ ] Mapa do pipeline end-to-end desenhado.
- [ ] Modelagem mínima definida (grão e chaves).
- [ ] Tabela silver particionada criada com dados do MinIO.
- [ ] Partition pruning demonstrado via EXPLAIN.
- [ ] Plano de particionamento iniciado para o Projeto 1.
- [ ] Trade-offs de custo calculados para pelo menos uma tabela.

---

## Referências

- **Cap. 8 — Data Storage Design Patterns**: padrão Partitioned Table, trade-offs de granularidade.
- **Cap. 10 — Data Observability Design Patterns**: métricas operacionais de partições (tamanho, número de arquivos).
- Documentação do Trino: https://trino.io/docs/current/connector/hive.html
- Documentação do MinIO: https://min.io/docs/
- **Arquivos desta sessão:**
  - `data/generated/marketing/events.csv`
  - `data/generated/marketing/events__cdc.csv`
  - `docs/sessions/sessao-02-03-airflow-cdc-tabelas/checklist-execucao-ao-vivo.md`
  - `docs/notes/relatorio-cdc-por-id.md`
  - `infrastructure/sessao-04-particionamento/`
