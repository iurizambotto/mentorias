---
title: "Apostila, Orquestracao com Apache Airflow"
date: 2026-07-30
type: apostila
status: draft
project: zambotto-mentoria
tags: [airflow, orquestracao]
---

# Apostila, Orquestracao com Apache Airflow

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

## Sumario

- [2.1 Por que orquestrar pipelines de dados](#21-por-que-orquestrar-pipelines-de-dados)
- [2.2 Arquitetura do Apache Airflow](#22-arquitetura-do-apache-airflow)
- [2.3 DAGs, tasks e dependências na prática](#23-dags-tasks-e-dependências-na-prática)
- [2.4 Idempotência e retries](#24-idempotência-e-retries)
- [2.5 Exercícios e entregáveis](#25-exercícios-e-entregáveis)

## Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.


> Pré-requisito: Capítulo 1, o Airflow é a ferramenta que garante a execução confiável e ordenada do pipeline descrito no ciclo de vida dos dados da Sessão 01.

## 2.1 Por que orquestrar pipelines de dados

**O que é orquestração de dados e por que ela existe**

Um pipeline de dados raramente é uma tarefa única. Em geral, ele envolve sequências como: aguardar dados chegarem → extrair → transformar → carregar → notificar. Executar essas etapas manualmente ou via `cron` simples gera problemas clássicos:

- **Ordem errada de execução.** Um job de transformação pode rodar antes dos dados de origem estarem completos, gerando resultados inválidos ou zerados.
- **Duplicidade de dados.** Se o job travar e você rodar manualmente, os registros podem ser inseridos duas vezes sem que você perceba de imediato.
- **Perda de rastreio.** Com scripts avulsos no cron, é difícil saber o que rodou quando, o que falhou e por quê. O histórico vira uma caixa-preta.
- **Falta de dependências explícitas.** O cron não sabe que o job B só pode rodar depois que o job A terminar. Você precisa codificar isso manualmente, o que não escala.

**A diferença entre agendar e orquestrar**

Agendar é dizer "rode às 03h". Orquestrar é dizer "rode às 03h, mas só se o dado de ontem estiver disponível, e depois que esse job terminar, dispare os dois jobs seguintes em paralelo, e se qualquer um falhar, tente mais três vezes com espera exponencial".

Orquestração resolve um problema de coordenação. Ela dá visibilidade, controle e auditoria ao fluxo de dados.

**Quando faz sentido usar um orquestrador**

Não todo pipeline precisa de Airflow. Um script simples que roda uma vez por dia sem dependências pode viver no cron sem problema. O orquestrador vale a pena quando:

- Há dependências entre tarefas ou entre pipelines distintos.
- O pipeline precisa ser reexecutado (backfill) de forma segura.
- É necessário monitorar SLA e receber alertas.
- A equipe precisa inspecionar histórico de execuções.
- Há múltiplos autores de pipelines que precisam de um padrão comum.

**Referência do livro (Cap. 6, Data Flow Design Patterns)**

O padrão *Local Sequencer* descreve exatamente esse problema: quando um job monolítico cresce a ponto de ser ininteligível, a solução é decompô-lo em tarefas sequenciais com dependências explícitas. A separação melhora a leitura do pipeline, facilita retries pontuais e define fronteiras de reprocessamento claras.

## 2.2 Arquitetura do Apache Airflow

Airflow é um orquestrador de workflows declarado em Python. Para trabalhar bem com ele, é fundamental conhecer seus componentes e o papel de cada um.

**Os componentes principais**

- **Webserver (API Server, a partir do Airflow 3.x).** É a interface visual e REST API. Você acessa a UI no `localhost:8081`, visualiza DAGs, loga nas tasks, força execuções manuais e monitora o estado dos pipelines. No Airflow 3.1.x (versão usada nesta trilha), o componente foi renomeado para `airflow-apiserver`.

- **Scheduler.** É o componente mais crítico. Ele varre os arquivos de DAG, determina quais tasks precisam ser enfileiradas com base nas dependências e no cronograma, e delega a execução para os workers. O scheduler não executa código de negócio diretamente, apenas toma decisões de agendamento.

- **Worker.** Executa o código das tasks. No modelo com Celery Executor, múltiplos workers podem rodar em paralelo, cada um em contêineres separados. No LocalExecutor (típico de ambientes de desenvolvimento), as tasks rodam em processos locais do scheduler.

- **Triggerer.** Componente introduzido no Airflow 2.2 para suportar *deferrable operators*. Ele gerencia tarefas que ficam esperando um evento externo (como uma API responder ou um arquivo aparecer) sem bloquear um worker. É útil em pipelines com muitos sensors.

- **Metastore (banco de dados).** O estado de todas as execuções é persistido em um banco relacional, geralmente PostgreSQL em produção. Inclui o histórico de DAG runs, o estado de cada task (queued, running, success, failed, skipped), logs resumidos e configurações.

- **Redis (ou outro broker de mensagens).** Usado no modelo com Celery Executor para enfileirar tasks entre o scheduler e os workers. O scheduler coloca a task na fila; o worker consome.

- **Init.** No Docker Compose local, o serviço `airflow-init` é um job de bootstrap que cria o banco, aplica migrações e cria o usuário admin. Roda uma única vez antes dos demais serviços subirem.

**Fluxo de uma execução**

1. O scheduler lê os arquivos `.py` da pasta `dags/`.
2. Identifica que uma DAG deve rodar (por schedule ou trigger manual).
3. Cria um *DAG run* no metastore e enfileira as tasks elegíveis.
4. O worker pega a task da fila, executa o código Python correspondente e reporta o resultado ao metastore.
5. O scheduler usa o resultado para determinar se a próxima task na dependência pode ser enfileirada.
6. A UI exibe o estado em tempo quase real.

**Por que o scheduler não executa tasks**

Se o scheduler executasse tasks, uma task lenta ou que consome muita memória poderia travar o agendamento de todas as outras DAGs. A separação de responsabilidades é deliberada e essencial para escalabilidade.

## 2.3 DAGs, tasks e dependências na prática

**O que é uma DAG**

DAG significa *Directed Acyclic Graph*. No Airflow, é o objeto principal que representa um pipeline. Ele define as tasks e a ordem em que devem rodar. "Acíclico" significa que não pode haver ciclos: task A → task B → task A nunca é permitido.

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
- `BranchPythonOperator`: avalia uma condição e decide qual branch seguir.

**catchup e start_date**

O `start_date` define quando a DAG começa a existir no tempo. Se `catchup=True` (padrão), o Airflow vai tentar rodar todos os intervalos entre `start_date` e hoje que ainda não foram executados, isso é backfill automático. Em ambientes de produção com dados reais, isso pode ser perigoso se o pipeline não for idempotente. Em desenvolvimento, use `catchup=False`.

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

**Exemplo da DAG de marketing**

A DAG didática desta sessão tem a seguinte sequência:

```
extract_costs -> extract_events -> build_daily_metrics -> publish_report
```

Cada task simula uma etapa real de um pipeline de marketing:

- `extract_costs`: lê custos por campanha.
- `extract_events`: lê eventos de usuários.
- `build_daily_metrics`: agrega as métricas diárias.
- `publish_report`: disponibiliza o relatório para consumo.

**Referência do livro (Cap. 6, Local Sequencer)**

Este pipeline segue o padrão *Local Sequencer*: tarefas encadeadas em sequência, onde cada uma depende da anterior. A vantagem prática é que, se `build_daily_metrics` falhar, o Airflow reexecuta apenas essa task, sem precisar refazer a extração, que pode ser cara ou ter janelas de tempo limitadas.

## 2.4 Idempotência e retries

**O que é idempotência em dados**

Uma operação é idempotente quando pode ser executada múltiplas vezes e sempre produz o mesmo resultado. Em dados, isso significa que rodar o mesmo pipeline duas vezes não duplica registros, não gera inconsistências, e produz exatamente o mesmo dataset que uma única execução produziria.

Idempotência não é opcional em engenharia de dados: retries acontecem, falhas parciais acontecem, e backfills são necessários. Se o pipeline não for idempotente, cada retry pode ser uma bomba-relógio.

**Por que duplicatas são o pior cenário**

Quando um pipeline duplica dados, há dois caminhos possíveis:

1. Duplicatas identificáveis: você tem chave primária, pode deduplicar. Caro, mas possível.
2. Duplicatas não identificáveis: sem chave única, não há como saber qual registro é a repetição. Esse é o cenário descrito como pesadelo no Cap. 4 do livro de referência.

**Padrões de idempotência (Cap. 4 do livro)**

O livro apresenta três famílias principais:

- **Fast Metadata Cleaner**: em vez de `DELETE FROM tabela WHERE ...` (caro em tabelas grandes), usa `TRUNCATE TABLE` ou `DROP + CREATE` por partição. Opera na camada de metadados, que é ordens de magnitude mais rápida que varrer dados.

- **Data Overwrite**: quando não há camada de metadados (ex: object store puro), usa `INSERT OVERWRITE` ou equivalente. No Spark, isso é `input_data.write.mode('overwrite')`.

- **Merger (UPSERT)**: para datasets incrementais onde não se tem o conjunto completo, usa a operação `MERGE INTO ... USING ...`. Aplica insert se o registro é novo, update se já existe. Deletes precisam ser expressos como soft deletes (campo `is_deleted`).

**Idempotência aplicada ao Airflow**

Na DAG de marketing, a task `publish_report` é o ponto mais sensível. Se ela rodar duas vezes, o relatório pode ser duplicado para os consumidores. A solução é garantir que o relatório seja identificado por data de execução (chave idempotente) e que a escrita seja overwrite por partição de data, e não append.

**Retries e idempotência andam juntos**

Configurar `retries=3` em uma task não idempotente é aumentar a probabilidade de problema, não de solução. Antes de habilitar retries, certifique-se de que a task pode ser reexecutada sem efeitos colaterais.

## 2.5 Exercícios e entregáveis

**Exercício 1, Matriz de decisão de orquestrador**

Objetivo: entender quando usar orquestrador vs. cron vs. sem automação.

Construa uma tabela com pelo menos 5 cenários (reais ou hipotéticos) e, para cada um, justifique a escolha de ferramenta:

| Cenário | Dependências? | Retries? | Backfill? | Ferramenta recomendada | Justificativa |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Entregável: tabela preenchida com 5 cenários + 2 parágrafos de justificativa técnica.

---

**Exercício 2, Blueprint de camadas bronze/silver/gold**

Objetivo: definir o padrão de armazenamento do Projeto 1.

Para cada camada, defina:
- Formato de arquivo
- Table format
- Estratégia de particionamento
- Política de retenção
- Critério de promoção para a próxima camada

Entregável: tabela de decisão por camada (os conceitos de table format e particionamento são detalhados nos capítulos 3 e 4).

---

**Exercício 3, Mini ADR de table format**

Objetivo: documentar formalmente a decisão de table format.

Um ADR (Architecture Decision Record) é um documento curto que registra uma decisão técnica e suas justificativas. Escreva um mini ADR com:

- **Contexto:** qual é o problema que motivou a decisão.
- **Decisão:** qual table format foi escolhido.
- **Alternativas consideradas:** Hive, Iceberg e Delta, com prós e contras de cada um para o contexto do Projeto 1.
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
