# Apostila — Sessão 02+03: Airflow, CDC e Formatos de Dados

> Sessão conjunta de orquestração, Change Data Capture e decisões de armazenamento.
> Conduzida por Iuri Zambotto com Paulo Shindi. Mentorado: Aurelius Oliveira.

---

## Sumário

1. Por que orquestrar pipelines de dados
2. Arquitetura do Apache Airflow
3. DAGs, tasks e dependências na prática
4. Idempotência e retries
5. Change Data Capture (CDC) — conceito e lifecycle
6. CDC por ciclo de vida de ID — regras e pitfalls
7. Formatos de arquivo: CSV, JSONL, Parquet e ORC
8. Tipos de tabela: Hive, Iceberg e Delta Lake
9. Camadas bronze, silver e gold
10. Exercícios e entregáveis

---

## 1. Por que orquestrar pipelines de dados

Antes do Airflow entrar em cena, vale a pena entender o problema que ele resolve.

**O que é orquestração de dados e por que ela existe**

Um pipeline de dados raramente é uma tarefa única. Em geral, ele envolve sequências como: aguardar dados chegarem → extrair → transformar → carregar → notificar. Se você executar essas etapas manualmente ou via `cron` simples, problemas clássicos vão aparecer:

- **Ordem errada de execução.** Um job de transformação pode rodar antes dos dados de origem estarem completos, gerando resultados inválidos ou zerados.
- **Duplicidade de dados.** Se o job travar e você rodar manualmente, os registros podem ser inseridos duas vezes, sem que você perceba de imediato.
- **Perda de rastreio.** Com scripts avulsos no cron, é difícil saber o que rodou quando, o que falhou, e por quê. O histórico vira uma caixa-preta.
- **Falta de dependências explícitas.** O cron não sabe que o job B só pode rodar depois que o job A terminar. Você precisa codificar isso na mão, o que não escala.

**A diferença entre agendar e orquestrar**

Agendar é dizer "rode às 03h". Orquestrar é dizer "rode às 03h, mas só se o dado de ontem estiver disponível, e depois que esse job terminar, dispare os dois jobs seguintes em paralelo, e se qualquer um falhar, tente mais três vezes com espera exponencial".

Orquestração resolve um problema de coordenação. Ela dá visibilidade, controle e auditoria ao fluxo de dados.

**Quando faz sentido usar um orquestrador**

Não todo pipeline precisa de Airflow. Um script simples que roda uma vez por dia e não tem dependências pode viver no cron sem problema. O orquestrador vale a pena quando:

- Há dependências entre tarefas ou entre pipelines distintos.
- O pipeline precisa ser reexecutado (backfill) de forma segura.
- É necessário monitorar SLA e receber alertas.
- A equipe precisa inspecionar histórico de execuções.
- Há múltiplos autores de pipelines que precisam de um padrão comum.

**Referência do livro (Cap. 6 — Data Flow Design Patterns)**

O padrão *Local Sequencer* descreve exatamente esse problema: quando um job monolítico cresce a ponto de ser ininteligível, a solução é decompô-lo em tarefas sequenciais com dependências explícitas. A separação de tarefas melhora a leitura do pipeline, facilita retries pontuais e define fronteiras de reprocessamento claras.

---

## 2. Arquitetura do Apache Airflow

Airflow é um orquestrador de workflows declarado em Python. Para entender como trabalhar bem com ele, é fundamental conhecer seus componentes e o papel de cada um.

**Os componentes principais**

- **Webserver (ou API Server, a partir do Airflow 3.x).** É a interface visual e REST API. Você acessa a UI no `localhost:8080`, visualiza DAGs, loga nas tasks, força execuções manuais e monitora o estado dos pipelines. No Airflow 3.1.x (versão desta mentoria), o componente foi renomeado para `airflow-apiserver`.

- **Scheduler.** É o componente mais crítico. Ele varre os arquivos de DAG, determina quais tasks precisam ser enfileiradas com base nas dependências e no cronograma, e delega a execução para os workers. O scheduler não executa código de negócio diretamente. Ele apenas toma decisões de agendamento.

- **Worker.** Executa o código das tasks. No modelo com Celery Executor, múltiplos workers podem rodar em paralelo, cada um em contêiners separados. No LocalExecutor (típico de ambientes de desenvolvimento), as tasks rodam em processos locais do scheduler.

- **Triggerer.** Componente introduzido no Airflow 2.2 para suportar *deferrable operators*. Ele gerencia tarefas que ficam esperando um evento externo (como uma API responder ou um arquivo aparecer) sem bloquear um worker. É especialmente útil em pipelines com muitos sensors.

- **Metastore (banco de dados).** O estado de todas as execuções é persistido em um banco relacional, geralmente PostgreSQL em produção. Inclui o histórico de DAG runs, o estado de cada task (queued, running, success, failed, skipped), logs resumidos e configurações.

- **Redis (ou outro broker de mensagens).** Usado no modelo com Celery Executor para enfileirar as tasks entre o scheduler e os workers. O scheduler coloca a task na fila, o worker consome.

- **Init.** No Docker Compose local, o serviço `airflow-init` é um job de bootstrap que cria o banco, aplica migrações e cria o usuário admin. Roda uma vez antes dos demais serviços subirem.

**Fluxo de uma execução**

1. O scheduler lê os arquivos `.py` da pasta `dags/`.
2. Identifica que uma DAG deve rodar (por schedule ou trigger manual).
3. Cria um *DAG run* no metastore e enfileira as tasks elegíveis.
4. O worker pega a task da fila, executa o código Python correspondente e reporta o resultado ao metastore.
5. O scheduler usa o resultado para determinar se a próxima task na dependência pode ser enfileirada.
6. A UI exibe o estado em tempo quase real.

**Por que o scheduler não executar tasks é importante**

Se o scheduler executasse tasks, uma task lenta ou que consome muita memória poderia travar o agendamento de todas as outras DAGs. A separação de responsabilidades é deliberada e essencial para escalabilidade.

---

## 3. DAGs, tasks e dependências na prática

**O que é uma DAG**

DAG significa *Directed Acyclic Graph*. No Airflow, é o objeto principal que representa um pipeline. Ele define as tasks e a ordem em que devem rodar. "Acyclico" significa que não pode haver ciclos: task A → task B → task A nunca é permitido.

Exemplo mínimo de DAG em Python:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extraindo dados...")

def transform():
    print("Transformando...")

def load():
    print("Carregando...")

with DAG(
    dag_id="pipeline_marketing",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    t1 >> t2 >> t3
```

O operador `>>` define a dependência: `t1` deve terminar com sucesso antes de `t2` iniciar.

**Tipos de operadores mais comuns**

- `PythonOperator`: executa uma função Python.
- `BashOperator`: executa um comando shell.
- `PostgresOperator`: executa uma query SQL num banco PostgreSQL.
- `FileSensor` / `ExternalTaskSensor`: espera uma condição externa antes de avançar.
- `BranchPythonOperator`: avalia uma condição e decide qual branch seguir (padrão *Exclusive Choice* do Cap. 6).

**catchup e start_date**

O `start_date` define quando a DAG começa a existir no tempo. Se `catchup=True` (padrão), o Airflow vai tentar rodar todos os intervalos entre `start_date` e hoje que ainda não foram executados. Isso é backfill automático. Em ambientes de produção com dados reais, isso pode ser perigoso se o pipeline não for idempotente. Por isso, em desenvolvimento, use `catchup=False`.

**Retries e políticas de falha**

Cada task pode ter configuração individual de retries:

```python
t2 = PythonOperator(
    task_id="transform",
    python_callable=transform,
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
)
```

Isso diz: se a task `transform` falhar, tente mais 3 vezes, com espera de 5 minutos entre as tentativas (e com backoff exponencial, o tempo entre retries cresce a cada tentativa).

**Exemplo da DAG de marketing usada na sessão**

A DAG didática desta sessão tem a seguinte sequência:

```
extract_costs -> extract_events -> build_daily_metrics -> publish_report
```

Cada task simula uma etapa real de um pipeline de marketing:

- `extract_costs`: lê custos por campanha.
- `extract_events`: lê eventos de usuários.
- `build_daily_metrics`: agrega as métricas diárias.
- `publish_report`: disponibiliza o relatório para consumo.

**Referência do livro (Cap. 6 — Local Sequencer)**

Este pipeline segue exatamente o padrão *Local Sequencer*: tarefas encadeadas em sequência, onde cada uma depende da anterior. A vantagem prática é que, se `build_daily_metrics` falhar, o Airflow reexecuta apenas essa task, sem precisar refazer a extração que pode ser cara ou ter janelas de tempo.

---

## 4. Idempotência e retries

**O que é idempotência em dados**

Uma operação é idempotente quando pode ser executada múltiplas vezes e sempre produz o mesmo resultado. Em dados, isso significa que rodar o mesmo pipeline duas vezes não duplica registros, não gera inconsistências, e produz exatamente o mesmo dataset que uma única execução produziria.

Idempotência não é opcional em engenharia de dados: retries acontecem, falhas parciais acontecem, e backfills são necessários. Se o pipeline não for idempotente, cada retry pode ser uma bomba-relógio.

**Por que duplicatas são o pior cenário**

Quando um pipeline duplica dados, há dois caminhos possíveis:

1. Duplicatas identificáveis: você tem chave primária, pode deduplicar. Caro, mas possível.
2. Duplicatas não identificáveis: sem chave única, não há como saber qual registro é a repetição. Esse é o pesadelo que o livro descreve no início do Cap. 4.

**Padrões de idempotência (Cap. 4 do livro)**

O livro apresenta três famílias principais:

- **Fast Metadata Cleaner**: em vez de `DELETE FROM tabela WHERE ...` (caro em tabelas grandes), usa `TRUNCATE TABLE` ou `DROP + CREATE` por partição. Opera na camada de metadados, que é ordens de magnitude mais rápida que varrer dados.

- **Data Overwrite**: quando não há camada de metadados (ex: object store puro), usa `INSERT OVERWRITE` ou equivalente. No Spark, isso é `input_data.write.mode('overwrite')`.

- **Merger (UPSERT)**: para datasets incrementais onde não se tem o conjunto completo, usa a operação `MERGE INTO ... USING ...`. Aplica insert se o registro é novo, update se já existe. Deletes precisam ser expressados como soft deletes (flag `is_deleted`).

**Idempotência aplicada ao Airflow**

Na DAG de marketing, a task `publish_report` é o ponto mais sensível. Se ela rodar duas vezes, o relatório pode ser duplicado para os consumidores. A solução é garantir que o relatório seja identificado por data de execução (chave idempotente) e que a escrita seja overwrite por partição de data, e não append.

**Retries e idempotência andam juntos**

Configurar `retries=3` em uma task não idempotente é aumentar a probabilidade de problema, não de solução. Antes de habilitar retries, certifique-se de que a task pode ser reexecutada sem efeitos colaterais.

---

## 5. Change Data Capture (CDC) — conceito e lifecycle

**O que é CDC e por que existe**

Change Data Capture é o conjunto de técnicas para capturar e representar as mudanças que ocorrem em um banco de dados de origem. Em vez de ler a tabela inteira a cada ciclo (snapshot completo), o CDC captura apenas o que mudou: inserções, atualizações e deleções.

O CDC nasce de uma necessidade real: dados mudam. Um usuário atualiza o endereço, uma campanha é cancelada, um pedido é deletado. Se você só tiver o snapshot mais recente, perdeu a história do que aconteceu. Se você capturar cada evento de mudança, tem uma trilha auditável e pode reconstruir qualquer estado anterior.

**Abordagem técnica: como o CDC é capturado**

Há diferentes métodos de captura:

- **Log-based CDC**: lê o write-ahead log (WAL) do banco de dados. É o método mais confiável e menos intrusivo. Ferramentas como Debezium fazem isso para PostgreSQL, MySQL, MongoDB e outros. Cada operação DML (INSERT, UPDATE, DELETE) gera um evento no log.

- **Trigger-based CDC**: triggers no banco disparam escrita em uma tabela de auditoria a cada mudança. Funciona, mas tem custo de escrita no próprio banco de origem.

- **Timestamp-based CDC**: lê registros onde `updated_at > last_processed_time`. Simples de implementar, mas não captura deleções e depende de o campo de timestamp existir e ser confiável.

- **Geração sintética (usado nesta sessão)**: para fins didáticos, geramos os eventos de CDC programaticamente com regras de lifecycle controladas. O script `generic_cdc.py` + `generate_domain_data.py` produz os arquivos `*__cdc.csv`.

**Campos padrão de um evento CDC**

Todo evento CDC carrega:

- `cdc_op`: tipo da operação — `insert`, `update` ou `delete`.
- `cdc_event_ts`: timestamp do evento.
- `cdc_source_table`: tabela de origem.
- Os dados do registro no estado em que estava no momento do evento.

**A diferença entre append-only e upsert**

Uma tabela append-only só recebe novos registros; registros passados nunca mudam. Exemplos: logs de acesso, eventos de clique, transações financeiras.

Uma tabela com upsert recebe inserções e também atualizações de registros existentes. Exemplos: cadastro de clientes, status de pedidos, saldo de conta.

O CDC é especialmente relevante para tabelas com upsert. Se você precisar reconstruir o estado atual de um cadastro de clientes, precisa saber não apenas o insert inicial, mas todos os updates subsequentes e, eventualmente, o delete.

---

## 6. CDC por ciclo de vida de ID — regras e pitfalls

Esta é a regra mais importante da sessão e precisa ser internalizada.

**A regra do lifecycle por ID**

Para cada identificador único (chave primária) numa tabela CDC, a sequência de eventos obedece a uma regra estrita:

```
insert → update* → delete?
```

Traduzindo:

1. O ID aparece **uma única vez** com `cdc_op = insert`. Esse é o primeiro e único evento de criação.
2. Após o insert, podem existir **zero ou mais** eventos com `cdc_op = update`. Cada update representa uma alteração no estado do registro.
3. O `cdc_op = delete` é **terminal**: significa que o registro foi removido da origem. Após um delete, esse ID não pode mais aparecer em novos eventos de insert ou update.

**Por que o delete é terminal**

Quando um registro é deletado no banco de origem, ele deixa de existir. Qualquer tentativa de referenciar aquele ID depois disso é ou um erro na captura CDC ou uma reinserção (novo ciclo, novo contexto). Para fins de lifecycle, tratamos o delete como fim de vida daquele ID específico.

**Evidência real do dataset desta sessão**

O relatório `docs/notes/relatorio-cdc-por-id.md` mostra os resultados do dataset `marketing`:

| Tabela       | IDs únicos | Inserts | Updates | Deletes | Violações |
|--------------|------------|---------|---------|---------|-----------|
| `users`      | 80         | 80      | 0       | 37      | 0         |
| `campaigns`  | 4          | 4       | 0       | 0       | 0         |
| `events`     | 80         | 80      | 584     | 2       | 0         |
| `costs`      | 4          | 4       | 52      | 0       | 0         |
| `crm`        | 80         | 80      | 0       | 27      | 0         |

**Zero violações** em todas as tabelas. Cada ID começa com `insert`, updates aparecem apenas entre o insert e o possível delete, e nenhum ID reaparece após o delete.

Exemplos concretos de sequências válidas:

- `user_0001`: `insert -> delete` (vida curta, apenas criou e foi removido)
- `user_0001` na tabela `events`: `insert -> update -> update -> update -> ... -> update` (criou e atualizou 8 vezes, ainda ativo)
- `user_0009` na tabela `events`: `insert -> update -> update -> update -> delete` (criou, atualizou 3 vezes, foi removido)

**Os pitfalls mais comuns em CDC**

- **Insert duplicado.** Um evento de insert para um ID que já existe indica erro no pipeline CDC ou problema de deduplicação. O dado não pode ser confiado sem investigação.

- **Update antes do insert.** Se um ID aparece primeiro com `update`, o evento de criação foi perdido. Isso pode acontecer em migrações parciais ou quando a captura CDC começou depois que o registro já existia na origem.

- **Evento após delete.** Se um ID que foi deletado reaparece com `update`, houve um problema sério: ou o delete foi registrado por engano, ou houve reinserção sem novo insert CDC. Ambos indicam inconsistência.

- **Timestamp fora de ordem.** Eventos CDC devem ser processados em ordem temporal por ID. Se o `cdc_event_ts` estiver fora de sequência, o estado reconstruído será incorreto.

- **Soft delete vs hard delete.** Nem todos os bancos geram eventos de delete explícito no CDC. Alguns sistemas usam soft delete: um campo `is_active = false` ou `deleted_at` é atualizado, e o registro permanece na tabela. Nesses casos, o CDC captura um `update`, não um `delete`. É importante saber qual estratégia o banco de origem usa.

**Como validar o lifecycle no código**

A validação implementada no `generic_cdc.py` do projeto segue esta lógica:

1. Agrupar eventos por `ID`.
2. Ordenar por `cdc_event_ts`.
3. Verificar que o primeiro evento é sempre `insert`.
4. Verificar que após qualquer `delete`, não existem mais eventos para aquele ID.
5. Reportar qualquer violação.

---

## 7. Formatos de arquivo: CSV, JSONL, Parquet e ORC

A escolha do formato de arquivo impacta diretamente o custo de processamento, a legibilidade, a capacidade de evolução do schema e a integração com diferentes ferramentas.

**CSV — Comma-Separated Values**

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

O arquivo `exemplos/output/events.csv` desta sessão é o dataset de eventos gerado para a tabela `events` do domínio marketing, exportado em CSV com header.

**JSONL — JSON Lines**

JSONL (também chamado de NDJSON — Newline-Delimited JSON) é um formato onde cada linha é um objeto JSON válido e independente. Diferente do JSON convencional (que é um único objeto ou array), JSONL é streamável: você pode processar um registro por vez sem ler o arquivo inteiro.

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

O arquivo `exemplos/output/events.jsonl` contém os mesmos eventos, mas em formato JSONL.

**Parquet — formato colunar da Apache**

Parquet é um formato binário e colunar. "Colunar" significa que os dados de cada coluna ficam armazenados juntos no arquivo, em vez de linha por linha.

Isso tem uma consequência enorme em analytics: se você tem uma tabela com 100 colunas e sua query usa apenas 5, o Parquet permite ler apenas os blocos dessas 5 colunas. Em CSV, você leria tudo.

Características:
- Compressão eficiente (Snappy, Gzip, Zstd) — reduz custo de armazenamento e I/O.
- Leitura seletiva de colunas (column pruning).
- Suporte a tipos complexos.
- Schema embutido no arquivo (metadata).
- Não é legível por humanos sem ferramentas.
- Dificuldade de merge e update de registros individuais (arquivo imutável por natureza).

Quando usar:
- Camada silver e gold de um data lake.
- Qualquer carga analítica com queries que selecionam subconjunto de colunas.
- Quando custo de armazenamento e tempo de query são prioridades.

O arquivo `exemplos/output/events.parquet` é o mesmo dataset em Parquet. Para inspecioná-lo manualmente, use `pandas.read_parquet()` ou `spark.read.parquet()`.

**ORC — Optimized Row Columnar**

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
- Quando as características de bloom filter do ORC forem relevantes para o padrão de query.
- Ambientes Databricks ou EMR onde ambos são suportados — a escolha depende do ecossistema da empresa.

O arquivo `exemplos/output/events.orc` permite comparação direta com o Parquet do mesmo dataset.

**Tabela comparativa**

| Característica       | CSV      | JSONL    | Parquet  | ORC      |
|----------------------|----------|----------|----------|----------|
| Legível por humanos  | sim      | sim      | não      | não      |
| Schema embutido      | não      | parcial  | sim      | sim      |
| Tipos complexos      | não      | sim      | sim      | sim      |
| Compressão nativa    | não      | não      | sim      | sim      |
| Leitura colunar      | não      | não      | sim      | sim      |
| Custo de scan        | alto     | alto     | baixo    | baixo    |
| Facilidade de merge  | alta     | alta     | baixa    | baixa    |
| Ecossistema          | universal| amplo    | amplo    | Hadoop+  |

**Referência do livro (Cap. 8 — Data Storage Design Patterns)**

O padrão *Horizontal Partitioner* descrito no Cap. 8 complementa diretamente a escolha de formato. Particionar por data no Parquet, por exemplo, é o que permite ao motor de query ignorar partições inteiras e ler apenas o intervalo de tempo relevante. Sem particionamento, até o melhor formato colunar vai ser forçado a escanear blocos desnecessários.

---

## 8. Tipos de tabela: Hive, Iceberg e Delta Lake

Formatos de arquivo (Parquet, ORC) são diferentes de *table formats*. O table format é a camada que define como metadados, schema, transações e histórico são gerenciados por cima dos arquivos físicos.

**Hive Table — o modelo original do data lake**

O modelo Hive é o mais antigo e o mais simples. Uma tabela Hive é basicamente um diretório no HDFS ou S3 com arquivos de dados, e um catálogo (Hive Metastore) que mapeia o nome da tabela para o path físico, o schema e as partições.

Como funciona:
- Os arquivos físicos ficam em `s3://bucket/tabela/particao=data/arquivo.parquet`.
- O Hive Metastore guarda o schema e o mapeamento.
- Engines como Hive, Spark, Presto e Athena consultam o metastore para saber onde estão os dados.

Limitações:
- Sem transações ACID robustas nativamente. Dois jobs escrevendo na mesma partição ao mesmo tempo podem corromper dados.
- Evolução de schema limitada: adicionar colunas é simples, mas renomear ou mudar tipos pode quebrar leitores existentes.
- Sem time travel nativo: você não consegue consultar "como estava a tabela há 3 dias" sem ter feito um backup manual.
- Operações de update e delete são limitadas ou ausentes (depende da engine e da versão).

Quando ainda faz sentido:
- Pipelines simples de append-only onde não há necessidade de update ou delete.
- Ambientes legados onde a migração para Iceberg ou Delta não vale o custo imediato.
- Quando a engine disponível (ex: Athena v1, EMR antigo) não suporta os novos formatos.

**Apache Iceberg — o table format moderno e multi-engine**

Iceberg foi criado pelo Netflix e Apache para resolver as limitações do Hive. É um table format aberto, desenhado para funcionar com múltiplas engines (Spark, Flink, Trino, Athena v3, Hive).

Como funciona:
- Cada escrita gera um novo *snapshot*. Um snapshot é um arquivo de metadados que aponta para os arquivos de dados que compõem o estado atual da tabela.
- O histórico de snapshots permite *time travel*: você pode consultar o estado da tabela em qualquer ponto do passado dentro do período de retenção.
- *Schema evolution* é um cidadão de primeira classe: adicionar, renomear e deletar colunas é suportado sem quebrar leitores que usam o schema antigo.
- *Partition evolution*: você pode mudar o esquema de particionamento sem precisar reescrever os dados existentes. Iceberg lida com múltiplos esquemas de partição no mesmo histórico da tabela.
- Suporte a operações ACID: escritas concorrentes são seguras.

Casos de uso ideais:
- Data lakes multi-engine onde diferentes times usam Spark, Trino ou Athena para consultar os mesmos dados.
- Tabelas que evoluem com frequência de schema.
- Pipelines que precisam de time travel para auditoria ou correção de dados históricos.
- Ambientes cloud onde o vendor-lock é uma preocupação (Iceberg é totalmente open source).

**Delta Lake — o table format do ecossistema Databricks**

Delta Lake foi criado pela Databricks e é o table format nativo do ambiente Databricks. Funciona bem com Spark e Databricks, e tem suporte crescente em outras engines (Trino, via Delta Kernel).

Como funciona:
- Usa um *transaction log* (`_delta_log/`) no diretório da tabela. Cada operação (write, delete, merge, optimize) gera um novo arquivo de log.
- As operações são ACID: um MERGE que processa milhões de linhas é atômico — ou tudo vai, ou nada vai.
- *Time travel*: como o log é preservado por configuração, você pode fazer `SELECT * FROM tabela VERSION AS OF 5` ou `TIMESTAMP AS OF '2026-01-01'`.
- `MERGE INTO` é especialmente performático em Delta Lake. É o padrão recomendado para pipelines de upsert.
- `OPTIMIZE` e `ZORDER BY` são operações de compactação e co-localização de dados que melhoram performance de queries.

Casos de uso ideais:
- Ambientes Databricks, onde Delta é nativo e tem suporte completo.
- Pipelines com mutações frequentes (merge, update, delete) onde performance transacional é crítica.
- Quando a integração com o ecossistema Spark/Databricks é prioritária.

**Tabela comparativa**

| Característica              | Hive        | Iceberg          | Delta Lake       |
|-----------------------------|-------------|------------------|------------------|
| Transações ACID             | limitado    | sim              | sim              |
| Schema evolution            | básico      | completo         | completo         |
| Partition evolution         | não         | sim              | não              |
| Time travel                 | não         | sim              | sim              |
| Multi-engine                | sim         | sim (melhor)     | crescente        |
| Merge / upsert              | limitado    | sim              | sim (otimizado)  |
| Vendor                      | Apache      | Apache (open)    | Databricks/Linux |
| Melhor cenário              | legado/simples | cloud multi-engine | Databricks      |

**Referência do livro (Cap. 4 — Merger Pattern)**

O padrão *Merger* do livro descreve exatamente o problema que Iceberg e Delta resolvem: como aplicar incrementos (inserts + updates + soft deletes) de forma idempotente a um dataset existente. A operação `MERGE INTO` do Delta/Iceberg é a implementação nativa desse padrão.

**Referência do livro (Cap. 4 — Stateful Merger)**

Para pipelines que precisam fazer backfill com consistência, o *Stateful Merger* depende de um banco com versionamento. Isso é exactamente o que Delta Lake (via transaction log) e Iceberg (via snapshots) fornecem: a capacidade de restaurar a tabela a uma versão anterior antes de reaplicar os dados corrigidos.

---

## 9. Camadas bronze, silver e gold

A arquitetura medallion (bronze/silver/gold) é um padrão de organização do data lake em camadas com diferentes níveis de curadoria.

**Bronze — dados brutos, fidelidade máxima**

A camada bronze recebe os dados como chegam da origem, com o mínimo de transformação possível. O objetivo é preservar a fidelidade dos dados originais.

Características:
- Formato preferido: JSONL ou CSV (mantém a estrutura original, legível).
- Particionamento por data de ingestão, não de evento.
- Dados podem ter inconsistências, nulos, duplicatas — tudo é preservado.
- Sem remoção de campos, mesmo que sensíveis (com controle de acesso adequado).
- Table format: Hive simples (append-only) ou Iceberg para capturar histórico.

Analogia: é o "fita bruta" da gravação. Você não edita a fita bruta. Tudo que aconteceu está lá.

**Silver — dados curados, prontos para análise**

A camada silver aplica transformações de qualidade: limpeza de nulos, deduplicação, padronização de tipos, enriquecimento com dados de referência.

Características:
- Formato preferido: Parquet (leitura eficiente, schema embutido).
- Particionamento por data de evento (não de ingestão).
- Dados devem atender contratos de schema definidos.
- Pode incluir campos derivados simples.
- Table format: Parquet + Iceberg ou Delta, dependendo da necessidade de upsert.

Analogia: é a "edição do corte" — você removeu os erros, normalizou o áudio, mas ainda não produziu o produto final.

**Gold — dados agregados, prontos para consumo**

A camada gold contém datasets prontos para consumo por analistas, dashboards e modelos. São as métricas, agregados e visões de negócio.

Características:
- Formato preferido: Parquet ou Delta/Iceberg (depende da necessidade de merge e auditoria).
- Estrutura orientada ao caso de uso (ex: tabela desnormalizada por produto, por região, por canal).
- Alta qualidade garantida (validações AWAP passadas).
- Pode ter SLA de atualização definido.

Analogia: é o produto final — o relatório, o dashboard, o número que o C-level vai olhar.

**Recomendação didática para o Projeto 1**

| Camada | Formato     | Table Format            | Justificativa                                        |
|--------|-------------|-------------------------|------------------------------------------------------|
| Bronze | JSONL / CSV | Hive ou Iceberg         | Fidelidade máxima, ingestão direta                   |
| Silver | Parquet     | Iceberg ou Delta        | Analytics eficiente, schema estável, suporte a merge |
| Gold   | Parquet     | Iceberg ou Delta        | Performance de query, auditabilidade, SLA            |

**Referência do livro (Cap. 9 — AWAP Pattern)**

O padrão *Audit-Write-Audit-Publish* descrito no Cap. 9 encaixa perfeitamente na transição silver → gold: antes de promover dados para a camada gold, você valida o dataset transformado (segunda auditoria). Se passar, promove. Se não passar, você tem opções: falha o pipeline, envia para dead-letter, ou promove com anotação de incompletude.

**Referência do livro (Cap. 10 — Flow Interruption Detector)**

A camada bronze é especialmente vulnerável a interrupções de fluxo. O padrão *Flow Interruption Detector* do Cap. 10 descreve como detectar quando um job parou de escrever dados sem falhar explicitamente. Implementar um detector de freshness na camada bronze previne que o silêncio de um job com bug passe despercebido por horas ou dias.

---

## 10. Exercícios e entregáveis

### Exercício 1 — Matriz de decisão de orquestrador

**Objetivo:** entender quando usar orquestrador vs. cron vs. sem automação.

Construa uma tabela com pelo menos 5 cenários (reais ou hipotéticos) e, para cada um, justifique a escolha de ferramenta:

| Cenário | Dependências? | Retries? | Backfill? | Ferramenta recomendada | Justificativa |
|---------|--------------|---------|----------|------------------------|---------------|
| ...     | ...          | ...     | ...      | ...                    | ...           |

**Entregável:** tabela preenchida + 2 parágrafos de justificativa técnica.

---

### Exercício 2 — Blueprint de camadas bronze/silver/gold

**Objetivo:** definir o padrão de armazenamento do Projeto 1.

Para cada camada, defina:
- Formato de arquivo
- Table format
- Estratégia de particionamento
- Política de retenção
- Critério de promoção para a próxima camada

**Entregável:** tabela de decisão por camada.

---

### Exercício 3 — Mini ADR de table format

**Objetivo:** documentar formalmente a decisão de table format.

Um ADR (Architecture Decision Record) é um documento curto que registra uma decisão técnica e suas justificativas. Escreva um mini ADR com:

- **Contexto:** qual é o problema que motivou a decisão.
- **Decisão:** qual table format foi escolhido.
- **Alternativas consideradas:** Hive, Iceberg e Delta, com prós e contras de cada um para o contexto.
- **Consequências:** o que fica mais fácil e o que fica mais difícil com a escolha feita.

**Entregável:** documento de 1 a 2 páginas com as quatro seções preenchidas.

---

### Exercício 4 — Validação de lifecycle CDC

**Objetivo:** verificar se você entende e consegue aplicar as regras de lifecycle CDC.

Dado um arquivo CSV com eventos CDC (use `data/generated/marketing/events__cdc.csv`):

1. Abra o arquivo com pandas.
2. Agrupe por `user_id`.
3. Ordene por `cdc_event_ts` dentro de cada grupo.
4. Implemente uma função que valida as regras de lifecycle:
   - Primeiro evento deve ser `insert`.
   - Após `delete`, não pode haver mais eventos.
5. Imprima o número de IDs com violação.

**Entregável:** script Python + resultado da validação (número de violações esperado: 0).

---

## Referências desta sessão

- **Livro:** Data Engineering Design Patterns (2025)
  - Cap. 4: Idempotency Design Patterns (Overwriting, Merger, Stateful Merger)
  - Cap. 6: Data Flow Design Patterns (Local Sequencer, Isolated Sequencer, Fan-In, Fan-Out)
  - Cap. 8: Data Storage Design Patterns (Horizontal Partitioner, Compactor)
  - Cap. 9: Data Quality Design Patterns (AWAP Pattern)
  - Cap. 10: Data Observability Design Patterns (Flow Interruption Detector)

- **Documentação do Airflow:** https://airflow.apache.org/docs/
- **Apache Iceberg:** https://iceberg.apache.org/
- **Delta Lake:** https://delta.io/

- **Arquivos desta sessão:**
  - `docs/sessions/sessao-02-03-airflow-cdc-tabelas/checklist-execucao-ao-vivo.md`
  - `docs/sessions/sessao-03-cdc-airflow-tabelas/exemplos/output/`
  - `docs/notes/relatorio-cdc-por-id.md`
  - `config/domains/marketing.yaml`
  - `src/zambotto_mentoria/generic_cdc.py`
  - `scripts/generate_domain_data.py`
  - `infrastructure/sessao-02-03-airflow-cdc-tabelas/docker-compose.yml`
