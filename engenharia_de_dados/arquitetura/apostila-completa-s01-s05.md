# Apostila Completa — Engenharia de Dados: Sessões 01 a 05

> Trilha de Engenharia de Dados com foco em arquitetura, orquestração e armazenamento.
> Conduzida por Iuri Zambotto com Paulo Shindi. Mentorado: Aurelius Oliveira.

---

## Sumário

- [Prefácio — O Projeto 1 como fio condutor](#prefácio--o-projeto-1-como-fio-condutor)
- [Capítulo 1 — Sessão 01: Alinhamento e Diagnóstico](#capítulo-1--sessão-01-alinhamento-e-diagnóstico)
  - [1.1 O Projeto 1: startup de marketing/e-commerce](#11-o-projeto-1-startup-de-marketinge-commerce)
  - [1.2 Ciclo de vida dos dados](#12-ciclo-de-vida-dos-dados)
  - [1.3 O que é um data product](#13-o-que-é-um-data-product)
  - [1.4 Métricas de negócio vs. métricas técnicas](#14-métricas-de-negócio-vs-métricas-técnicas)
  - [1.5 Hipóteses mensuráveis e critérios de sucesso](#15-hipóteses-mensuráveis-e-critérios-de-sucesso)
  - [1.6 Exemplos do domínio](#16-exemplos-do-domínio)
  - [1.7 Exercícios e entregáveis](#17-exercícios-e-entregáveis)
- [Capítulo 2 — Sessão 02: Orquestração com Apache Airflow](#capítulo-2--sessão-02-orquestração-com-apache-airflow)
  - [2.1 Por que orquestrar pipelines de dados](#21-por-que-orquestrar-pipelines-de-dados)
  - [2.2 Arquitetura do Apache Airflow](#22-arquitetura-do-apache-airflow)
  - [2.3 DAGs, tasks e dependências na prática](#23-dags-tasks-e-dependências-na-prática)
  - [2.4 Idempotência e retries](#24-idempotência-e-retries)
  - [2.5 Exercícios e entregáveis](#25-exercícios-e-entregáveis)
- [Capítulo 3 — Sessão 03: CDC, Formatos de Arquivo e Tipos de Tabela](#capítulo-3--sessão-03-cdc-formatos-de-arquivo-e-tipos-de-tabela)
  - [3.1 Change Data Capture (CDC) — conceito e lifecycle](#31-change-data-capture-cdc--conceito-e-lifecycle)
  - [3.2 CDC por ciclo de vida de ID — regras e pitfalls](#32-cdc-por-ciclo-de-vida-de-id--regras-e-pitfalls)
  - [3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC](#33-formatos-de-arquivo-csv-jsonl-parquet-e-orc)
  - [3.4 Tipos de tabela: Hive, Iceberg e Delta Lake](#34-tipos-de-tabela-hive-iceberg-e-delta-lake)
  - [3.5 Camadas bronze, silver e gold](#35-camadas-bronze-silver-e-gold)
  - [3.6 Exercícios e entregáveis](#36-exercícios-e-entregáveis)
- [Capítulo 4 — Sessão 04: Particionamento e Performance de Consultas](#capítulo-4--sessão-04-particionamento-e-performance-de-consultas)
  - [4.0 Visão integrada do Projeto 1](#40-visão-integrada-do-projeto-1)
  - [4.1 Por que particionamento importa](#41-por-que-particionamento-importa)
  - [4.2 Como o particionamento físico funciona](#42-como-o-particionamento-físico-funciona)
  - [4.3 Partition pruning — o mecanismo central](#43-partition-pruning--o-mecanismo-central)
  - [4.4 Estratégias de particionamento](#44-estratégias-de-particionamento)
  - [4.5 Cardinalidade e escolha de chave de partição](#45-cardinalidade-e-escolha-de-chave-de-partição)
  - [4.6 Skew de partição](#46-skew-de-partição)
  - [4.7 Hot partitions](#47-hot-partitions)
  - [4.8 Custo versus performance](#48-custo-versus-performance)
  - [4.9 A stack do laboratório: MinIO, Hive Metastore, Trino e Airflow](#49-a-stack-do-laboratório-minio-hive-metastore-trino-e-airflow)
  - [4.10 Laboratório integrado: CDC → MinIO → Trino → particionamento](#410-laboratório-integrado-cdc--minio--trino--particionamento)
  - [4.11 Análise do domínio de marketing](#411-análise-do-domínio-de-marketing)
  - [4.12 Exercícios e entregáveis](#412-exercícios-e-entregáveis)
- [Capítulo 5 — Sessão 05: Fontes, Arquitetura e Contratos de Dados](#capítulo-5--sessão-05-fontes-arquitetura-e-contratos-de-dados)
  - [5.1 Perguntas de negócio por stakeholder](#51-perguntas-de-negócio-por-stakeholder)
  - [5.2 Modelo de dados — as cinco entidades](#52-modelo-de-dados--as-cinco-entidades)
  - [5.3 Natureza das fontes](#53-natureza-das-fontes)
  - [5.4 Ferramentas de ingestão — categorias e exemplos](#54-ferramentas-de-ingestão--categorias-e-exemplos)
  - [5.5 Make vs buy — critérios para um time pequeno](#55-make-vs-buy--critérios-para-um-time-pequeno)
  - [5.6 Contratos de dados v0](#56-contratos-de-dados-v0)
  - [5.7 Exercícios e entregáveis](#57-exercícios-e-entregáveis)
  - [5.8 O que deliberadamente não decidir agora](#58-o-que-deliberadamente-não-decidir-agora)
- [Referências](#referências)

---

## Prefácio — O Projeto 1 como fio condutor

Esta apostila unifica o conteúdo das cinco primeiras sessões da trilha de Engenharia de Dados. Em vez de cinco documentos isolados, você tem aqui um único guia de estudo com progressão explícita — cada capítulo referencia o anterior quando os conceitos são pré-requisito para o seguinte.

O fio condutor é o **Projeto 1**: uma startup fictícia de marketing/e-commerce que gerencia campanhas pagas, tem uma base de usuários em crescimento e precisa responder perguntas reais de negócio (ROI por canal, taxa de conversão, risco de churn) com dados heterogêneos e em diferentes latências.

Essa empresa não é um exemplo decorativo. Ela aparece em todos os capítulos porque a engenharia de dados não existe no vácuo — existe para responder perguntas de negócio. Cada decisão técnica apresentada nesta apostila (orquestrar com Airflow, capturar mudanças via CDC, armazenar em Parquet com partição por data) tem uma justificativa que começa na necessidade do negócio, não na ferramenta.

**Como usar este documento**

- Para **leitura linear**: siga a ordem dos capítulos. O conteúdo foi estruturado para construir conhecimento incrementalmente.
- Para **revisão pontual**: use o sumário para navegar diretamente ao tópico que precisa revisar.
- Para **estudo de um conceito específico**: cada seção é autossuficiente dentro do capítulo, mas as referências cruzadas indicam onde o conceito aparece antes ou depois.

---

## Capítulo 1 — Sessão 01: Alinhamento e Diagnóstico

> Este capítulo estabelece o contexto do Projeto 1 e os conceitos fundamentais que servem de base para todos os capítulos seguintes.

### 1.1 O Projeto 1: startup de marketing/e-commerce

O Projeto 1 é o fio condutor de toda esta trilha. Ele representa uma startup fictícia que atua no segmento de marketing e e-commerce, gerenciando campanhas de aquisição paga em múltiplos canais (Google Ads, Meta Ads, TikTok Ads) com uma base de usuários em crescimento.

**Contexto do negócio**

O negócio precisa responder perguntas como:

- Qual campanha está gerando mais receita este mês?
- Quais canais trazem o melhor retorno sobre investimento (ROI)?
- Quais usuários estão em risco de deixar de usar o produto?
- Onde no funil de conversão estamos perdendo mais usuários?

Para responder essas perguntas, a empresa precisa integrar dados de múltiplas fontes com diferentes naturezas: um banco relacional que armazena cadastros de usuários e campanhas, uma API externa de mídia que reporta os custos de anúncios, e um sistema de eventos em tempo real que captura o comportamento dos usuários no produto.

**O time de dados**

O time é pequeno. Isso tem implicações diretas nas decisões de arquitetura: cada ferramenta escolhida precisa ser mantida com custo operacional controlado, por poucos engenheiros. Soluções enterprise que exigem equipes especializadas para operar não se encaixam nesse contexto. O Capítulo 5 retoma esse critério na discussão de make vs buy.

**As cinco entidades do domínio**

O domínio do Projeto 1 é modelado em cinco entidades que serão usadas em todos os capítulos:

| Entidade | O que representa |
|---|---|
| `users` | Cadastro dos usuários da plataforma |
| `campaigns` | Campanhas de marketing criadas e gerenciadas |
| `events` | Eventos de comportamento dos usuários no funil de conversão |
| `costs` | Custos diários por campanha e canal de mídia |
| `crm` | Dados de relacionamento e score de risco de churn por usuário |

As entidades são conectadas por duas chaves: `user_id` une `users`, `events` e `crm`; `campaign_id` une `campaigns`, `costs` e `events`. A entidade `events` é o centro do modelo: ela registra cada interação entre um usuário e uma campanha ao longo do funil.

### 1.2 Ciclo de vida dos dados

Antes de projetar qualquer pipeline, é necessário entender como os dados se movem e se transformam. O ciclo de vida dos dados tem quatro etapas principais.

**1. Ingestão**

Os dados nascem em sistemas de origem: o banco de dados da aplicação, APIs de fornecedores, sistemas de eventos. A ingestão é o processo de extrair esses dados e movê-los para o ambiente de dados da empresa.

A natureza da fonte determina como a ingestão funciona. Sistemas transacionais como bancos de dados relacionais podem ser capturados via CDC (Change Data Capture), que registra cada alteração individual. APIs externas são extraídas em lotes periódicos (batch). Sistemas de eventos em tempo real usam streaming. Essas estratégias são detalhadas no Capítulo 3 (CDC) e no Capítulo 5 (escolha por fonte).

**2. Transformação**

Dados brutos raramente estão prontos para análise. A transformação cobre:

- Limpeza: remoção de duplicatas, tratamento de nulos, padronização de formatos.
- Enriquecimento: join com tabelas de referência, adição de campos calculados.
- Agregação: criação de métricas resumidas (contagens, somas, médias por período).

A transformação é executada por pipelines que precisam ser confiáveis, rerreexecutáveis e monitorados. O Apache Airflow, apresentado no Capítulo 2, é a ferramenta que orquestra esse fluxo.

**3. Modelagem**

Modelagem é a etapa de estruturar os dados transformados de forma que respondam perguntas de negócio com eficiência. Envolve decisões de granularidade (qual é o grão de cada tabela?), de chaves e relações (como as tabelas se conectam?), de formatos de armazenamento (Capítulo 3) e de estratégia de particionamento (Capítulo 4).

**4. Consumo**

O dado modelado é consumido por analistas, dashboards, modelos de machine learning ou APIs de produto. O consumo é o teste final da qualidade do trabalho: se os dados chegam corretos, frescos e com eficiência ao consumidor, o pipeline cumpriu seu objetivo.

**A sequência no Projeto 1**

```
[PostgreSQL / API / Kafka]
         |
   [Ingestão + CDC]
         |
    [Bronze — raw]
         |
   [Silver — curado]
         |
    [Gold — métricas]
         |
    [BI / Análise]
```

Essa sequência — construída ao longo de toda a trilha — é o que conecta uma pergunta do CEO ("qual campanha gerou mais ROI?") a um registro em um banco de dados de origem.

### 1.3 O que é um data product

Um data product é qualquer ativo de dados construído com a intenção de ser consumido por um usuário, interno ou externo, para tomar decisões. Não é apenas um dataset — é um serviço com garantias.

**Quatro atributos de um data product de qualidade**

**Utilidade:** o data product resolve um problema real de negócio. Uma tabela de eventos que ninguém usa não é um data product — é um dado sem destinatário. O dado só tem valor quando existe uma pergunta para responder.

Para o Projeto 1, um exemplo de data product com utilidade clara: uma tabela gold com ROI diário por campanha, consumida pelo time de marketing toda manhã para ajustar o budget de anúncios do dia.

**Confiabilidade:** o consumidor pode confiar no dado. Isso inclui ausência de duplicatas, valores dentro dos intervalos esperados, chaves primárias sem nulos e cobertura temporal completa. Um dado que "parece certo" mas que o consumidor não pode verificar não é confiável — é uma suposição.

**Tempo de entrega (freshness):** o dado está disponível quando o consumidor precisa. Um relatório de ROI que aparece às 15h de um dia em que a decisão de budget acontece às 9h não cumpre seu propósito. O SLA de entrega é tão importante quanto o conteúdo.

**Qualidade percebida:** o consumidor entende o que está recebendo. Isso inclui documentação do schema, definições dos campos, histórico de mudanças e comunicação proativa quando algo mudar. Qualidade percebida é sobre confiança, e confiança se constrói com transparência ao longo do tempo.

**A diferença entre dado e data product**

| Dado bruto | Data product |
|---|---|
| Sem destinatário definido | Tem consumidor e caso de uso |
| Sem SLA | Tem SLA de entrega |
| Sem documentação | Schema documentado |
| Sem monitoramento | Alertas de qualidade configurados |
| Sem contrato | Contrato de dados definido |

O Capítulo 5 detalha os contratos de dados, que são o mecanismo formal de definir e comunicar o que o data product entrega e com quais garantias.

### 1.4 Métricas de negócio vs. métricas técnicas

Uma confusão comum no início da carreira em dados é tratar métricas técnicas como objetivo final, quando elas são instrumentos a serviço das métricas de negócio.

**Métricas de negócio**

São as métricas que o negócio usa para tomar decisões. No domínio do Projeto 1:

- **CAC (Custo de Aquisição de Cliente):** quanto custa, em média, adquirir um novo cliente por canal. Calculado como total de gastos em mídia dividido pelo número de novos usuários no período.
- **ROI por campanha:** retorno sobre o investimento em publicidade. Calculado como `(receita gerada − custo) / custo`. Um ROI negativo indica que o custo de aquisição ainda supera a receita gerada.
- **Taxa de conversão do funil:** percentual de usuários que completam cada etapa do funil (visita → signup → checkout → purchase).
- **Churn:** taxa de usuários que param de usar o produto em um período. Pode ser segmentado por canal de aquisição, por segmento de usuário ou por período.
- **LTV (Lifetime Value):** valor total esperado de um cliente ao longo de seu relacionamento com o produto.

**Métricas técnicas**

São métricas que indicam a saúde da infraestrutura de dados. Elas não respondem perguntas de negócio diretamente, mas alertam quando algo está errado no pipeline que alimenta os dados de negócio:

- **Latência de ingestão:** tempo entre o evento ocorrer na origem e estar disponível no Bronze.
- **Freshness:** quão recente é o dado mais recente disponível em cada tabela.
- **Taxa de erro:** percentual de registros rejeitados por violações de schema ou regras de qualidade.
- **Cobertura:** se todos os registros esperados chegaram (detecção de lacunas no histórico).
- **Tamanho médio de arquivo por partição:** indicador de small files e skew (conceitos aprofundados no Capítulo 4).

**A relação entre as duas**

As métricas técnicas servem as métricas de negócio. Se a latência de ingestão aumenta, o ROI calculado no relatório da manhã pode estar desatualizado. Se a taxa de erro sobe, a taxa de conversão pode estar subestimada por perda de eventos. A engenharia de dados existe para manter as métricas técnicas dentro de níveis que tornam as métricas de negócio confiáveis.

### 1.5 Hipóteses mensuráveis e critérios de sucesso

Antes de construir qualquer pipeline, é necessário definir o que sucesso significa. Hipóteses mensuráveis traduzem objetivos de negócio em afirmações verificáveis com dados.

**O formato SMART**

Uma boa hipótese ou meta é:
- **Específica (Specific):** diz exatamente o que será medido.
- **Mensurável (Measurable):** tem uma métrica e um valor-alvo.
- **Alcançável (Achievable):** é realista dado o contexto.
- **Relevante (Relevant):** responde a uma necessidade real do negócio.
- **Temporal (Time-bound):** tem um prazo.

**Exemplos aplicados ao Projeto 1**

| Objetivo vago | Hipótese SMART |
|---|---|
| "Melhorar a conversão" | "Aumentar a taxa de conversão do funil de 1,5% para 2,0% até o final do trimestre, medida pela razão compras/visitas na tabela `events` agrupada por semana" |
| "Reduzir o CAC" | "Reduzir o CAC médio do canal Meta Ads de R$45 para R$38 em 60 dias, calculado como total de custos na tabela `costs` dividido por novos usuários na tabela `users`" |
| "Detectar churn" | "Identificar usuários com score de churn > 0,7 na tabela `crm` com antecedência de 7 dias e acurácia de pelo menos 70%, medida por comparação com saídas reais do período seguinte" |

**Critérios de sucesso do pipeline do Projeto 1**

Para o pipeline que construiremos ao longo da trilha, os critérios de sucesso técnicos são:

1. Todas as cinco entidades do domínio estão disponíveis nas camadas bronze e silver com schemas documentados.
2. A camada gold contém pelo menos uma tabela que responde a cada grupo de stakeholder (CEO, Growth, Operações, Analytics).
3. Os SLAs de entrega são cumpridos: tabelas de CDC em até 30 minutos após alteração na origem; custos do dia anterior disponíveis até às 8h; eventos com latência máxima de 5 minutos.
4. O pipeline é idempotente: reexecutar qualquer DAG no Airflow não duplica dados nem gera inconsistências.

### 1.6 Exemplos do domínio

Esta seção apresenta exemplos concretos com dados sintéticos do domínio de marketing. Esses dados são gerados pelo módulo `cdc_generator` e servem como base para os laboratórios das sessões seguintes.

**Métrica de conversão por campanha**

Uma tabela básica de desempenho de campanha teria esta estrutura:

| campaign_id | visitas | compras | taxa_conversão | custo (R$) | receita (R$) | ROI |
|---|---|---|---|---|---|---|
| camp_001 | 450 | 6 | 1,33% | 2.000 | 480 | −0,76 |
| camp_002 | 456 | 15 | 3,29% | 2.000 | 1.125 | −0,44 |

`camp_002` tem taxa de conversão mais de duas vezes maior que `camp_001`, mas ambas têm ROI negativo — o custo de aquisição ainda supera a receita gerada. A hipótese de negócio seria: "qual ajuste nas campanhas levaria o ROI para positivo primeiro?"

**Funil de conversão**

O funil rastreia a jornada do usuário por estágios. Cada evento é um registro na tabela `events`.

```
visita → signup → checkout → purchase
```

| Estágio | Usuários | Taxa de avanço |
|---|---|---|
| visita | 1.000 | 100% |
| signup | 250 | 25% |
| checkout | 80 | 32% |
| purchase | 25 | 31% |

A queda mais pronunciada está entre "visita" e "signup": 75% dos usuários saem nessa etapa. Esse é o ponto de investigação prioritário.

**Risco de churn por segmento**

A tabela `crm` contém um score de churn por usuário. Uma análise simples por segmento revela onde atuar:

| segmento | usuários totais | em risco (score > 0,7) | taxa de risco |
|---|---|---|---|
| premium | 500 | 45 | 9% |
| free | 2.000 | 680 | 34% |

Usuários do segmento `free` têm taxa de risco quatro vezes maior. Isso pode justificar campanhas de retenção direcionadas — e o pipeline de dados é o que torna esse tipo de análise possível e repetível.

### 1.7 Exercícios e entregáveis

**Exercício 1 — Metas SMART**

Objetivo: traduzir objetivos de negócio genéricos em hipóteses verificáveis com dados.

Para cada um dos três objetivos abaixo, reescreva no formato SMART indicando a métrica, o valor-alvo, o prazo e qual tabela do domínio seria usada para medir:

1. "Quero aumentar a receita das campanhas."
2. "Quero diminuir o custo por clique."
3. "Quero melhorar a retenção dos usuários premium."

Entregável: três hipóteses no formato SMART com referência às entidades do Projeto 1.

---

**Exercício 2 — Mapa de perguntas de negócio**

Objetivo: praticar o raciocínio que conecta perguntas de stakeholders a fontes de dados.

Construa uma tabela com 10 perguntas de negócio do domínio de marketing/e-commerce. Use as perguntas da seção 5.1 (Capítulo 5) como ponto de partida. Para cada pergunta, identifique:

- Qual stakeholder faria essa pergunta.
- Quais entidades do domínio são necessárias para respondê-la.
- Qual é a frequência de atualização necessária (tempo real, diário, semanal).

Entregável: tabela com 10 perguntas priorizadas, stakeholder, entidades e frequência.

---

**Exercício 3 — Inventário inicial de fontes**

Objetivo: mapear as fontes de dados necessárias para o Projeto 1.

Construa uma tabela com as cinco entidades do domínio. Para cada entidade, preencha:

- Tipo de fonte (banco relacional, API, sistema de eventos).
- Frequência de atualização esperada.
- Time dono dos dados na origem.
- Criticidade para as perguntas de negócio (alta, média, baixa).

Entregável: tabela de inventário de fontes com as colunas acima preenchidas.

---

## Capítulo 2 — Sessão 02: Orquestração com Apache Airflow

> Pré-requisito: Capítulo 1 — o Airflow é a ferramenta que garante a execução confiável e ordenada do pipeline descrito no ciclo de vida dos dados da Sessão 01.

### 2.1 Por que orquestrar pipelines de dados

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

**Referência do livro (Cap. 6 — Data Flow Design Patterns)**

O padrão *Local Sequencer* descreve exatamente esse problema: quando um job monolítico cresce a ponto de ser ininteligível, a solução é decompô-lo em tarefas sequenciais com dependências explícitas. A separação melhora a leitura do pipeline, facilita retries pontuais e define fronteiras de reprocessamento claras.

### 2.2 Arquitetura do Apache Airflow

Airflow é um orquestrador de workflows declarado em Python. Para trabalhar bem com ele, é fundamental conhecer seus componentes e o papel de cada um.

**Os componentes principais**

- **Webserver (API Server, a partir do Airflow 3.x).** É a interface visual e REST API. Você acessa a UI no `localhost:8081`, visualiza DAGs, loga nas tasks, força execuções manuais e monitora o estado dos pipelines. No Airflow 3.1.x (versão usada nesta trilha), o componente foi renomeado para `airflow-apiserver`.

- **Scheduler.** É o componente mais crítico. Ele varre os arquivos de DAG, determina quais tasks precisam ser enfileiradas com base nas dependências e no cronograma, e delega a execução para os workers. O scheduler não executa código de negócio diretamente — apenas toma decisões de agendamento.

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

### 2.3 DAGs, tasks e dependências na prática

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

O `start_date` define quando a DAG começa a existir no tempo. Se `catchup=True` (padrão), o Airflow vai tentar rodar todos os intervalos entre `start_date` e hoje que ainda não foram executados — isso é backfill automático. Em ambientes de produção com dados reais, isso pode ser perigoso se o pipeline não for idempotente. Em desenvolvimento, use `catchup=False`.

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

**Referência do livro (Cap. 6 — Local Sequencer)**

Este pipeline segue o padrão *Local Sequencer*: tarefas encadeadas em sequência, onde cada uma depende da anterior. A vantagem prática é que, se `build_daily_metrics` falhar, o Airflow reexecuta apenas essa task, sem precisar refazer a extração, que pode ser cara ou ter janelas de tempo limitadas.

### 2.4 Idempotência e retries

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

### 2.5 Exercícios e entregáveis

**Exercício 1 — Matriz de decisão de orquestrador**

Objetivo: entender quando usar orquestrador vs. cron vs. sem automação.

Construa uma tabela com pelo menos 5 cenários (reais ou hipotéticos) e, para cada um, justifique a escolha de ferramenta:

| Cenário | Dependências? | Retries? | Backfill? | Ferramenta recomendada | Justificativa |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Entregável: tabela preenchida com 5 cenários + 2 parágrafos de justificativa técnica.

---

**Exercício 2 — Blueprint de camadas bronze/silver/gold**

Objetivo: definir o padrão de armazenamento do Projeto 1.

Para cada camada, defina:
- Formato de arquivo
- Table format
- Estratégia de particionamento
- Política de retenção
- Critério de promoção para a próxima camada

Entregável: tabela de decisão por camada (os conceitos de table format e particionamento são detalhados nos capítulos 3 e 4).

---

**Exercício 3 — Mini ADR de table format**

Objetivo: documentar formalmente a decisão de table format.

Um ADR (Architecture Decision Record) é um documento curto que registra uma decisão técnica e suas justificativas. Escreva um mini ADR com:

- **Contexto:** qual é o problema que motivou a decisão.
- **Decisão:** qual table format foi escolhido.
- **Alternativas consideradas:** Hive, Iceberg e Delta, com prós e contras de cada um para o contexto do Projeto 1.
- **Consequências:** o que fica mais fácil e o que fica mais difícil com a escolha feita.

Entregável: documento de 1 a 2 páginas com as quatro seções preenchidas.

---

## Capítulo 3 — Sessão 03: CDC, Formatos de Arquivo e Tipos de Tabela

> Pré-requisito: Capítulo 2 — o CDC é a técnica de ingestão que alimenta as DAGs do Airflow descritas na Sessão 02.

### 3.1 Change Data Capture (CDC) — conceito e lifecycle

**O que é CDC e por que existe**

Change Data Capture é o conjunto de técnicas para capturar e representar as mudanças que ocorrem em um banco de dados de origem. Em vez de ler a tabela inteira a cada ciclo (snapshot completo), o CDC captura apenas o que mudou: inserções, atualizações e deleções.

O CDC nasce de uma necessidade real: dados mudam. Um usuário atualiza o endereço, uma campanha é cancelada, um pedido é deletado. Se você só tiver o snapshot mais recente, perdeu a história do que aconteceu. Se você capturar cada evento de mudança, tem uma trilha auditável e pode reconstruir qualquer estado anterior.

**Métodos de captura**

- **Log-based CDC**: lê o write-ahead log (WAL) do banco de dados. É o método mais confiável e menos intrusivo. Ferramentas como Debezium fazem isso para PostgreSQL, MySQL, MongoDB e outros. Cada operação DML (INSERT, UPDATE, DELETE) gera um evento no log.

- **Trigger-based CDC**: triggers no banco disparam escrita em uma tabela de auditoria a cada mudança. Funciona, mas tem custo de escrita no próprio banco de origem.

- **Timestamp-based CDC**: lê registros onde `updated_at > last_processed_time`. Simples de implementar, mas não captura deleções e depende de o campo de timestamp existir e ser confiável.

- **Geração sintética**: para fins didáticos, geramos os eventos de CDC programaticamente com regras de lifecycle controladas. O módulo `cdc_generator` produz arquivos `*__cdc.csv` com essa abordagem.

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

### 3.2 CDC por ciclo de vida de ID — regras e pitfalls

Esta é a regra mais importante desta sessão e precisa ser internalizada.

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

Quando um registro é deletado no banco de origem, ele deixa de existir. Qualquer tentativa de referenciar aquele ID depois disso é ou um erro na captura CDC ou uma reinserção (novo ciclo, novo contexto). Para fins de lifecycle, o delete é o fim de vida daquele ID específico.

**Evidência real do dataset desta sessão**

O arquivo `notes/relatorio-cdc-por-id.md` mostra os resultados do dataset `marketing`:

| Tabela | IDs únicos | Inserts | Updates | Deletes | Violações |
|---|---|---|---|---|---|
| `users` | 80 | 80 | 0 | 37 | 0 |
| `campaigns` | 4 | 4 | 0 | 0 | 0 |
| `events` | 80 | 80 | 584 | 2 | 0 |
| `costs` | 4 | 4 | 52 | 0 | 0 |
| `crm` | 80 | 80 | 0 | 27 | 0 |

Zero violações em todas as tabelas. Cada ID começa com `insert`, updates aparecem apenas entre o insert e o possível delete, e nenhum ID reaparece após o delete.

Exemplos de sequências válidas:

- `user_0001` na tabela `users`: `insert → delete` (vida curta)
- `user_0001` na tabela `events`: `insert → update → update → ... → update` (criou e atualizou 8 vezes, ainda ativo)
- `user_0009` na tabela `events`: `insert → update → update → update → delete`

**Os pitfalls mais comuns em CDC**

- **Insert duplicado.** Um evento de insert para um ID que já existe indica erro no pipeline CDC ou problema de deduplicação. O dado não pode ser confiado sem investigação.

- **Update antes do insert.** Se um ID aparece primeiro com `update`, o evento de criação foi perdido. Isso pode acontecer em migrações parciais ou quando a captura CDC começou depois que o registro já existia.

- **Evento após delete.** Se um ID que foi deletado reaparece com `update`, houve um problema sério: ou o delete foi registrado por engano, ou houve reinserção sem novo insert CDC. Ambos indicam inconsistência.

- **Timestamp fora de ordem.** Eventos CDC devem ser processados em ordem temporal por ID. Se o `cdc_event_ts` estiver fora de sequência, o estado reconstruído será incorreto.

- **Soft delete vs hard delete.** Nem todos os bancos geram eventos de delete explícito no CDC. Alguns sistemas usam soft delete: um campo `is_active = false` ou `deleted_at` é atualizado, e o registro permanece na tabela. Nesses casos, o CDC captura um `update`, não um `delete`. É importante saber qual estratégia o banco de origem usa.

**Como validar o lifecycle no código**

A validação implementada no `cdc_generator` segue esta lógica:

1. Agrupar eventos por ID.
2. Ordenar por `cdc_event_ts`.
3. Verificar que o primeiro evento é sempre `insert`.
4. Verificar que após qualquer `delete`, não existem mais eventos para aquele ID.
5. Reportar qualquer violação.

### 3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC

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
- Ambientes Databricks ou EMR onde ambos são suportados — a escolha depende do ecossistema da empresa.

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

**Referência do livro (Cap. 8 — Data Storage Design Patterns)**

O padrão *Horizontal Partitioner* descrito no Cap. 8 complementa diretamente a escolha de formato. Particionar por data no Parquet, por exemplo, é o que permite ao motor de query ignorar partições inteiras e ler apenas o intervalo de tempo relevante. Sem particionamento, até o melhor formato colunar é forçado a escanear blocos desnecessários.

### 3.4 Tipos de tabela: Hive, Iceberg e Delta Lake

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
- Sem time travel nativo.
- Operações de update e delete são limitadas ou ausentes.

Quando ainda faz sentido:
- Pipelines simples de append-only onde não há necessidade de update ou delete.
- Ambientes legados onde a migração para Iceberg ou Delta não vale o custo imediato.
- Quando a engine disponível não suporta os novos formatos.

**Apache Iceberg — o table format moderno e multi-engine**

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

**Delta Lake — o table format do ecossistema Databricks**

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

**Referência do livro (Cap. 4 — Merger Pattern)**

O padrão *Merger* descreve como aplicar incrementos (inserts + updates + soft deletes) de forma idempotente a um dataset existente. A operação `MERGE INTO` do Delta/Iceberg é a implementação nativa desse padrão.

### 3.5 Camadas bronze, silver e gold

A arquitetura medallion (bronze/silver/gold) é um padrão de organização do data lake em camadas com diferentes níveis de curadoria.

**Bronze — dados brutos, fidelidade máxima**

A camada bronze recebe os dados como chegam da origem, com o mínimo de transformação possível. O objetivo é preservar a fidelidade dos dados originais.

Características:
- Formato preferido: JSONL ou CSV (mantém a estrutura original, legível).
- Particionamento por data de ingestão, não de evento.
- Dados podem ter inconsistências, nulos, duplicatas — tudo é preservado.
- Sem remoção de campos, mesmo que sensíveis (com controle de acesso adequado).
- Table format: Hive simples (append-only) ou Iceberg para capturar histórico.

Analogia: é a "fita bruta" da gravação. Tudo que aconteceu está lá.

**Silver — dados curados, prontos para análise**

A camada silver aplica transformações de qualidade: limpeza de nulos, deduplicação, padronização de tipos, enriquecimento com dados de referência.

Características:
- Formato preferido: Parquet (leitura eficiente, schema embutido).
- Particionamento por data de evento (não de ingestão).
- Dados devem atender contratos de schema definidos.
- Pode incluir campos derivados simples.
- Table format: Parquet + Iceberg ou Delta, dependendo da necessidade de upsert.

Analogia: é a "edição do corte" — você removeu os erros, normalizou os dados, mas ainda não produziu o produto final.

**Gold — dados agregados, prontos para consumo**

A camada gold contém datasets prontos para consumo por analistas, dashboards e modelos. São as métricas, agregados e visões de negócio.

Características:
- Formato preferido: Parquet ou Delta/Iceberg.
- Estrutura orientada ao caso de uso (tabela desnormalizada por produto, por região, por canal).
- Alta qualidade garantida.
- Pode ter SLA de atualização definido.

Analogia: é o produto final — o relatório, o dashboard, o número que o stakeholder vai olhar.

**Recomendação para o Projeto 1**

| Camada | Formato | Table Format | Justificativa |
|---|---|---|---|
| Bronze | JSONL / CSV | Hive ou Iceberg | Fidelidade máxima, ingestão direta |
| Silver | Parquet | Iceberg ou Delta | Analytics eficiente, schema estável, suporte a merge |
| Gold | Parquet | Iceberg ou Delta | Performance de query, auditabilidade, SLA |

**Referência do livro (Cap. 9 — AWAP Pattern)**

O padrão *Audit-Write-Audit-Publish* encaixa na transição silver → gold: antes de promover dados para a camada gold, você valida o dataset transformado. Se passar, promove. Se não passar, você tem opções: falha o pipeline, envia para dead-letter, ou promove com anotação de incompletude.

**Referência do livro (Cap. 10 — Flow Interruption Detector)**

A camada bronze é especialmente vulnerável a interrupções de fluxo. O padrão *Flow Interruption Detector* descreve como detectar quando um job parou de escrever dados sem falhar explicitamente. Implementar um detector de freshness na camada bronze previne que o silêncio de um job com bug passe despercebido por horas ou dias.

### 3.6 Exercícios e entregáveis

**Exercício 1 — Matriz de decisão de orquestrador**

Objetivo: aplicar os conceitos de CDC no contexto do Projeto 1.

Dado um arquivo CSV com eventos CDC da tabela `events`:

1. Abra o arquivo com pandas.
2. Agrupe por `event_id`.
3. Ordene por `cdc_event_ts` dentro de cada grupo.
4. Implemente uma função que valida as regras de lifecycle: o primeiro evento deve ser `insert`; após `delete`, não pode haver mais eventos para aquele ID.
5. Imprima o número de IDs com violação.

Entregável: script Python + resultado da validação (número de violações esperado: 0 para o dataset gerado pelo `cdc_generator`).

---

**Exercício 2 — Blueprint de camadas bronze/silver/gold**

Objetivo: definir o padrão de armazenamento do Projeto 1.

Para cada camada, defina:
- Formato de arquivo
- Table format
- Estratégia de particionamento
- Política de retenção
- Critério de promoção para a próxima camada

Entregável: tabela de decisão por camada.

---

**Exercício 3 — Mini ADR de table format**

Objetivo: documentar formalmente a decisão de table format para o Projeto 1.

Escreva um mini ADR com:
- **Contexto:** qual é o problema que motivou a decisão.
- **Decisão:** qual table format foi escolhido.
- **Alternativas consideradas:** Hive, Iceberg e Delta, com prós e contras de cada um para o contexto.
- **Consequências:** o que fica mais fácil e o que fica mais difícil com a escolha feita.

Entregável: documento de 1 a 2 páginas com as quatro seções preenchidas.

---

## Capítulo 4 — Sessão 04: Particionamento e Performance de Consultas

> Pré-requisito: Capítulo 3 — os tipos de tabela (Hive, Iceberg, Delta Lake) são a base sobre a qual o particionamento é aplicado.

### 4.0 Visão integrada do Projeto 1

Antes de escolher uma estratégia de partição, é necessário enxergar o projeto como um todo.

**Mapa simplificado do pipeline**

```
[Origem] -> [CDC] -> [Bronze] -> [Silver] -> [Gold] -> [Consumo]
               ^
               | (Airflow orquestra a ordem e os checks)
```

**O que cada camada resolve**

- **CDC**: representa mudanças (insert/update/delete) de forma auditável.
- **Bronze**: dados brutos, sem transformação (fidelidade máxima).
- **Silver**: dados limpos e padronizados (prontos para análise).
- **Gold**: métricas e tabelas de consumo.
- **Trino**: motor de consulta para validar e explorar.

**Perguntas guia antes de definir particionamento**

- Qual problema de negócio estamos resolvendo?
- Qual o grão de cada tabela?
- Onde os dados nascem e onde precisam chegar?
- O que precisa ser idempotente e onde?
- Qual coluna define o tempo do dado (`event_date`, `updated_at`)?

**Modelagem mínima antes do particionamento**

Particionamento é uma decisão de armazenamento. Antes disso, é necessário ter o básico da modelagem definido:

| Entidade | Grão | Chave principal | Tipo de mudança | Partição sugerida |
|---|---|---|---|---|
| `events` | 1 evento | `event_id` | append-only | `event_date` |
| `campaigns` | 1 campanha | `campaign_id` | upsert | `created_date` |
| `costs` | 1 campanha × dia | (`campaign_id`, `cost_date`) | upsert | `cost_date` |
| `crm` | 1 usuário | `user_id` | upsert | `updated_at` |
| `users` | 1 usuário | `user_id` | upsert | `updated_at` |

Nota: se existir dado sensível (ex: email, telefone), marcar e limitar acesso antes de promover para silver/gold.

### 4.1 Por que particionamento importa

**O cenário sem particionamento**

Imagine uma tabela de eventos com 5 bilhões de registros, cobrindo três anos de histórico. Você precisa calcular o total de cliques da última semana. Sem particionamento, a query precisa varrer todos os 5 bilhões de registros para encontrar os que caem na janela de tempo solicitada. Isso é um *full table scan*: caro, lento, e que cresce linearmente com o volume de dados.

Em sistemas como o Athena (serviço gerenciado da AWS sobre Presto/Trino), você paga por byte escaneado. Um full scan em 5 bilhões de registros pode custar dezenas de dólares por consulta. Multiplique isso por centenas de consultas por dia e o custo torna-se inviável.

**O que o particionamento faz**

Particionamento é a prática de organizar fisicamente os dados em subconjuntos (partições) com base nos valores de uma ou mais colunas. Quando o engine de consulta precisa responder a uma query com filtro sobre a coluna de partição, ele consulta apenas as partições relevantes, ignorando todo o resto.

No exemplo acima: se os eventos estão particionados por data, a query da última semana lê apenas 7 partições de um total de mais de 1000. Em vez de varrer 5 bilhões de registros, o engine lê apenas os da última semana — talvez 30 ou 40 milhões. A redução de custo e de latência é de uma ou duas ordens de magnitude.

**A decisão que mais impacta o custo do data lake**

Particionamento é, frequentemente, a decisão de design de dados com maior impacto direto em custo. Uma escolha errada de chave de partição pode:

- Fazer com que todas as queries continuem sendo full scans.
- Gerar dezenas de milhares de arquivos minúsculos (small files), degradando o próprio mecanismo que deveria melhorar a performance.
- Criar desequilíbrio de tamanho entre partições (*skew*), onde uma partição tem 1000x mais dados que outra.

**Referência do livro (Cap. 8 — Data Storage Design Patterns)**

O padrão *Partitioned Table* apresentado no Cap. 8 é o fundamento de qualquer estratégia de storage em larga escala. A premissa é simples: o acesso aos dados deve ser O(1) em relação ao volume total sempre que possível. Particionar por uma coluna que é filtrada sistematicamente é a forma mais direta de atingir isso.

### 4.2 Como o particionamento físico funciona

**A metáfora do armário de arquivos**

Imagine que você tem 365 pastas, uma para cada dia do ano. Quando alguém pede os documentos de 15 de janeiro, você vai diretamente na pasta "2026-01-15" e pega. Você não abre cada pasta do ano para procurar.

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

O S3 não sabe que aqueles diretórios são partições de uma tabela — ele enxerga apenas objetos com prefixos de caminho. Quem dá significado a essa estrutura é o Hive Metastore.

O Hive Metastore é um serviço que mantém um catálogo de metadados. Ele sabe:

- Que existe uma tabela chamada `events` no schema `marketing`.
- Que essa tabela está armazenada em `s3://bronze/marketing/events/`.
- Que a coluna de partição é `event_date`.
- Quais partições existem, com seus caminhos e estatísticas.

Quando o Trino recebe uma query como `SELECT * FROM hive.marketing.events WHERE event_date = '2026-01-10'`, ele consulta o Hive Metastore para descobrir quais partições existem e quais se encaixam no filtro antes de tocar qualquer arquivo no MinIO.

**Registro de partições**

Para que o Metastore saiba que uma partição existe, ela precisa ser registrada. Isso acontece automaticamente quando você usa `INSERT INTO` via Trino (o Trino registra a partição no metastore após gravar os arquivos), ou quando você executa `MSCK REPAIR TABLE` manualmente.

Se você gravar arquivos diretamente no S3 sem registrar no metastore, as queries não encontrarão os dados.

**A coluna de partição e os arquivos Parquet**

A coluna de partição (`event_date`, neste exemplo) geralmente não é armazenada dentro dos arquivos Parquet de cada partição. Ela está codificada no próprio caminho do diretório. Isso economiza espaço e evita redundância. Quando o engine faz o merge dos dados com o metadado de partição, ele reconstrói a coluna automaticamente a partir do caminho.

### 4.3 Partition pruning — o mecanismo central

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

Em engines modernos como o Trino, existe também o *pushdown* de predicados para o nível de arquivo. O Parquet armazena estatísticas de min/max por *row group*. O Trino pode usar essas estatísticas para pular row groups inteiros dentro de um arquivo Parquet, mesmo após o pruning de partições.

A hierarquia de otimização é:

1. Partition pruning: elimina partições inteiras (não toca os arquivos).
2. File pruning: em formatos como Iceberg, elimina arquivos individuais.
3. Row group pruning: usa estatísticas de min/max dentro de arquivos Parquet.

**Como inspecionar o pruning com EXPLAIN**

No Trino, você pode usar `EXPLAIN` para ver se o engine está fazendo pruning:

```sql
EXPLAIN
SELECT *
FROM hive.marketing.events
WHERE event_date = DATE '2026-01-10';
```

Quando o pruning acontece, a saída mostra algo como:

```
TableScan[hive:marketing:events]
    Constraint: event_date IN (2026-01-10)
```

Isso confirma que o engine só vai ler a partição `event_date=2026-01-10`.

### 4.4 Estratégias de particionamento

**Particionamento por tempo**

A estratégia mais comum em data lakes. Faz sentido quando:

- Os dados têm uma dimensão temporal forte (eventos, transações, logs).
- As queries mais frequentes filtram por período de tempo (dia, semana, mês).
- Os dados chegam de forma incremental e nunca são atualizados em partições antigas.

A granularidade deve ser escolhida com cuidado:

- **Muito grosso (por ano):** cada partição acumula volume enorme, reduzindo o benefício do pruning para queries diárias.
- **Muito fino (por hora ou por minuto):** gera excesso de partições e arquivos minúsculos, aumentando overhead de metadados.
- **Por dia:** o equilíbrio mais comum para dados transacionais.

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

Por exemplo, em uma plataforma multi-país, particionar por `country` faz sentido se a maioria das queries é scoped por país, cada país tem volume similar (sem skew) e o número de países é fixo e baixo.

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
- Qual a cardinalidade dessa coluna?
- Há risco de skew?
- Qual o volume médio por partição? (objetivo: partições entre 128 MB e 1 GB)

### 4.5 Cardinalidade e escolha de chave de partição

**O que é cardinalidade**

Cardinalidade é o número de valores distintos de uma coluna. Alta cardinalidade significa muitos valores distintos (ex: `user_id` com milhões de usuários). Baixa cardinalidade significa poucos valores (ex: `country` com 10 países, `event_type` com 5 tipos).

**Por que alta cardinalidade é problemática para partição**

Se você particionar por `user_id` em uma tabela de 100 milhões de usuários distintos, terá 100 milhões de partições. Os problemas resultantes são:

- **Small files problem:** cada partição gera um ou mais arquivos minúsculos. O S3 tem overhead fixo por arquivo. Milhões de arquivos pequenos degradam drasticamente a performance.
- **Overhead de metastore:** o Hive Metastore precisa armazenar e indexar os metadados de cada partição. Com 100 milhões de partições, o metastore fica lento e instável.
- **Pruning ineficaz:** em alta cardinalidade, o pruning reduz pouco o scan — o custo de gerenciar as partições supera o benefício.

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

### 4.6 Skew de partição

**O que é skew**

Skew (distorção) é o desequilíbrio de tamanho entre partições. Em uma tabela particionada por `event_type`, se 90% dos eventos são do tipo `view` e os outros tipos somam 10%, a partição `event_type=view` será 9 vezes maior que todas as outras juntas.

**Por que skew é um problema**

Em engines distribuídos como o Trino ou o Spark, o trabalho é dividido entre workers. Se uma partição é muito maior que as demais, o worker responsável por ela termina muito depois dos outros. O tempo total da query é limitado pelo worker mais lento. Esse fenômeno é chamado de *stragglers* ou *tail latency*.

**Como detectar skew**

No Trino, você pode inspecionar as estatísticas de partições:

```sql
SELECT partition_key, row_count, data_size
FROM hive.marketing."$partitions";
```

Se os valores de `data_size` variarem em ordens de magnitude, há skew.

**Estratégias para lidar com skew**

- **Mudar a chave de partição:** se a coluna de partição tem skew natural, avaliar uma chave mais equilibrada.
- **Sub-particionar:** adicionar uma segunda dimensão que equilibre a distribuição.
- **Bucketing:** dentro de uma partição, distribuir os dados em N arquivos (buckets) de tamanho similar.
- **Aceitar o skew:** em alguns casos é inevitável e o correto é aceitar e otimizar as queries para a partição grande especificamente.

### 4.7 Hot partitions

**O que são hot partitions**

Hot partition é o fenômeno em que uma partição específica recebe um volume desproporcional de escritas simultâneas. Acontece com frequência em tabelas particionadas por tempo quando vários processos escrevem para o "dia de hoje" ao mesmo tempo.

**Por que é um problema diferente do skew**

Skew é um problema de leitura: a partição é grande e demora para ser lida. Hot partition é um problema de escrita: a partição recebe muitos writes concorrentes, o que pode:

- Causar conflitos de arquivo em formatos sem controle de concorrência como Hive clássico.
- Gerar muitos arquivos pequenos porque cada processo escreve um arquivo separado.
- Sobrecarregar o metastore com atualizações de metadados da partição atual.

**O caso clássico: partição do dia atual**

Em um pipeline de eventos com processamento quase em tempo real, vários workers escrevem para `event_date=2026-03-03` ao longo do dia. Cada job de microbatch gera um arquivo. Ao fim do dia, a partição pode ter centenas ou milhares de arquivos pequenos.

**Estratégias de mitigação**

- **Compaction:** um job periódico (via Airflow, por exemplo) lê todos os arquivos pequenos de uma partição, une-os em arquivos maiores e sobrescreve. O Iceberg e o Delta Lake têm compaction nativo e transacional. No Hive clássico, o processo é manual.
- **Staging area:** em vez de escrever diretamente na partição final, os jobs escrevem em uma área de staging. Um job de merge periódico move os dados para a partição oficial com compaction automática.
- **Controle de concorrência via orquestrador:** o Airflow pode serializar as escritas para a partição do dia atual, evitando múltiplos writers simultâneos.

### 4.8 Custo versus performance

**O trade-off fundamental**

Particionar resolve um problema, mas cria outro. A redução de custo e latência de queries vem com um custo de overhead de gerenciamento: mais partições = mais metadados = mais overhead do metastore = maior latência para operações que varrem o schema inteiro.

**O problema dos small files**

Cada arquivo no S3 tem um custo fixo de operação: um GET request para abrir, um PUT para escrever. Em um Parquet típico, o overhead de abertura é de dezenas de milissegundos. Se uma partição tem 1000 arquivos de 1 KB cada, o engine faz 1000 GETs para ler 1 MB de dados.

A regra prática: arquivos entre **128 MB e 1 GB** são o ideal para queries analíticas em S3. Abaixo de 10 MB, o overhead começa a ser perceptível. Abaixo de 1 MB, é um problema.

**Granularidade de partição versus tamanho de arquivo**

Há uma tensão direta entre granularidade de partição e tamanho de arquivo:

- Particionar por hora gera 24 partições por dia. Se o volume de dados for baixo, cada partição pode ter poucos MB, gerando small files.
- Particionar por mês resolve o small files problem, mas reduz drasticamente o benefício do pruning para queries diárias.

A decisão correta depende do volume de dados. A regra de ouro: **cada partição deve ter pelo menos alguns arquivos de 128 MB ou mais**. Conhecendo o volume diário de dados, você consegue calcular qual granularidade é adequada.

**Referência do livro (Cap. 8 e 10)**

O Cap. 8 cobre o padrão *Partitioned Table* com discussão explícita do trade-off entre granularidade e overhead. O Cap. 10 (Data Observability) menciona a importância de monitorar o tamanho de partições e o número de arquivos como métricas operacionais fundamentais de um data lake.

### 4.9 A stack do laboratório: MinIO, Hive Metastore, Trino e Airflow

Esta seção explica o papel de cada componente antes do laboratório prático.

**MinIO — Object Storage S3-compatible**

O MinIO é um servidor de object storage de código aberto que implementa a API do Amazon S3. Ele funciona idêntico ao S3 para qualquer cliente que usa o SDK ou API do S3. Para fins de laboratório e desenvolvimento, é indistinguível do S3 real.

Nesta sessão, o MinIO tem três buckets:

- `bronze`: dados brutos, particionados por data.
- `silver`: dados curados e transformados.
- `gold`: dados agregados para consumo analítico.

**Hive Metastore — Catálogo de tabelas**

O Hive Metastore armazena metadados de tabelas: nome, schema (colunas e tipos), localização no S3, colunas de partição, lista de partições existentes e estatísticas. Ele usa um banco relacional como backend — neste lab, PostgreSQL. Em produção na AWS, o serviço equivalente é o AWS Glue Data Catalog.

A comunicação entre o Trino e o Hive Metastore é via protocolo Thrift na porta 9083.

**Trino — Engine de consulta SQL**

O Trino é um engine de consulta SQL distribuído, desenhado para consultas analíticas de alta performance sobre dados em object storage. Ele não armazena dados: apenas os lê e processa.

O Trino se conecta ao Hive Metastore via conector Hive e ao MinIO via protocolo S3 (com endpoint override apontando para o MinIO local).

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

O Airflow orquestra a sequência das etapas:

- `generate_cdc` → gera eventos (ou captura CDC real)
- `load_bronze` → envia arquivos para o MinIO (bronze)
- `build_silver` → cria ou atualiza tabela particionada
- `validate_queries` → roda queries de validação e EXPLAIN

### 4.10 Laboratório integrado: CDC → MinIO → Trino → particionamento

Esta seção conecta CDC, storage e consulta. Os comandos abaixo usam os dados sintéticos gerados pelo `cdc_generator` (pasta `data/generated/marketing/`).

**Conectar ao Trino via CLI**

```bash
docker exec -it mentoria-s04-trino trino
```

**Verificar o catálogo disponível**

```sql
SHOW CATALOGS;
```

Deve retornar pelo menos: `hive`.

---

**Lab 0: Carregar dados no MinIO (bronze)**

```bash
# Replace <data-path> with the path to the generated marketing data
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v <data-path>:/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events.csv local/bronze/marketing/raw/events/

docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v <data-path>:/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events__cdc.csv local/bronze/marketing/raw/events_cdc/
```

---

**Lab 1: Criar schema e tabela bronze (raw)**

```sql
CREATE SCHEMA IF NOT EXISTS hive.marketing
WITH (location = 's3://bronze/marketing/');
```

```sql
-- CSV no Hive/Trino aceita apenas VARCHAR; tipos são aplicados na tabela silver via CAST
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

---

**Lab 2: Criar tabela silver particionada**

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

---

**Lab 3: Listar partições**

```sql
SELECT * FROM hive.marketing."events_silver$partitions";
```

---

**Lab 4: Query com partition pruning**

```sql
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10';
```

```sql
EXPLAIN
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10';
```

No plano retornado, procure por `Constraint` na linha do `TableScan`. Deve mostrar `event_date IN (2025-01-10)` — confirmando que o engine só vai ler aquela partição.

---

**Lab 5: Query sem partition pruning (full scan)**

```sql
EXPLAIN
SELECT event_id, user_id, campaign_id, channel
FROM hive.marketing.events_silver
WHERE channel = 'organic';
```

A linha do `TableScan` não terá `Constraint` de partição — confirmando que o engine lê todas as partições para aplicar o filtro de `channel` dentro dos arquivos.

---

**Lab 6 (opcional): CDC aplicado — última versão por event_id**

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

### 4.11 Análise do domínio de marketing

Com a tabela de eventos criada no lab, é possível fazer as perguntas típicas de um analista de marketing e observar o impacto do particionamento.

**Agregação diária de cliques por campanha**

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

**Usuários únicos por campanha**

```sql
SELECT
    campaign_id,
    COUNT(DISTINCT user_id) AS unique_users
FROM hive.marketing.events_silver
WHERE event_date = DATE '2025-01-10'
GROUP BY campaign_id;
```

**Ponto de aprendizado:** todas essas queries são naturalmente filtradas por data. Esse é o padrão dominante no domínio de analytics: "me dá os dados do dia X, da semana Y, do mês Z". Por isso, particionar por data é a decisão padrão e correta para tabelas de eventos.

**Quando particionar por campanha em vez de data?**

Se as queries mais comuns fossem "me dá todos os eventos da campanha A desde o início dos tempos", particionar por `campaign_id` faria mais sentido. Mas esse padrão é menos comum porque campanhas têm ciclos de vida curtos — a maioria das análises ainda usa janelas de tempo. A decisão final deve vir dos padrões de acesso reais, não de suposições.

### 4.12 Exercícios e entregáveis

**Exercício 1: Mapa do pipeline + contrato mínimo**

Objetivo: conectar as caixinhas do Projeto 1.

Entregável: diagrama com origem, CDC, bronze, silver, gold e consumo; onde entra o Airflow (orquestração); contratos básicos (granularidade e chaves).

---

**Exercício 2: Modelagem mínima**

Objetivo: definir o grão e as chaves de cada entidade.

Entregável: tabela com entidade, grão, chave principal e tipo de mudança (append/upsert).

---

**Exercício 3: Plano de particionamento**

Contexto: você está projetando as camadas bronze e silver para o Projeto 1.

| Tabela | Volume estimado | Padrões de query mais comuns |
|---|---|---|
| `events` | 10 M registros/dia | Por data, por campanha, por stage |
| `campaigns` | 500 registros/mês | Por data de criação, por status |
| `costs` | 1.000 registros/dia | Por data, por campanha |
| `crm` | 200 K registros total, com atualizações diárias | Por segmento, por data de última atualização |

Entregável: proposta de particionamento para cada tabela com chave de partição escolhida, justificativa, granularidade e riscos identificados (skew, small files, hot partitions).

---

**Exercício 4: Análise de custo**

Contexto: a tabela `events` tem 2 anos de histórico (730 dias) e 10 M registros por dia, totalizando 7,3 bilhões de registros. Cada registro ocupa 200 bytes em Parquet, totalizando 1,46 TB.

Cenário A — Sem partição:
- Uma query que filtra os últimos 7 dias varre todos os 1,46 TB.
- Custo estimado no Athena: 1,46 TB × $5/TB = $7,30 por query.

Cenário B — Particionado por dia:
- A mesma query lê apenas 7 partições de 730.
- Volume lido: 7/730 × 1,46 TB ≈ 14 GB.
- Custo estimado no Athena: 14 GB × $5/TB = $0,07 por query.

Entregável: tabela comparativa de custo para as tabelas do Exercício 3, usando os volumes estimados e o modelo de precificação do Athena ($5/TB). Calcule o custo mensal assumindo 100 queries/dia para cada tabela nos dois cenários.

---

**Exercício 5: Mini ADR de estratégia de partição**

Entregável: ADR com título, status, contexto, decisão, alternativas consideradas (ao menos 2) e consequências.

---

## Capítulo 5 — Sessão 05: Fontes, Arquitetura e Contratos de Dados

> Pré-requisito: Capítulos 1 a 4 — as perguntas de negócio da Sessão 01 agora são mapeadas para fontes reais, com as ferramentas e conceitos das Sessões 02 a 04 como base.

### 5.1 Perguntas de negócio por stakeholder

A arquitetura não começa pelo diagrama. Começa pelas perguntas que o negócio precisa responder.

**CEO / Diretoria**

- "Qual campanha está gerando mais receita este mês?"
- "Quanto estamos gastando por real faturado em cada canal?"
- "Quantos novos clientes adquirimos esta semana versus a semana passada?"

**Time de Growth / Marketing**

- "Qual é a taxa de conversão do funil por campanha e por canal?"
- "Em qual etapa estamos perdendo mais usuários?"
- "Qual canal tem menor CAC (custo de aquisição de cliente)?"

**Time de Operações**

- "Há alguma queda anômala no volume de checkouts hoje?"
- "Quais usuários estão em risco de churn esta semana?"

**Time de Analytics / BI**

- "Como está a evolução do ROI mês a mês por canal?"
- "Qual é o perfil dos usuários que chegam ao purchase por campanha?"

**Tabela: pergunta → fontes necessárias**

| Pergunta | Stakeholder | Fontes necessárias |
|---|---|---|
| ROI por campanha | CEO / Analytics | `costs` (API) + `events` (Kafka) + `campaigns` (CDC) |
| Taxa de conversão do funil | Growth | `events` (Kafka) |
| Novos clientes por semana | CEO | `users` (CDC) |
| Risco de churn | Operações | `crm` (CDC) + `events` (Kafka) |
| CAC por canal | Growth | `costs` (API) + `users` (CDC) + `events` (Kafka) |
| Queda de checkouts hoje | Operações | `events` (Kafka) — requer baixa latência |
| Perfil de usuários que convertem | Analytics | `users` (CDC) + `events` (Kafka) + `campaigns` (CDC) |

**Ponto central:** nenhuma dessas perguntas é respondível com uma fonte só. A motivação da arquitetura é exatamente essa: integrar fontes heterogêneas com contratos claros.

### 5.2 Modelo de dados — as cinco entidades

**users — Fonte: PostgreSQL (CDC)**

| Campo | Tipo | Descrição |
|---|---|---|
| `user_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome do usuário |
| `email` | VARCHAR | E-mail |
| `segment` | VARCHAR | Segmento (ex: premium, free) |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**campaigns — Fonte: PostgreSQL (CDC)**

| Campo | Tipo | Descrição |
|---|---|---|
| `campaign_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome da campanha |
| `channel` | VARCHAR | Canal (google, meta, tiktok) |
| `start_date` | DATE | Data de início |
| `end_date` | DATE | Data de término |
| `status` | VARCHAR | Status (active, paused, ended) |
| `updated_at` | TIMESTAMP | Última atualização |

**events — Fonte: Kafka (streaming)**

| Campo | Tipo | Descrição |
|---|---|---|
| `event_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `event_type` | VARCHAR | Tipo: visit, signup, checkout, purchase |
| `occurred_at` | TIMESTAMP | Momento do evento |

**costs — Fonte: API externa de mídia (batch)**

| Campo | Tipo | Descrição |
|---|---|---|
| `cost_id` | UUID | Chave primária |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `date` | DATE | Data de referência do custo |
| `channel` | VARCHAR | Canal de mídia |
| `amount` | DECIMAL | Valor investido |
| `currency` | VARCHAR | Moeda (BRL, USD) |

**crm — Fonte: PostgreSQL (CDC)**

| Campo | Tipo | Descrição |
|---|---|---|
| `crm_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `lifecycle_stage` | VARCHAR | Estágio: lead, active, at_risk, churned |
| `churn_risk_score` | FLOAT | Score de risco de churn (0 a 1) |
| `last_contact_at` | TIMESTAMP | Último contato registrado |
| `updated_at` | TIMESTAMP | Última atualização |

**Diagrama de relações**

```
users (user_id)
    |
    |--- events (user_id, campaign_id)
    |--- crm (user_id)

campaigns (campaign_id)
    |
    |--- events (campaign_id)
    |--- costs (campaign_id)
```

Tecido conectivo:
- `user_id` une: `users` ↔ `events` ↔ `crm`
- `campaign_id` une: `campaigns` ↔ `costs` ↔ `events`

`events` é a entidade central: conecta usuários, campanhas e o funil de conversão em um único lugar.

### 5.3 Natureza das fontes

**PostgreSQL → CDC**

Tabelas afetadas: `users`, `campaigns`, `crm`

Essas entidades são master data que mudam ao longo do dia. Um usuário pode mudar de segmento, uma campanha pode mudar de status, um score de churn pode ser atualizado múltiplas vezes.

Com batch diário, você captura apenas o estado final do dia — perde o histórico de alterações. Com CDC (ver Capítulo 3), você captura cada alteração com timestamp e tipo de operação (INSERT, UPDATE, DELETE). Isso permite:

- Reconstruir o estado de um registro em qualquer ponto do tempo.
- Detectar anomalias (ex: campanha que mudou de status três vezes em uma hora).
- Alimentar pipelines downstream com dados frescos sem esperar o batch noturno.

Frequência esperada: alterações contínuas ao longo do dia.
SLA no Bronze: dados disponíveis em até 30 minutos após alteração.

**API externa de mídia → Batch**

Tabela afetada: `costs`

Os custos de campanha em APIs de mídia são imutáveis por data — o custo do dia 10 é um snapshot do que foi gasto naquele dia. Não há alterações de registro a rastrear. A API expõe um endpoint por data e você extrai o que aconteceu.

Além disso, APIs de mídia têm rate limits e custos de chamada. Uma extração contínua seria ineficiente e cara sem ganho real — o dado muda uma vez por dia, no máximo.

Frequência esperada: uma extração por dia.
SLA no Bronze: dados do dia anterior disponíveis até às 8h.

**Kafka → Streaming**

Tabela afetada: `events`

Eventos de funil têm valor na latência. Detectar uma queda no volume de checkouts às 14h, em tempo quase real, é uma informação acionável — você pode investigar e corrigir o problema antes que o impacto seja maior.

Além disso, eventos têm natureza append-only: cada evento é imutável após ocorrer. Não há UPDATE nem DELETE — só INSERT. Isso torna o streaming uma abordagem natural: cada evento publicado no Kafka é consumido e gravado no Bronze sem complexidade de merge.

Importante: Kafka é implementado em sessão futura. Nesta sessão, o contrato é projetado e o slot na arquitetura é reservado. A implementação não existe ainda.

Frequência esperada: contínua, por evento.
SLA no Bronze: latência máxima de 5 minutos do evento ao Bronze.

### 5.4 Ferramentas de ingestão — categorias e exemplos

O objetivo desta seção não é escolher a ferramenta — é abrir o mapa de opções. A escolha deve acontecer depois de avaliar critérios de make vs buy (seção 5.5) para cada contexto.

**CDC**

| Ferramenta | Tipo | Observação |
|---|---|---|
| Debezium | OSS, connector Kafka | Padrão de mercado para CDC em PostgreSQL/MySQL. Requer Kafka. |
| Airbyte | OSS/Cloud, plataforma | Tem conector CDC via log replication. Mais fácil de operar. |
| Fivetran | SaaS | Gerenciado, fácil de configurar, mas tem custo por linha sincronizada. |
| AWS DMS | Cloud (AWS) | Gerenciado pela AWS, bom para ambientes já na AWS. |
| Kafka Connect (JDBC) | OSS | Polling via JDBC, não é CDC puro — não captura DELETEs. |

**API batch**

| Ferramenta | Tipo | Observação |
|---|---|---|
| Airbyte | OSS/Cloud, plataforma | Tem conectores prontos para Google Ads, Meta Ads, etc. |
| Fivetran | SaaS | Conectores prontos e gerenciados. Custo por linha. |
| Meltano | OSS | Baseado em Singer. Flexível, mas exige mais configuração. |
| Singer | OSS, protocolo | Base do Meltano/Airbyte. Taps e targets customizáveis. |
| Script Python custom | Custom | Máximo controle, máximo custo de manutenção. |

**Streaming / Kafka**

| Ferramenta | Tipo | Observação |
|---|---|---|
| Kafka Connect | OSS | Conectores para sources e sinks. Ecossistema amplo. |
| Confluent Platform | Cloud/Enterprise | Kafka gerenciado com operações simplificadas. |
| Flink | OSS | Processamento stateful, janelas, joins em streaming. |
| Spark Structured Streaming | OSS | Bom para times com histórico em Spark. |

### 5.5 Make vs buy — critérios para um time pequeno

Para cada fonte, a decisão não é "qual é a ferramenta mais poderosa?" — é "qual é a ferramenta que sustentamos com o time que temos?"

**Critérios de avaliação**

| Critério | Favorece ferramenta pronta | Favorece script custom |
|---|---|---|
| Número de fontes | Muitas fontes | Poucas fontes muito específicas |
| Frequência de mudança do contrato da fonte | Alta (API instável) | Baixa (contrato estável) |
| Disponibilidade de manutenção | Time pequeno, sem plantão | Time com capacidade de manter |
| Custo de licença aceitável | Sim | Não — budget restrito |
| Conector pronto disponível | Sim | Não existe conector adequado |
| Complexidade de lógica custom | Baixa | Alta — regras de negócio embutidas |

**Ponto de atenção**

Ferramentas prontas reduzem custo de engenharia inicial, mas introduzem dependência de vendor e custo de licença recorrente. Scripts custom têm custo de manutenção invisível — quem mantém quando o engenheiro que escreveu sai da empresa?

Para um time em fase de crescimento, a pergunta mais honesta é: "quem vai manter isso às 2h da manhã quando quebrar?"

### 5.6 Contratos de dados v0

Para cada fonte, os atributos do contrato definem o que o pipeline entrega e com quais garantias. Abaixo estão os contratos v0 do Projeto 1.

**PostgreSQL CDC — `users`, `campaigns`, `crm`**

| Atributo | Valor |
|---|---|
| Schema | Conforme seção 5.2 |
| Formato de destino | JSONL no Bronze; Parquet no Silver |
| Partição | Por data de ingestão no Bronze; por `updated_at` no Silver |
| SLA | Dados disponíveis em até 30 minutos após alteração na origem |
| Histórico | Mínimo 90 dias de eventos CDC no Bronze |

**API de mídia — `costs`**

| Atributo | Valor |
|---|---|
| Schema | Conforme seção 5.2 |
| Formato de destino | CSV ou JSONL no Bronze; Parquet no Silver |
| Partição | Por `date` (data de referência do custo) |
| SLA | Dados do dia anterior disponíveis até às 8h |
| Histórico | Mínimo 2 anos de histórico |

**Kafka — `events` (contrato projetado — implementação futura)**

| Atributo | Valor |
|---|---|
| Schema | Conforme seção 5.2 |
| Tópico | `marketing.events` |
| Formato de destino | JSONL no Bronze (append-only); Parquet no Silver |
| Partição | Por `event_date` |
| SLA | Latência máxima de 5 minutos do evento ao Bronze |
| Histórico | Mínimo 1 ano no Silver |

### 5.7 Exercícios e entregáveis

**Exercício 1 — Mapeamento de perguntas para fontes**

Objetivo: praticar o raciocínio de tracing reverso — partir de uma pergunta de negócio e identificar quais entidades e fontes são necessárias para respondê-la.

Instrução: escolha três perguntas da seção 5.1 (uma de stakeholders diferentes). Para cada pergunta, preencha:

- **Pergunta**: copie a pergunta exatamente como está na seção 5.1.
- **Entidades necessárias**: liste as tabelas do domínio cujos campos são necessários.
- **Fontes de ingestão**: CDC, API batch ou Kafka.
- **Chave de conexão utilizada**: `user_id`, `campaign_id` ou nenhuma.

| Pergunta (seção 5.1) | Entidades necessárias | Fontes de ingestão | Chave de conexão |
|---|---|---|---|
| | | | |

Exemplo resolvido (não usar como resposta):

| Pergunta | Entidades necessárias | Fontes de ingestão | Chave de conexão |
|---|---|---|---|
| "Qual canal tem menor CAC?" | `costs`, `users`, `events` | API batch + CDC + Kafka | `campaign_id` (costs↔events) e `user_id` (users↔events) |

Critério de aceite: para cada linha, o caminho fonte → entidade → pergunta deve ser traçável sem gaps.

---

**Exercício 2 — Architecture canvas v0**

Objetivo: desenhar a arquitetura completa do Projeto 1 em um diagrama.

Passos:

1. **Fontes:** listar as três fontes (PostgreSQL, API de mídia, Kafka) com a natureza de cada uma (CDC, batch, streaming).
2. **Camada de ingestão:** para cada fonte, marcar o slot da ferramenta com `[?]` — a escolha da ferramenta é aberta para análise posterior.
3. **Camadas de armazenamento:** desenhar Bronze → Silver → Gold. Para cada camada, anotar: Bronze (raw, imutável, particionado por data de ingestão), Silver (deduplicado, joins aplicados, schema confiável), Gold (datasets de negócio, prontos para responder as perguntas da seção 5.1).
4. **Consumo:** listar os consumidores (BI/dashboards, analytics ad-hoc, ativações). Conectar ao Gold.
5. **Validação:** percorrer o canvas de trás para frente — pegar uma pergunta da seção 5.1 e traçar o caminho até a fonte. Se o caminho existir e estiver completo, o canvas está correto para essa pergunta.

Entregável: diagrama do canvas (pode ser desenhado no papel, Miro ou Lucidchart) com os cinco elementos acima.

---

**Exercício 3 — Proposta de ferramentas por tipo de ingestão**

Objetivo: definir a escolha de ferramenta para cada tipo de ingestão com justificativa.

| Tipo de ingestão | Ferramenta proposta | Justificativa (custo, complexidade, manutenção) |
|---|---|---|
| CDC (PostgreSQL) | | |
| API de mídia (batch) | | |
| Streaming (Kafka) | | |

Critério de aceite: para cada linha, a justificativa deve referenciar ao menos um critério da tabela de make vs buy da seção 5.5.

### 5.8 O que deliberadamente não decidir agora

Para evitar paralisia por análise:

- Não fechar a escolha de ferramenta de ingestão para nenhuma das fontes antes de completar o Exercício 3.
- Não detalhar os jobs individuais de cada pipeline — isso é escopo das sessões seguintes.
- Não discutir sizing de infraestrutura, tuning ou benchmarks.
- Não modelar as tabelas Silver e Gold em detalhes — isso é Sessão 06 em diante.
- Não buscar perfeição no canvas v0 — ele vai evoluir. O objetivo é ter um ponto de partida validado.
- Não implementar nada. Nenhum comando é executado nesta sessão.

---

## Referências

**Livro de referência da trilha**

Data Engineering Design Patterns (2025):
- Cap. 4: Idempotency Design Patterns — Overwriting, Merger, Stateful Merger
- Cap. 6: Data Flow Design Patterns — Local Sequencer, Isolated Sequencer, Fan-In, Fan-Out
- Cap. 8: Data Storage Design Patterns — Horizontal Partitioner, Partitioned Table, Compactor
- Cap. 9: Data Quality Design Patterns — AWAP Pattern
- Cap. 10: Data Observability Design Patterns — Flow Interruption Detector

**Apache Airflow**

- Documentação oficial: https://airflow.apache.org/docs/
- Componentes do Airflow 3.x: https://airflow.apache.org/docs/apache-airflow/stable/architecture.html

**Formatos de arquivo e table formats**

- Apache Parquet: https://parquet.apache.org/
- Apache Iceberg: https://iceberg.apache.org/
- Delta Lake: https://delta.io/

**Trino e MinIO**

- Documentação do Trino (conector Hive): https://trino.io/docs/current/connector/hive.html
- Documentação do MinIO: https://min.io/docs/

**Change Data Capture**

- Debezium (CDC log-based): https://debezium.io/
- Airbyte (plataforma de ingestão): https://airbyte.com/
