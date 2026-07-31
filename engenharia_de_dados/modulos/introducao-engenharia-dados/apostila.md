---
title: "Apostila, Introducao a engenharia de dados e diagnostico"
date: 2026-07-30
type: apostila
status: draft
project: zambotto-mentoria
tags: [diagnostico, mentoria]
---

# Apostila, Introducao a engenharia de dados e diagnostico

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

## Sumario

- [1.1 O Projeto 1: startup de marketing/e-commerce](#11-o-projeto-1-startup-de-marketinge-commerce)
- [1.2 Ciclo de vida dos dados](#12-ciclo-de-vida-dos-dados)
- [1.3 O que é um data product](#13-o-que-é-um-data-product)
- [1.4 Métricas de negócio vs. métricas técnicas](#14-métricas-de-negócio-vs-métricas-técnicas)
- [1.5 Hipóteses mensuráveis e critérios de sucesso](#15-hipóteses-mensuráveis-e-critérios-de-sucesso)
- [1.6 Exemplos do domínio](#16-exemplos-do-domínio)
- [1.7 Exercícios e entregáveis](#17-exercícios-e-entregáveis)

## Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.


> Este capítulo estabelece o contexto do Projeto 1 e os conceitos fundamentais que servem de base para todos os capítulos seguintes.

## 1.1 O Projeto 1: startup de marketing/e-commerce

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

## 1.2 Ciclo de vida dos dados

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
    [Bronze, raw]
         |
   [Silver, curado]
         |
    [Gold, métricas]
         |
    [BI / Análise]
```

Essa sequência, construída ao longo de toda a trilha, é o que conecta uma pergunta do CEO ("qual campanha gerou mais ROI?") a um registro em um banco de dados de origem.

## 1.3 O que é um data product

Um data product é qualquer ativo de dados construído com a intenção de ser consumido por um usuário, interno ou externo, para tomar decisões. Não é apenas um dataset, é um serviço com garantias.

**Quatro atributos de um data product de qualidade**

**Utilidade:** o data product resolve um problema real de negócio. Uma tabela de eventos que ninguém usa não é um data product, é um dado sem destinatário. O dado só tem valor quando existe uma pergunta para responder.

Para o Projeto 1, um exemplo de data product com utilidade clara: uma tabela gold com ROI diário por campanha, consumida pelo time de marketing toda manhã para ajustar o budget de anúncios do dia.

**Confiabilidade:** o consumidor pode confiar no dado. Isso inclui ausência de duplicatas, valores dentro dos intervalos esperados, chaves primárias sem nulos e cobertura temporal completa. Um dado que "parece certo" mas que o consumidor não pode verificar não é confiável, é uma suposição.

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

## 1.4 Métricas de negócio vs. métricas técnicas

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

## 1.5 Hipóteses mensuráveis e critérios de sucesso

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

## 1.6 Exemplos do domínio

Esta seção apresenta exemplos concretos com dados sintéticos do domínio de marketing. Esses dados são gerados pelo módulo `cdc_generator` e servem como base para os laboratórios das sessões seguintes.

**Métrica de conversão por campanha**

Uma tabela básica de desempenho de campanha teria esta estrutura:

| campaign_id | visitas | compras | taxa_conversão | custo (R$) | receita (R$) | ROI |
|---|---|---|---|---|---|---|
| camp_001 | 450 | 6 | 1,33% | 2.000 | 480 | −0,76 |
| camp_002 | 456 | 15 | 3,29% | 2.000 | 1.125 | −0,44 |

`camp_002` tem taxa de conversão mais de duas vezes maior que `camp_001`, mas ambas têm ROI negativo, o custo de aquisição ainda supera a receita gerada. A hipótese de negócio seria: "qual ajuste nas campanhas levaria o ROI para positivo primeiro?"

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

Usuários do segmento `free` têm taxa de risco quatro vezes maior. Isso pode justificar campanhas de retenção direcionadas, e o pipeline de dados é o que torna esse tipo de análise possível e repetível.

## 1.7 Exercícios e entregáveis

**Exercício 1, Metas SMART**

Objetivo: traduzir objetivos de negócio genéricos em hipóteses verificáveis com dados.

Para cada um dos três objetivos abaixo, reescreva no formato SMART indicando a métrica, o valor-alvo, o prazo e qual tabela do domínio seria usada para medir:

1. "Quero aumentar a receita das campanhas."
2. "Quero diminuir o custo por clique."
3. "Quero melhorar a retenção dos usuários premium."

Entregável: três hipóteses no formato SMART com referência às entidades do Projeto 1.

---

**Exercício 2, Mapa de perguntas de negócio**

Objetivo: praticar o raciocínio que conecta perguntas de stakeholders a fontes de dados.

Construa uma tabela com 10 perguntas de negócio do domínio de marketing/e-commerce. Use as perguntas da seção 5.1 (Capítulo 5) como ponto de partida. Para cada pergunta, identifique:

- Qual stakeholder faria essa pergunta.
- Quais entidades do domínio são necessárias para respondê-la.
- Qual é a frequência de atualização necessária (tempo real, diário, semanal).

Entregável: tabela com 10 perguntas priorizadas, stakeholder, entidades e frequência.

---

**Exercício 3, Inventário inicial de fontes**

Objetivo: mapear as fontes de dados necessárias para o Projeto 1.

Construa uma tabela com as cinco entidades do domínio. Para cada entidade, preencha:

- Tipo de fonte (banco relacional, API, sistema de eventos).
- Frequência de atualização esperada.
- Time dono dos dados na origem.
- Criticidade para as perguntas de negócio (alta, média, baixa).

Entregável: tabela de inventário de fontes com as colunas acima preenchidas.

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
