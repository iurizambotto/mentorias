---
title: "Apostila completa, Engenharia de Dados"
date: 2026-07-31
type: apostila
status: active
tags: [mentoria, apostila]
---

# Apostila completa, Engenharia de Dados

> Arquivo gerado a partir do `trilha.yml`. Nao edite a mao: rode `gerar_trilha.py` novamente, senao a edicao se perde e o documento diverge.

Cada capitulo abaixo e a apostila de um modulo, na ordem recomendada da
trilha. Para estudar um assunto isolado, va direto ao modulo.

## Sumario

- [Capitulo 1, Introducao a engenharia de dados e diagnostico](#capitulo-1-introducao-a-engenharia-de-dados-e-diagnostico)
- [Capitulo 2, SQL com foco em JOINs](#capitulo-2-sql-com-foco-em-joins)
- [Capitulo 3, Formatos de arquivo e tipos de tabela](#capitulo-3-formatos-de-arquivo-e-tipos-de-tabela)
- [Capitulo 4, Particionamento e performance de consultas](#capitulo-4-particionamento-e-performance-de-consultas)
- [Capitulo 5, Orquestracao com Apache Airflow](#capitulo-5-orquestracao-com-apache-airflow)
- [Capitulo 6, Fontes, arquitetura e contratos de dados](#capitulo-6-fontes-arquitetura-e-contratos-de-dados)
- [Capitulo 7, Change Data Capture](#capitulo-7-change-data-capture)
- [Capitulo 8, Transformacao com dbt](#capitulo-8-transformacao-com-dbt)
- [Capitulo 9, Cloud para dados](#capitulo-9-cloud-para-dados)
- [Capitulo 10, Infraestrutura como codigo](#capitulo-10-infraestrutura-como-codigo)
- [Capitulo 11, Streaming com Apache Kafka](#capitulo-11-streaming-com-apache-kafka)
- [Capitulo 12, Kubernetes para engenharia de dados](#capitulo-12-kubernetes-para-engenharia-de-dados)

---

## Capitulo 1, Introducao a engenharia de dados e diagnostico

Fonte: `modulos/introducao-engenharia-dados/apostila.md`

### Apostila, Introducao a engenharia de dados e diagnostico

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

#### Sumario

- [1.1 O Projeto 1: startup de marketing/e-commerce](#11-o-projeto-1-startup-de-marketinge-commerce)
- [1.2 Ciclo de vida dos dados](#12-ciclo-de-vida-dos-dados)
- [1.3 O que é um data product](#13-o-que-é-um-data-product)
- [1.4 Métricas de negócio vs. métricas técnicas](#14-métricas-de-negócio-vs-métricas-técnicas)
- [1.5 Hipóteses mensuráveis e critérios de sucesso](#15-hipóteses-mensuráveis-e-critérios-de-sucesso)
- [1.6 Exemplos do domínio](#16-exemplos-do-domínio)
- [1.7 Exercícios e entregáveis](#17-exercícios-e-entregáveis)

#### Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.


> Este capítulo estabelece o contexto do Projeto 1 e os conceitos fundamentais que servem de base para todos os capítulos seguintes.

#### 1.1 O Projeto 1: startup de marketing/e-commerce

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

#### 1.2 Ciclo de vida dos dados

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

#### 1.3 O que é um data product

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

#### 1.4 Métricas de negócio vs. métricas técnicas

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

#### 1.5 Hipóteses mensuráveis e critérios de sucesso

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

#### 1.6 Exemplos do domínio

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

#### 1.7 Exercícios e entregáveis

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


#### Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

#### Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

#### Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

#### Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

#### Glossario

Pendente. Listar os termos novos deste modulo.

#### Referencias

Pendente. Documentacao oficial com data de consulta.

#### Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.

---

## Capitulo 2, SQL com foco em JOINs

Fonte: `modulos/sql-joins/apostila.md`

### Apostila, SQL com foco em JOINs

> Base de leitura da sessão única de 60 minutos.
> Domínio de referência: CRM e marketing (clientes e pedidos).

---

#### Sumário

0. Como usar esta apostila
1. Objetivo pedagógico da sessão
2. Contexto de negócio: por que JOIN importa
3. Fundamentos relacionais que sustentam os JOINs
4. JOINs com leitura conceitual e diagrama de Venn
5. `ON` vs `WHERE` (ponto mais importante da sessão)
6. Setup e base de dados da prática
7. Roteiro de condução (60 minutos)
8. Exercícios guiados com gabarito comentado
9. Mini-desafio final com solução e interpretação
10. Rubrica de validação da aprendizagem
11. Erros comuns e como corrigir
12. Plano de continuidade pós-sessão
13. Glossário rápido
14. Referências

---

#### 0. Como usar esta apostila

Esta apostila foi escrita para servir como material principal de leitura da sessão.

Uso recomendado:

1. Ler as seções 1 a 5 antes da prática.
2. Executar as queries da seção 8 no editor SQL.
3. Tentar resolver o mini-desafio (seção 9) sem olhar a solução.
4. Voltar à seção 11 para revisar erros e anti-padrões.

Objetivo desta abordagem: transformar o conteúdo em repertório aplicável em cenário real, e não apenas em memorização de sintaxe.

---

#### 1. Objetivo pedagógico da sessão

Ao final da sessão, a mentorada deve conseguir:

1. diferenciar quando usar `INNER JOIN`, `LEFT JOIN` e `FULL OUTER JOIN`;
2. explicar por que a posição do filtro (`ON` ou `WHERE`) muda o resultado;
3. montar e interpretar consultas com `JOIN + filtro + agregação`;
4. justificar a escolha da query com base em pergunta de negócio.

Resultado esperado da sessão:

- segurança conceitual para leitura de bases relacionais;
- autonomia para resolver problemas iniciais de análise com SQL.

---

#### 2. Contexto de negócio: por que JOIN importa

No domínio de CRM e marketing, os dados quase nunca ficam em uma única tabela.

Exemplo realista:

- tabela `clientes`: quem são os clientes;
- tabela `pedidos`: histórico de compras.

Perguntas típicas:

- quais clientes compraram no período?
- quais clientes ainda não compraram?
- qual é o valor total de compras por cliente?

Sem JOIN, essas perguntas ficam incompletas ou exigem processamento manual.

Com JOIN bem aplicado, conseguimos combinar contexto de negócio com fatos transacionais em uma única leitura analítica.

---

#### 3. Fundamentos relacionais que sustentam os JOINs

#### 3.1 Grão da tabela (granularidade)

Grão = o que cada linha representa.

- `clientes`: 1 linha = 1 cliente.
- `pedidos`: 1 linha = 1 pedido.

Se o grão não estiver claro, a leitura de JOIN fica confusa e surgem erros de interpretação.

#### 3.2 Chave primária e chave estrangeira

- **Chave primária (PK)**: identifica unicamente uma linha.
  - Ex.: `clientes.cliente_id`.
- **Chave estrangeira (FK lógica)**: aponta para a PK de outra tabela.
  - Ex.: `pedidos.cliente_id` referencia `clientes.cliente_id`.

JOIN, na prática, é o vínculo entre essas chaves.

#### 3.3 Cardinalidade

Cardinalidade descreve como uma entidade se relaciona com outra:

- `1:1`, um para um;
- `1:N`, um para muitos;
- `N:N`, muitos para muitos (geralmente exige tabela ponte).

No nosso caso:

- um cliente pode ter vários pedidos (`1:N`).

Consequência prática: um cliente pode aparecer várias vezes após o JOIN.

#### 3.4 Nulos, linhas faltantes e duplicidades

Três sinais para sempre observar no resultado:

1. **Nulos (`NULL`)**: indicam ausência de correspondência (muito comum em `LEFT JOIN`).
2. **Linhas faltantes**: geralmente JOIN muito restritivo ou filtro mal posicionado.
3. **Duplicidades aparentes**: muitas vezes são esperadas pela cardinalidade (ex.: um cliente com dois pedidos).

---

#### 4. JOINs com leitura conceitual e diagrama de Venn

Antes dos tipos de JOIN, definimos os conjuntos:

- **A** = conjunto de clientes (`clientes`).
- **B** = conjunto de clientes que aparecem em pedidos (`pedidos`, projetado por `cliente_id`).

Importante: diagrama de Venn ajuda na intuição de pertencimento de conjunto, mas não mostra multiplicidade de linhas.

##### 4.1 `INNER JOIN` (interseção)

Retorna apenas o que existe em A e em B ao mesmo tempo.

Leitura em conjuntos:

- `INNER JOIN = A ∩ B`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /         \          /         \
    /     A     \________/     B     \
    \           /########\           /
     \_________/##########\_________/

Área hachurada (########) = resultado do INNER JOIN
```

Quando usar:

- quando você quer apenas registros com correspondência nos dois lados.

##### 4.2 `LEFT JOIN` (preserva esquerda)

Retorna tudo de A e, quando houver, dados de B.

Leitura em conjuntos:

- `LEFT JOIN = A`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /         \
    /###########\________/     B     \
    \###########/########\           /
     \#########/##########\_________/

Área hachurada = todo o conjunto A
```

Quando usar:

- quando cobertura da base da esquerda é requisito de negócio.

##### 4.3 `FULL OUTER JOIN` (união completa)

Retorna tudo de A e tudo de B.

Leitura em conjuntos:

- `FULL OUTER JOIN = A ∪ B`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /#########\
    /###########\________/###########\
    \###########/########\###########/
     \#########/##########\#########/

Área hachurada = A inteiro + B inteiro
```

Quando usar:

- auditoria de cobertura;
- reconciliação entre duas bases.

Observação prática:

- em alguns engines, `FULL OUTER JOIN` pode ter limitações ou não ser suportado.

##### 4.4 Comparativo rápido

| Tipo de JOIN | Regra | Melhor uso |
|---|---|---|
| `INNER JOIN` | Apenas correspondência em ambos | Análise de interseção |
| `LEFT JOIN` | Preserva esquerda | Cobertura de base principal |
| `FULL OUTER JOIN` | Preserva ambos | Reconciliação/auditoria |

---

#### 5. `ON` vs `WHERE` (ponto mais importante da sessão)

Regra prática:

- `ON` controla como as tabelas se conectam.
- `WHERE` filtra o resultado depois da conexão.

Em `LEFT JOIN`, essa diferença muda o significado da consulta.

##### 5.1 Caso correto para preservar todos os clientes

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Interpretação:

- mantém todos os clientes;
- limita apenas os pedidos considerados na agregação.

##### 5.2 Caso que quebra cobertura sem perceber

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Interpretação:

- remove clientes sem pedido no período;
- na prática, comporta-se como `INNER JOIN` para essa condição.

Mensagem-chave da sessão:

> Se a intenção é manter todos os clientes, filtros da tabela da direita devem ir no `ON` (quando aplicável ao relacionamento).

---

#### 6. Setup e base de dados da prática

Ferramentas sugeridas:

- SQLBolt: https://sqlbolt.com/
- DB Fiddle (PostgreSQL): https://www.db-fiddle.com/
- W3Schools SQL Tryit (contingência): https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all

Script base (copiar e executar):

```sql
CREATE TABLE clientes (
    cliente_id INT PRIMARY KEY,
    nome TEXT,
    segmento TEXT
);

CREATE TABLE pedidos (
    pedido_id INT PRIMARY KEY,
    cliente_id INT,
    data_pedido DATE,
    valor NUMERIC(10,2)
);

INSERT INTO clientes (cliente_id, nome, segmento) VALUES
(1, 'Ana', 'vip'),
(2, 'Bruno', 'regular'),
(3, 'Carla', 'vip'),
(4, 'Diego', 'novo');

INSERT INTO pedidos (pedido_id, cliente_id, data_pedido, valor) VALUES
(101, 1, '2026-03-01', 120.00),
(102, 1, '2026-03-10', 80.00),
(103, 2, '2026-03-08', 50.00),
(104, 3, '2026-03-15', 200.00);
```

Leitura rápida da base:

- 4 clientes;
- 4 pedidos;
- 1 cliente sem pedido (caso didático para `LEFT JOIN`).

---

#### 7. Roteiro de condução (60 minutos)

##### Bloco 1 (0,10 min), Aquecimento

- revisão rápida de `SELECT`, `WHERE`, `GROUP BY`;
- confirmação de PK/FK e grão das tabelas;
- alinhamento de objetivo da sessão.

##### Bloco 2 (10,25 min), Conceito de JOINs

- `INNER JOIN`, `LEFT JOIN`, `FULL OUTER JOIN`;
- leitura dos diagramas de Venn;
- explicação de `ON` vs `WHERE` com exemplo comparativo.

##### Bloco 3 (25,45 min), Prática guiada

Distribuição sugerida:

- 25,32 min: exercício 1 (`INNER JOIN`);
- 32,39 min: exercício 2 (`LEFT JOIN`);
- 39,45 min: exercício 3 (`JOIN + GROUP BY`).

##### Bloco 4 (45,55 min), Mini-desafio

- resolver query final com período e agregação;
- interpretar resultado (nulos, cobertura da base e ordenação).

##### Bloco 5 (55,60 min), Fechamento

- registrar 3 aprendizados;
- registrar 1 dúvida pendente;
- validar se o objetivo da sessão foi atingido.

---

#### 8. Exercícios guiados com gabarito comentado

##### Exercício 1, `INNER JOIN` básico

Enunciado:

> Listar cliente, pedido e valor para quem comprou.

```sql
SELECT
    c.cliente_id,
    c.nome,
    p.pedido_id,
    p.valor
FROM clientes c
INNER JOIN pedidos p
    ON c.cliente_id = p.cliente_id
ORDER BY c.cliente_id, p.pedido_id;
```

Resultado esperado:

| cliente_id | nome | pedido_id | valor |
|---:|---|---:|---:|
| 1 | Ana | 101 | 120.00 |
| 1 | Ana | 102 | 80.00 |
| 2 | Bruno | 103 | 50.00 |
| 3 | Carla | 104 | 200.00 |

Leitura didática:

- Diego não aparece porque não possui pedido.

##### Exercício 2, `LEFT JOIN` para cobertura da base

Enunciado:

> Listar todos os clientes e identificar quem não comprou.

```sql
SELECT
    c.cliente_id,
    c.nome,
    p.pedido_id
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
ORDER BY c.cliente_id, p.pedido_id;
```

Resultado esperado:

| cliente_id | nome | pedido_id |
|---:|---|---:|
| 1 | Ana | 101 |
| 1 | Ana | 102 |
| 2 | Bruno | 103 |
| 3 | Carla | 104 |
| 4 | Diego | `NULL` |

Agora, apenas clientes sem pedido:

```sql
SELECT
    c.cliente_id,
    c.nome
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.pedido_id IS NULL;
```

Resultado esperado:

| cliente_id | nome |
|---:|---|
| 4 | Diego |

##### Exercício 3, `JOIN + GROUP BY` (resumo analítico)

Enunciado:

> Calcular total financeiro e quantidade de pedidos por cliente.

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_total,
    COUNT(p.pedido_id) AS total_pedidos
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total DESC, c.cliente_id;
```

Resultado esperado:

| cliente_id | nome | valor_total | total_pedidos |
|---:|---|---:|---:|
| 1 | Ana | 200.00 | 2 |
| 3 | Carla | 200.00 | 1 |
| 2 | Bruno | 50.00 | 1 |
| 4 | Diego | 0.00 | 0 |

Leitura didática:

- `COALESCE` evita total nulo para clientes sem pedido;
- `COUNT(p.pedido_id)` conta apenas linhas com pedido válido.

---

#### 9. Mini-desafio final com solução e interpretação

##### Enunciado

Monte uma query que traga todos os clientes com total de compras apenas no período de `2026-03-01` a `2026-03-10`, incluindo clientes sem compras no período. Ordene por maior valor total.

##### Dicas antes do gabarito

1. Comece de `clientes`.
2. Use `LEFT JOIN` para preservar cobertura.
3. Posicione o filtro de período no `ON`.
4. Agregue com `SUM` e trate nulos com `COALESCE`.

##### Gabarito

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_total_periodo,
    COUNT(p.pedido_id) AS qtd_pedidos_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total_periodo DESC, c.cliente_id;
```

Resultado esperado:

| cliente_id | nome | valor_total_periodo | qtd_pedidos_periodo |
|---:|---|---:|---:|
| 1 | Ana | 200.00 | 2 |
| 2 | Bruno | 50.00 | 1 |
| 3 | Carla | 0.00 | 0 |
| 4 | Diego | 0.00 | 0 |

Interpretação:

- Carla tem pedido fora do período e, por isso, fica com 0 no recorte;
- Diego segue aparecendo por causa do `LEFT JOIN`.

---

#### 10. Rubrica de validação da aprendizagem

Considere a sessão bem-sucedida quando a mentorada:

- explica a diferença entre `INNER` e `LEFT` com exemplo próprio;
- identifica por que linhas “somem” em um JOIN;
- evita o erro clássico de filtro no `WHERE` após `LEFT JOIN`;
- entrega mini-desafio com leitura correta do resultado;
- comunica a lógica da query com linguagem de negócio.

Checklist rápido:

- [ ] Entendeu PK/FK e grão das tabelas.
- [ ] Diferenciou `INNER`, `LEFT` e `FULL OUTER`.
- [ ] Demonstrou domínio de `ON` vs `WHERE`.
- [ ] Construiu query final sem ajuda total.

---

#### 11. Erros comuns e como corrigir

1. **Esquecer condição de JOIN (`ON`)**
   - Sintoma: explosão de linhas (produto cartesiano).
   - Correção: validar relacionamento por chave antes de executar.

2. **Aplicar filtro da tabela da direita no `WHERE` após `LEFT JOIN`**
   - Sintoma: perda de clientes sem correspondência.
   - Correção: mover o filtro para o `ON` quando a intenção for preservar a esquerda.

3. **Somar sem agrupar corretamente**
   - Sintoma: erro SQL de coluna não agregada.
   - Correção: incluir no `GROUP BY` todas as colunas não agregadas do `SELECT`.

4. **Não tratar `NULL` em saída analítica**
   - Sintoma: métricas em branco e leitura confusa.
   - Correção: usar `COALESCE` na apresentação do resultado.

5. **Interpretar duplicidade como erro sem checar cardinalidade**
   - Sintoma: suspeita falsa de dado duplicado.
   - Correção: confirmar se o relacionamento `1:N` explica múltiplas linhas.

---

#### 12. Plano de continuidade pós-sessão

Se houver necessidade de reforço:

1. repetir os exercícios com outra janela de datas;
2. adicionar uma terceira tabela simples (ex.: `campanhas`) para múltiplos JOINs;
3. montar lista curta de 10 queries progressivas (básico -> intermediário);
4. registrar dúvidas e decisões em `../../notes/`.

Próximo degrau natural da trilha:

- avançar para JOIN em mais de duas tabelas e introduzir CTE para legibilidade.

---

#### 13. Glossário rápido

- **PK (Primary Key)**: chave única da tabela.
- **FK (Foreign Key)**: chave que referencia outra tabela.
- **Cardinalidade**: padrão de relacionamento entre entidades.
- **JOIN**: operação de combinação de tabelas.
- **`NULL`**: ausência de valor.
- **Agregação**: resumo de dados com funções como `SUM`, `COUNT`, `AVG`.

---

#### 14. Referências

- SQLBolt: https://sqlbolt.com/
- DB Fiddle: https://www.db-fiddle.com/
- W3Schools SQL Tryit: https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all

Materiais locais da sessão:

- `sessao-01-sql-joins.md`
- `plano-aula.md`
- `checklist-execucao-ao-vivo.md`

---

## Capitulo 3, Formatos de arquivo e tipos de tabela

Fonte: `modulos/formatos-e-tipos-de-tabela/apostila.md`

### Apostila, Formatos de arquivo e tipos de tabela

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

#### Sumario

- [3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC](#33-formatos-de-arquivo-csv-jsonl-parquet-e-orc)
- [3.4 Tipos de tabela: Hive, Iceberg e Delta Lake](#34-tipos-de-tabela-hive-iceberg-e-delta-lake)
- [3.5 Camadas bronze, silver e gold](#35-camadas-bronze-silver-e-gold)
- [3.6 Exercícios e entregáveis](#36-exercícios-e-entregáveis)

#### Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

#### 3.3 Formatos de arquivo: CSV, JSONL, Parquet e ORC

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

#### 3.4 Tipos de tabela: Hive, Iceberg e Delta Lake

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

#### 3.5 Camadas bronze, silver e gold

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

#### 3.6 Exercícios e entregáveis

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


#### Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

#### Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

#### Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

#### Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

#### Glossario

Pendente. Listar os termos novos deste modulo.

#### Referencias

Pendente. Documentacao oficial com data de consulta.

#### Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.

---

## Capitulo 4, Particionamento e performance de consultas

Fonte: `modulos/particionamento-performance/apostila.md`

### Apostila, Particionamento + integração do pipeline

> Estratégias de particionamento, partition pruning, skew e laboratório integrado com CDC, Trino, MinIO e Hive Metastore.
> Conduzida por Iuri Zambotto com Paulo Shindi.

---

#### Sumário

0. Visão integrada do Projeto 1 (as caixinhas)
0.1 Modelagem mínima antes do particionamento
1. Por que particionamento importa
2. Como o particionamento físico funciona
3. Partition pruning, o mecanismo central
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

#### 0. Visão integrada do Projeto 1 (as caixinhas)

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

#### 0.1 Modelagem mínima antes do particionamento

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

#### 1. Por que particionamento importa

Antes de falar sobre técnica, vale entender o problema que o particionamento resolve.

**O cenário sem particionamento**

Imagine uma tabela de eventos de uma plataforma de e-commerce com 5 bilhões de registros, cobrindo três anos de histórico. Você precisa calcular o total de cliques da última semana. Sem particionamento, a query precisa varrer todos os 5 bilhões de registros para encontrar os que caem na janela de tempo solicitada. Isso é um *full table scan*: caro, lento, e que cresce linearmente com o volume de dados.

Em sistemas como Athena (serviço gerenciado da AWS sobre o Presto/Trino), você paga por byte escaneado. Um full scan em 5 bilhões de registros pode custar dezenas de dólares por consulta. Multiplique isso por centenas de consultas por dia e o custo torna-se inviável.

**O que o particionamento faz**

Particionamento é a prática de organizar fisicamente os dados em subconjuntos (partições) com base nos valores de uma ou mais colunas. Quando o engine de consulta precisa responder a uma query com filtro sobre a coluna de partição, ele consulta apenas as partições relevantes, ignorando todo o resto.

No exemplo acima: se os eventos estão particionados por data, a query da última semana lê apenas 7 partições de 3 anos (mais de 1000 partições). Em vez de varrer 5 bilhões de registros, o engine lê apenas os da última semana, talvez 30 ou 40 milhões. A redução de custo e de latência é de uma ou duas ordens de magnitude.

**A decisão que mais impacta o custo do datalake**

Particionamento é, frequentemente, a decisão de design de dados com maior impacto direto em custo. Uma escolha errada de chave de partição pode:

- Fazer com que todas as queries continuem sendo full scans (partição com alta cardinalidade que nenhuma query usa como filtro).
- Gerar dezenas de milhares de arquivos minúsculos (small files), degradando o próprio mecanismo que deveria melhorar a performance.
- Criar desequilíbrio de tamanho entre partições (*skew*), onde uma partição tem 1000x mais dados que outra.

Esta sessão cobre essas decisões em detalhe, com laboratório prático.

**Referência do livro (Cap. 8, Data Storage Design Patterns)**

O capítulo 8 descreve o padrão *Partitioned Table* como fundamento de qualquer estratégia de storage em larga escala. A premissa é simples: o acesso aos dados deve ser O(1) em relação ao volume total sempre que possível. Particionar por uma coluna que é filtrada sistematicamente é a forma mais direta de atingir isso.

---

#### 2. Como o particionamento físico funciona

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

Um detalhe importante: a coluna de partição (`event_date`, neste exemplo) geralmente **não é armazenada dentro dos arquivos Parquet de cada partição**. Ela está codificada no próprio caminho do diretório. Isso economiza espaço e evita redundância, o valor `2026-01-10` não precisa aparecer em cada linha de um arquivo que já está dentro de `event_date=2026-01-10/`.

Quando o engine faz o merge dos dados com o metadado de partição ao retornar resultados, ele reconstrói a coluna automaticamente a partir do caminho.

---

#### 3. Partition pruning, o mecanismo central

**O que é partition pruning**

Partition pruning (ou partition elimination) é o mecanismo pelo qual o engine de consulta identifica, a partir dos filtros da query, quais partições precisam ser lidas e descarta todas as demais antes de tocar qualquer arquivo.

O nome "pruning" vem de "podar", como podar galhos desnecessários de uma árvore.

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

Um equívoco comum é achar que qualquer filtro ativa o pruning. Só a coluna de partição pode ativar o pruning. Filtros em outras colunas (`event_type`, `user_id`, `campaign_id`) não eliminam partições, eles aplicam filtros dentro dos arquivos já carregados.

Isso tem uma implicação prática importante: a coluna de partição deve ser aquela mais usada como filtro nas queries mais frequentes e mais caras do sistema.

**Pruning e Pushdown, conceitos relacionados**

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

#### 4. Estratégias de particionamento

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

#### 5. Cardinalidade e escolha de chave de partição

**O que é cardinalidade**

Cardinalidade é o número de valores distintos de uma coluna. Alta cardinalidade significa muitos valores distintos (ex: `user_id` com milhões de usuários). Baixa cardinalidade significa poucos valores (ex: `country` com 10 países, `event_type` com 5 tipos).

**Por que alta cardinalidade é problemática para partição**

Se você particionar por `user_id` em uma tabela de 100 milhões de usuários distintos, terá 100 milhões de partições. Cada partição terá, em média, pouquíssimos registros. Os problemas resultantes são:

- **Small files problem:** cada partição gera um ou mais arquivos minúsculos. O S3 e o HDFS têm overhead fixo por arquivo (requests, metadata lookups). Milhões de arquivos pequenos degradam drasticamente a performance de qualquer operação sobre o dataset.
- **Overhead de metastore:** o Hive Metastore precisa armazenar e indexar os metadados de cada partição. Com 100 milhões de partições, o metastore fica lento e instável.
- **Pruning ineficaz:** em alta cardinalidade, o pruning reduz pouco o scan (você elimina poucas partições do total). O custo de gerenciar as partições supera o benefício.

**A faixa ideal de cardinalidade para partição**

Não existe um número mágico, mas a prática do mercado indica que partições funcionam bem com cardinalidade entre 10 e 10.000 valores distintos. Abaixo de 10, o pruning é limitado. Acima de 10.000, o risco de small files e overhead de metadados cresce.

Para colunas de alta cardinalidade que precisam ser filtradas com frequência, a solução adequada não é a partição, mas o *clustering* ou o *Z-ordering* (disponível em formatos como Delta e Iceberg), técnicas que organizam os dados dentro de arquivos para melhorar o pruning a nível de row group.

**Exemplos do domínio de marketing**

| Coluna | Cardinalidade estimada | Adequada para partição? |
|---|---|---|
| `event_date` | 365 por ano | Sim, padrão clássico |
| `event_type` | 5 a 10 | Sim, mas avaliar skew |
| `campaign_id` | 100 a 10.000 | Depende do volume por campanha |
| `user_id` | Milhões | Não, alta cardinalidade |
| `country` | 10 a 50 | Sim, se volume equilibrado |

---

#### 6. Skew de partição

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

#### 7. Hot partitions

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

#### 8. Custo versus performance

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

#### 9. A stack do laboratório: MinIO, Hive Metastore, Trino e o papel do Airflow

Esta seção explica o papel de cada componente antes do laboratório prático.

**MinIO, Object Storage S3-compatible**

O MinIO é um servidor de object storage de código aberto que implementa a API do Amazon S3. Ele funciona idêntico ao S3 para qualquer cliente que usa o SDK ou API do S3: você cria buckets, faz PUT de objetos, faz GET, lista prefixos.

A diferença em relação ao S3 real: o MinIO roda localmente, sem custo e sem precisar de conta na AWS. Para fins de laboratório e desenvolvimento, é indistinguível do S3.

Nesta sessão, o MinIO tem três buckets:

- `bronze`: dados brutos, particionados por data.
- `silver`: dados curados e transformados.
- `gold`: dados agregados para consumo analítico.

**Hive Metastore, Catálogo de tabelas**

O Hive Metastore é um serviço independente que armazena metadados de tabelas: nome, schema (colunas e tipos), localização no S3, colunas de partição, lista de partições existentes e estatísticas.

Ele usa um banco relacional como backend. Neste lab, o backend é um PostgreSQL. Em produção na AWS, o serviço equivalente é o AWS Glue Data Catalog, que é totalmente compatível com o protocolo Thrift do Hive Metastore.

A comunicação entre o Trino e o Hive Metastore é via protocolo Thrift na porta 9083. O Trino consulta o metastore sempre que precisa resolver metadados de uma tabela.

**Trino, Engine de consulta SQL**

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

#### 10. Laboratório integrado: CDC → MinIO → Trino → particionamento

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

##### Lab 0: Carregar dados no MinIO (bronze)

Usaremos o MinIO Client via Docker (sem instalar nada no host).

Antes, aponte a variavel abaixo para a pasta onde os dados sinteticos foram gerados na sua
maquina. E o unico caminho que muda de pessoa para pessoa:

```bash
export DADOS_GERADOS="$HOME/dados-mentoria/marketing"
```

```bash
docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v "$DADOS_GERADOS":/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events.csv local/bronze/marketing/raw/events/

docker run --rm \
  --network mentoria-sessao-04-particionamento_default \
  -v "$DADOS_GERADOS":/data \
  -e MC_HOST_local="http://minioadmin:minioadmin@minio:9000" \
  minio/mc:RELEASE.2025-08-13T08-35-41Z \
  cp /data/events__cdc.csv local/bronze/marketing/raw/events_cdc/
```

Isso cria dois prefixos no bucket `bronze`: `raw/events/` e `raw/events_cdc/`.

---

##### Lab 1: Criar schema e tabela bronze (raw)

**Criar schema no bucket bronze**

```sql
CREATE SCHEMA IF NOT EXISTS hive.marketing
WITH (location = 's3://bronze/marketing/');
```

**Criar tabela raw (CSV), somente VARCHAR**

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

##### Lab 2: Criar tabela silver particionada

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

##### Lab 3: Listar partições

```sql
SELECT * FROM hive.marketing."events_silver$partitions";
```

---

##### Lab 4: Query com partition pruning

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

##### Lab 5: Query sem partition pruning (full scan)

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

##### Lab 6 (opcional): CDC aplicado (última versão por event_id)

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

##### Lab 7 (opcional): Alta cardinalidade e particionamento híbrido

Use os labs de alta cardinalidade e particionamento híbrido como extensão (ver checklist e exemplos da sessão 02+03).

---

#### 11. Análise do domínio de marketing

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
- Campanhas têm ciclos de vida curtos, a maioria das análises ainda usa janelas de tempo.

A decisão final deve vir dos padrões de acesso reais, não de suposições.

---

#### 12. Exercícios e entregáveis

##### Exercício 1: Mapa do pipeline + contrato mínimo

**Objetivo:** conectar as caixinhas do Projeto 1.

**Entregável esperado:** diagrama com:
- origem, CDC, bronze, silver, gold e consumo;
- onde entra o Airflow (orquestração);
- contratos básicos (granularidade e chaves).

---

##### Exercício 2: Modelagem mínima

**Objetivo:** definir o grão e as chaves de cada entidade.

**Entregável esperado:** tabela com entidade, grão, chave principal e tipo de mudança (append/upsert).

---

##### Exercício 3: Plano de particionamento

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

##### Exercício 4: Análise de custo

**Contexto:** a tabela `events` tem 2 anos de histórico (730 dias) e 10 M registros por dia, totalizando 7,3 bilhões de registros. Cada registro ocupa 200 bytes em Parquet, totalizando 1,46 TB.

**Cenário A, Sem partição:**
- Uma query que filtra os últimos 7 dias varre todos 1,46 TB.
- Custo estimado no Athena: 1,46 TB x $5/TB = $7,30 por query.

**Cenário B, Particionado por dia:**
- A mesma query lê apenas 7 partições de 730.
- Volume lido: 7/730 x 1,46 TB = ~14 GB.
- Custo estimado no Athena: 14 GB x $5/TB = $0,07 por query.

**Entregável esperado:** tabela comparativa de custo para as tabelas do Exercício 3, usando os volumes estimados e o modelo de precificação do Athena ($5/TB). Calcule o custo mensal assumindo 100 queries/dia para cada tabela nos dois cenários (sem partição vs com partição).

---

##### Exercício 5: Mini ADR de estratégia de partição

**ADR** (Architecture Decision Record) é um documento curto que registra uma decisão técnica com contexto, alternativas consideradas e justificativa.

**Entregável esperado:** ADR com:
- **Título:** Estratégia de particionamento para tabela de eventos.
- **Status:** Proposta.
- **Contexto:** o que motivou a decisão.
- **Decisão:** qual estratégia foi escolhida.
- **Alternativas consideradas:** pelo menos 2 outras estratégias com seus trade-offs.
- **Consequências:** o que muda no pipeline com essa decisão.

---

#### Checklist de validação da sessão

- [ ] Mapa do pipeline end-to-end desenhado.
- [ ] Modelagem mínima definida (grão e chaves).
- [ ] Tabela silver particionada criada com dados do MinIO.
- [ ] Partition pruning demonstrado via EXPLAIN.
- [ ] Plano de particionamento iniciado para o Projeto 1.
- [ ] Trade-offs de custo calculados para pelo menos uma tabela.

---

#### Referências

- **Cap. 8, Data Storage Design Patterns**: padrão Partitioned Table, trade-offs de granularidade.
- **Cap. 10, Data Observability Design Patterns**: métricas operacionais de partições (tamanho, número de arquivos).
- Documentação do Trino: https://trino.io/docs/current/connector/hive.html
- Documentação do MinIO: https://min.io/docs/
- **Arquivos desta sessão:**
  - `data/generated/marketing/events.csv`
  - `data/generated/marketing/events__cdc.csv`
  - `docs/sessions/sessao-02-03-airflow-cdc-tabelas/checklist-execucao-ao-vivo.md`
  - `docs/notes/relatorio-cdc-por-id.md`
  - `infrastructure/sessao-04-particionamento/`

---

## Capitulo 5, Orquestracao com Apache Airflow

Fonte: `modulos/orquestracao-airflow/apostila.md`

### Apostila, Orquestracao com Apache Airflow

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

#### Sumario

- [2.1 Por que orquestrar pipelines de dados](#21-por-que-orquestrar-pipelines-de-dados)
- [2.2 Arquitetura do Apache Airflow](#22-arquitetura-do-apache-airflow)
- [2.3 DAGs, tasks e dependências na prática](#23-dags-tasks-e-dependências-na-prática)
- [2.4 Idempotência e retries](#24-idempotência-e-retries)
- [2.5 Exercícios e entregáveis](#25-exercícios-e-entregáveis)

#### Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.


> Pré-requisito: Capítulo 1, o Airflow é a ferramenta que garante a execução confiável e ordenada do pipeline descrito no ciclo de vida dos dados da Sessão 01.

#### 2.1 Por que orquestrar pipelines de dados

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

#### 2.2 Arquitetura do Apache Airflow

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

#### 2.3 DAGs, tasks e dependências na prática

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

#### 2.4 Idempotência e retries

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

#### 2.5 Exercícios e entregáveis

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


#### Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

#### Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

#### Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

#### Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

#### Glossario

Pendente. Listar os termos novos deste modulo.

#### Referencias

Pendente. Documentacao oficial com data de consulta.

#### Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.

---

## Capitulo 6, Fontes, arquitetura e contratos de dados

Fonte: `modulos/fontes-arquitetura-contratos/apostila.md`

### Apostila, Dados, fontes e arquitetura do projeto real

#### Resumo executivo

Esta apostila é o material de referência completo da Sessão 05. O ponto de entrada não é tecnologia, é negócio. A arquitetura que será construída nas próximas sessões começa com perguntas reais de gestores e stakeholders. Só depois de entender o que precisa ser respondido é possível justificar cada decisão arquitetural.

A sessão apresenta o domínio de dados de uma startup fictícia de marketing/e-commerce, as cinco entidades do projeto, a natureza de cada fonte de dados e as categorias de ferramentas disponíveis para cada tipo de ingestão. O resultado é um architecture canvas v0 com slots de ferramentas marcados e contratos de dados v0 definidos por fonte.

Nenhum comando é executado nesta sessão.

---

#### 1. Objetivo pedagógico

Ao final desta sessão, o mentorado deve ser capaz de:

1. Partir de perguntas de negócio para justificar decisões arquiteturais.
2. Identificar as fontes necessárias para responder qualquer pergunta do projeto.
3. Justificar por que cada fonte exige uma abordagem de ingestão diferente (CDC, batch, streaming).
4. Conhecer as categorias de ferramentas disponíveis para cada tipo de ingestão.
5. Desenhar um architecture canvas v0 com camadas Bronze/Silver/Gold e slots de ferramentas marcados.
6. Definir contratos de dados v0 por fonte: schema, formato, partição e SLA.

---

#### 2. Contexto do projeto (startup fictícia de marketing/e-commerce)

##### 2.1 Cenário

Uma startup de marketing/e-commerce gerencia campanhas pagas em múltiplos canais (Google Ads, Meta, TikTok), tem uma base de usuários em crescimento e precisa responder, semanal e diariamente, perguntas como:

- Quais canais trazem melhor ROI?
- Quais campanhas convertem mais por segmento?
- Onde há queda de conversão no funil?
- Quais usuários estão em risco de churn esta semana?

O time de dados é pequeno. As decisões de arquitetura precisam ser sustentáveis com poucos engenheiros e sem orçamento de enterprise.

##### 2.2 Por que OSS

O projeto usa stack OSS (Airflow, MinIO, Trino) como escolha deliberada por portabilidade e ausência de vendor lock-in. A lógica é a mesma que qualquer stack de dados maduro, camadas, contratos, qualidade. A ferramenta é diferente; os princípios são os mesmos.

---

#### 3. Perguntas de negócio por stakeholder

A arquitetura não começa pelo diagrama. Começa aqui.

##### CEO / Diretoria

- "Qual campanha está gerando mais receita este mês?"
- "Quanto estamos gastando por real faturado em cada canal?"
- "Quantos novos clientes adquirimos esta semana versus a semana passada?"

##### Time de Growth / Marketing

- "Qual é a taxa de conversão do funil por campanha e por canal?"
- "Em qual etapa estamos perdendo mais usuários?"
- "Qual canal tem menor CAC (custo de aquisição de cliente)?"

##### Time de Operações

- "Há alguma queda anômala no volume de checkouts hoje?"
- "Quais usuários estão em risco de churn esta semana?"

##### Time de Analytics / BI

- "Como está a evolução do ROI mês a mês por canal?"
- "Qual é o perfil dos usuários que chegam ao purchase por campanha?"

##### Tabela: pergunta → fontes necessárias

| Pergunta | Stakeholder | Fontes necessárias |
| --- | --- | --- |
| ROI por campanha | CEO / Analytics | `costs` (API) + `events` (Kafka) + `campaigns` (CDC) |
| Taxa de conversão do funil | Growth | `events` (Kafka) |
| Novos clientes por semana | CEO | `users` (CDC) |
| Risco de churn | Operações | `crm` (CDC) + `events` (Kafka) |
| CAC por canal | Growth | `costs` (API) + `users` (CDC) + `events` (Kafka) |
| Queda de checkouts hoje | Operações | `events` (Kafka), requer baixa latência |
| Perfil de usuários que convertem | Analytics | `users` (CDC) + `events` (Kafka) + `campaigns` (CDC) |

**Ponto central:** nenhuma dessas perguntas é respondível com uma fonte só. A motivação da arquitetura é exatamente essa: integrar fontes heterogêneas com contratos claros.

---

#### 4. Modelo de dados, as cinco entidades

##### 4.1 Entidades e campos principais

**users**, Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `user_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome do usuário |
| `email` | VARCHAR | E-mail |
| `segment` | VARCHAR | Segmento (ex.: premium, free) |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**campaigns**, Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `campaign_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome da campanha |
| `channel` | VARCHAR | Canal (google, meta, tiktok) |
| `start_date` | DATE | Data de início |
| `end_date` | DATE | Data de término |
| `status` | VARCHAR | Status (active, paused, ended) |
| `updated_at` | TIMESTAMP | Última atualização |

**events**, Fonte: Kafka (streaming)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `event_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `event_type` | VARCHAR | Tipo: visit, signup, checkout, purchase |
| `occurred_at` | TIMESTAMP | Momento do evento |

**costs**, Fonte: API externa de mídia (batch)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `cost_id` | UUID | Chave primária |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `date` | DATE | Data de referência do custo |
| `channel` | VARCHAR | Canal de mídia |
| `amount` | DECIMAL | Valor investido |
| `currency` | VARCHAR | Moeda (BRL, USD) |

**crm**, Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `crm_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `lifecycle_stage` | VARCHAR | Estágio: lead, active, at_risk, churned |
| `churn_risk_score` | FLOAT | Score de risco de churn (0 a 1) |
| `last_contact_at` | TIMESTAMP | Último contato registrado |
| `updated_at` | TIMESTAMP | Última atualização |

##### 4.2 Diagrama de relações

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

**Tecido conectivo:**
- `user_id` une: `users` ↔ `events` ↔ `crm`
- `campaign_id` une: `campaigns` ↔ `costs` ↔ `events`

`events` é a entidade central: conecta usuários, campanhas e o funil de conversão em um único lugar.

---

#### 5. Natureza das fontes, por que cada uma exige uma abordagem diferente

##### 5.1 PostgreSQL → CDC

**Tabelas:** `users`, `campaigns`, `crm`

**Por que CDC e não batch diário?**

Essas entidades são master data que mudam ao longo do dia. Um usuário pode mudar de segmento, uma campanha pode mudar de status, um score de churn pode ser atualizado múltiplas vezes em um dia.

Com batch diário, você captura apenas o estado final do dia, perde o histórico de alterações. Com CDC, você captura cada alteração com timestamp e tipo de operação (INSERT, UPDATE, DELETE). Isso permite:

- Reconstruir o estado de um registro em qualquer ponto do tempo.
- Detectar anomalias (ex.: campanha que mudou de status três vezes em uma hora).
- Alimentar pipelines downstream com dados frescos sem esperar o batch noturno.

**Frequência esperada:** alterações contínuas ao longo do dia.

**SLA no Bronze:** dados disponíveis em até 30 minutos após alteração.

##### 5.2 API externa de mídia → Batch

**Tabela:** `costs`

**Por que batch e não CDC ou streaming?**

Os custos de campanha em APIs de mídia são imutáveis por data, ou seja, o custo do dia 10 é um snapshot do que foi gasto naquele dia. Não há alterações de registro a rastrear. A API expõe um endpoint por data e você extrai o que aconteceu.

Além disso, APIs de mídia têm rate limits e custos de chamada. Uma extração contínua seria ineficiente e cara sem ganho real, o dado muda uma vez por dia, no máximo.

Batch diário por data é a abordagem natural: extrai os custos do dia anterior até às 8h e disponibiliza para análise.

**Frequência esperada:** uma extração por dia.

**SLA no Bronze:** dados do dia anterior disponíveis até às 8h.

##### 5.3 Kafka → Streaming

**Tabela:** `events`

**Por que streaming e não batch?**

Eventos de funil têm valor na latência. Detectar uma queda no volume de checkouts às 14h, em tempo quase real, é uma informação acionável, você pode investigar e corrigir o problema antes que o impacto seja maior. Ver isso no relatório de ontem não tem o mesmo valor.

Além disso, eventos têm natureza append-only: cada evento é imutável após ocorrer. Não há UPDATE nem DELETE, só INSERT. Isso torna o streaming uma abordagem natural: cada evento publicado no Kafka é consumido e gravado no Bronze sem complexidade de merge.

**Importante:** Kafka será implementado em sessão futura. Nesta sessão, o contrato é projetado e o slot na arquitetura é reservado. A implementação não existe ainda.

**Frequência esperada:** contínua, por evento.

**SLA no Bronze:** latência máxima de 5 minutos do evento ao Bronze.

---

#### 6. Ferramentas de ingestão, categorias e exemplos

O objetivo desta seção não é escolher a ferramenta, é abrir o mapa de opções. A escolha acontece na Sessão 06, depois da tarefa de casa.

##### 6.1 CDC

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Debezium | OSS, connector Kafka | Padrão de mercado para CDC em PostgreSQL/MySQL. Requer Kafka. |
| Airbyte | OSS/Cloud, plataforma | Tem conector CDC via log replication. Mais fácil de operar. |
| Fivetran | SaaS | Gerenciado, fácil de configurar, mas tem custo por linha sincronizada. |
| AWS DMS | Cloud (AWS) | Gerenciado pela AWS, bom para ambientes já na AWS. |
| Kafka Connect (JDBC) | OSS | Polling via JDBC, não é CDC puro, não captura DELETEs. |

##### 6.2 API batch

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Airbyte | OSS/Cloud, plataforma | Tem conectores prontos para Google Ads, Meta Ads, etc. |
| Fivetran | SaaS | Conectores prontos e gerenciados. Custo por linha. |
| Meltano | OSS | Baseado em Singer. Flexível, mas exige mais configuração. |
| Singer | OSS, protocolo | Base do Meltano/Airbyte. Taps e targets customizáveis. |
| Script Python custom | Custom | Máximo controle, máximo custo de manutenção. |

##### 6.3 Streaming / Kafka

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Kafka Connect | OSS | Conectores para sources e sinks. Ecosistema amplo. |
| Confluent Platform | Cloud/Enterprise | Kafka gerenciado com operações simplificadas. |
| Flink | OSS | Processamento stateful, janelas, joins em streaming. |
| Spark Structured Streaming | OSS | Bom para times com histórico em Spark. |

---

#### 7. Make vs buy, critérios para um time pequeno

Para cada fonte, a decisão não é "qual é a ferramenta mais poderosa?", é "qual é a ferramenta que sustentamos com o time que temos?"

##### Critérios de avaliação

| Critério | Favorece ferramenta pronta | Favorece script custom |
| --- | --- | --- |
| Número de fontes | Muitas fontes | Poucas fontes muito específicas |
| Frequência de mudança do contrato da fonte | Alta (API instável) | Baixa (contrato estável) |
| Disponibilidade de manutenção | Time pequeno, sem plantão | Time com capacidade de manter |
| Custo de licença aceitável | Sim | Não, budget restrito |
| Conector pronto disponível | Sim | Não existe conector adequado |
| Complexidade de lógica custom | Baixa | Alta, regras de negócio embutidas |

##### Ponto de atenção

Ferramentas prontas reduzem custo de engenharia inicial, mas introduzem dependência de vendor e custo de licença recorrente. Scripts custom têm custo de manutenção invisível, quem mantém quando o engenheiro que escreveu sai da empresa?

Para um time em fase de crescimento, a pergunta mais honesta é: "quem vai manter isso às 2h da manhã quando quebrar?"

---

#### 8. Contratos de dados v0

Para cada fonte, preencha os atributos do contrato com base na discussão da sessão.

##### PostgreSQL CDC, `users`, `campaigns`, `crm`

| Atributo | Valor |
| --- | --- |
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

##### API de mídia, `costs`

| Atributo | Valor |
| --- | --- |
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

##### Kafka, `events` (contrato projetado, implementação futura)

| Atributo | Valor |
| --- | --- |
| Schema | |
| Tópico | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

---

#### 9. Exercício 2, Architecture canvas v0

Guia para desenhar o canvas em conjunto durante o Bloco 4.

**Passo 1, Fontes (canto esquerdo):**
Listar as três fontes: PostgreSQL, API de mídia, Kafka. Anotar a natureza de cada uma (CDC, batch, streaming).

**Passo 2, Camada de ingestão:**
Para cada fonte, marcar o slot da ferramenta com `[?]`. A escolha da ferramenta fica aberta, é a tarefa de casa.

**Passo 3, Camadas de armazenamento:**
Desenhar Bronze → Silver → Gold. Para cada camada, anotar:
- Bronze: raw, imutável, particionado por data de ingestão
- Silver: deduplicado, joins aplicados, schema confiável
- Gold: datasets de negócio, prontos para responder as perguntas da seção 3

**Passo 4, Consumo (canto direito):**
Listar os consumidores: BI/dashboards, analytics ad-hoc, ativações. Conectar ao Gold.

**Passo 5, Validação:**
Percorrer o canvas de trás para frente: pegar uma pergunta da seção 3 e traçar o caminho até a fonte. Se o caminho existir e estiver completo, o canvas está correto para essa pergunta.

---

#### 10. Exercício 1, Mapeamento de perguntas para fontes

**Objetivo:** praticar o raciocínio de tracing reverso, partir de uma pergunta de negócio e identificar quais entidades e fontes são necessárias para respondê-la.

**Referência:** use a lista de perguntas da seção 3 e o modelo de dados da seção 4.

**Instrução:**

Escolha três perguntas da seção 3 (uma de stakeholders diferentes, se possível). Para cada pergunta, preencha uma linha da tabela abaixo:

- **Pergunta**: copie a pergunta exatamente como está na seção 3.
- **Entidades necessárias**: liste as tabelas do domínio (seção 4.1) cujos campos são necessários para responder.
- **Fontes de ingestão**: identifique de onde cada entidade vem, CDC, API batch ou Kafka (seção 5).
- **Chave de conexão utilizada**: indique qual chave (`user_id`, `campaign_id` ou nenhuma) conecta as entidades listadas.

| Pergunta (seção 3) | Entidades necessárias | Fontes de ingestão | Chave de conexão utilizada |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

**Exemplo resolvido** (não usar como resposta, é apenas para entender o formato):

| Pergunta | Entidades necessárias | Fontes de ingestão | Chave de conexão |
| --- | --- | --- | --- |
| "Qual canal tem menor CAC?" | `costs`, `users`, `events` | API batch + CDC + Kafka | `campaign_id` (costs↔events) e `user_id` (users↔events) |

**Critério de aceite:** para cada linha, o caminho fonte → entidade → pergunta deve ser traçável sem gaps.

---

#### 11. Template, Tarefa de casa

A ser apresentada no início da Sessão 06.

| Ingestão | Ferramenta proposta | Justificativa (custo, complexidade, manutenção) |
| --- | --- | --- |
| CDC (PostgreSQL) | | |
| API de mídia (batch) | | |
| Streaming (Kafka) | | |

---

#### 12. Critérios de aceite da sessão

- Perguntas dos gestores mapeadas para fontes necessárias.
- Entidades do domínio e relações via `user_id` e `campaign_id` desenhadas.
- Natureza de cada fonte justificada com critério técnico.
- Categorias de ferramentas apresentadas para CDC, API e streaming.
- Architecture canvas v0 desenhado com slots de ferramentas marcados.
- Contratos de dados v0 definidos para as três fontes.
- Contrato do Kafka projetado, schema, tópico, partição, sem implementação.
- Tarefa de casa comunicada: proposta de ferramenta por tipo de ingestão para a S06.
- Backlog claro e priorizado para a Sessão 06.

---

#### 13. O que deliberadamente não decidir agora

Para evitar paralisia por análise:

- Não fechar a escolha de ferramenta de ingestão para nenhuma das fontes, essa é a tarefa de casa.
- Não detalhar os jobs individuais de cada pipeline.
- Não discutir sizing de infraestrutura, tuning ou benchmarks.
- Não modelar as tabelas Silver e Gold em detalhes, isso é Sessão 06 em diante.
- Não buscar perfeição no canvas v0, ele vai evoluir. O objetivo é ter um ponto de partida validado.
- Não implementar nada. Nenhum arquivo é criado, nenhum comando é executado.

---

## Capitulo 7, Change Data Capture

Fonte: `modulos/cdc/apostila.md`

### Apostila, Change Data Capture

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

#### Sumario

- [3.1 Change Data Capture (CDC), conceito e lifecycle](#31-change-data-capture-cdc-conceito-e-lifecycle)
- [3.2 CDC por ciclo de vida de ID, regras e pitfalls](#32-cdc-por-ciclo-de-vida-de-id-regras-e-pitfalls)

#### Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

#### 3.1 Change Data Capture (CDC), conceito e lifecycle

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

- `cdc_op`: tipo da operação, `insert`, `update` ou `delete`.
- `cdc_event_ts`: timestamp do evento.
- `cdc_source_table`: tabela de origem.
- Os dados do registro no estado em que estava no momento do evento.

**A diferença entre append-only e upsert**

Uma tabela append-only só recebe novos registros; registros passados nunca mudam. Exemplos: logs de acesso, eventos de clique, transações financeiras.

Uma tabela com upsert recebe inserções e também atualizações de registros existentes. Exemplos: cadastro de clientes, status de pedidos, saldo de conta.

O CDC é especialmente relevante para tabelas com upsert. Se você precisar reconstruir o estado atual de um cadastro de clientes, precisa saber não apenas o insert inicial, mas todos os updates subsequentes e, eventualmente, o delete.

#### 3.2 CDC por ciclo de vida de ID, regras e pitfalls

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


#### Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

#### Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

#### Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

#### Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

#### Glossario

Pendente. Listar os termos novos deste modulo.

#### Referencias

Pendente. Documentacao oficial com data de consulta.

#### Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.

---

## Capitulo 8, Transformacao com dbt

Fonte: `modulos/dbt/apostila.md`

### Apostila, dbt: transformação com SQL versionado e testado

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

#### Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O que o dbt é, e o que ele não é](#3-o-que-o-dbt-é-e-o-que-ele-não-é)
- [4. Model, ref e o DAG](#4-model-ref-e-o-dag)
- [5. Materializações](#5-materializações)
- [6. Camadas: sources, staging e marts](#6-camadas-sources-staging-e-marts)
- [7. Seeds e snapshots](#7-seeds-e-snapshots)
- [8. Jinja e macros](#8-jinja-e-macros)
- [9. Testes: genéricos, singulares e unitários](#9-testes-genéricos-singulares-e-unitários)
- [10. Contratos, documentação e linhagem](#10-contratos-documentação-e-linhagem)
- [11. Laboratório](#11-laboratório)
- [12. Exercícios e entregáveis](#12-exercícios-e-entregáveis)
- [13. Mini-desafio com solução](#13-mini-desafio-com-solução)
- [14. Rubrica de validação da aprendizagem](#14-rubrica-de-validação-da-aprendizagem)
- [15. Erros comuns e como corrigir](#15-erros-comuns-e-como-corrigir)
- [16. Plano de continuidade](#16-plano-de-continuidade)
- [17. Glossário](#17-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

#### 0. Como usar esta apostila

**Leitura linear.** Seções 1 a 10 constroem o modelo mental. A seção 11 é o
laboratório, e ela só faz sentido depois da 6. As seções 12 a 14 são o que você
entrega e como isso é avaliado na call.

**Revisão pontual.** Se você já usa dbt e veio atrás de um assunto específico,
vá direto: materialização na 5, teste na 9, contrato na 10. A seção 15 é a que
mais economiza tempo de quem já está com o projeto na mão.

**Pré-requisitos.** SQL com JOIN e agregação, no nível do módulo de SQL da
trilha. Docker rodando na sua máquina, no nível do módulo de Docker. Você não
precisa saber Python, e não precisa de conta em nuvem.

**Versões desta apostila.** Tudo foi verificado com dbt Core 1.12.0 e
dbt-duckdb 1.10.1, em 2026-07-31. Onde a versão importa para o comportamento, a
apostila diz qual.

#### 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** por que o dbt existe e qual problema do ELT ele resolve, sem
   recorrer a "porque é a ferramenta padrão".
2. **Escrever** um model em SQL que o dbt materializa como view, table ou
   incremental, e justificar a escolha por custo e frequência.
3. **Conectar** models pelo `ref()` e ler o DAG resultante, entendendo por que a
   ordem de execução não é escrita por você.
4. **Organizar** um projeto em sources, staging e marts, dizendo o que entra em
   cada camada e o que nunca entra.
5. **Testar** dados com teste genérico, teste singular e unit test, sabendo qual
   dos três responde a qual pergunta.
6. **Declarar** um contrato de model e prever o que quebra quando o contrato é
   violado.
7. **Diagnosticar** as falhas mais comuns de um projeto dbt a partir da
   mensagem de erro, sem tentativa e erro.

O verbo de cada item é o que será cobrado. "Explicar" é oral, na call.
"Escrever" e "testar" são código que roda.

#### 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha continua a mesma. Ela
veicula campanhas pagas em Google Ads, Meta Ads e TikTok Ads, e nos módulos
anteriores você já construiu a parte de baixo do pipeline: o object storage
guardando o dado bruto, o particionamento decidindo o custo da leitura, o
Airflow orquestrando a ingestão e o Kafka trazendo o evento quase em tempo real.

O que ainda não existe é a camada que responde à pergunta do negócio. Hoje o
analista abre o dado cru e escreve, de novo, o mesmo JOIN entre campanha,
veiculação e conversão. Cada um escreve um pouco diferente. Quando a diretoria
pergunta qual canal tem o melhor custo por conversão, chegam dois números.

A pergunta deste módulo é essa: **quanto custou cada conversão, por canal e por
dia, com um número só, calculado num lugar só.**

O que este módulo acrescenta ao projeto:

| Camada | Já existia | Este módulo acrescenta |
|---|---|---|
| Ingestão | Airflow, Kafka, MinIO | nada |
| Armazenamento | Parquet particionado | nada |
| Transformação | query solta de analista | models versionados, testados e documentados |
| Consumo | planilha | uma tabela fato com uma definição única |

#### 3. O que o dbt é, e o que ele não é

##### 3.1 O recorte do dbt no ELT

**O que é**

O dbt é a camada de transformação de um pipeline ELT. Ele não extrai dado e não
carrega dado: ele pega o que já está no banco e produz tabelas e views novas a
partir de SELECT.

A sigla ajuda a lembrar do recorte. No ETL clássico, você transforma antes de
carregar, geralmente numa máquina intermediária. No ELT, você carrega primeiro e
transforma dentro do próprio banco, usando o poder de processamento dele. O dbt
é o "T" do ELT, e só ele.

**Como funciona na prática**

Você escreve um arquivo `.sql` com um SELECT. O dbt envolve esse SELECT no DDL
apropriado e submete ao banco. Você nunca escreve `CREATE TABLE`, `DROP TABLE`
nem `CREATE SCHEMA`.

**O equívoco comum**

Muita gente descreve o dbt como "um orquestrador". Ele ordena a execução dos
próprios models, o que é diferente de orquestrar um pipeline. Ele não agenda,
não tenta de novo com backoff, não observa fonte externa e não dispara alerta
por si. Quem faz isso é o Airflow, do módulo de orquestração. Em produção os
dois convivem: o Airflow chama o dbt.

**Como inspecionar**

O comando `dbt compile` mostra o SQL que seria enviado ao banco, sem enviar.
É a forma mais direta de ver que o dbt é um gerador de SQL, não um motor de
processamento.

##### 3.2 Analytics engineering, a prática por trás da ferramenta

O dbt trouxe para o trabalho analítico quatro coisas que a engenharia de
software já tinha: versionamento, teste automatizado, documentação junto do
código e integração contínua.

O ganho não é a ferramenta, é a mudança de quem responde pela definição. Antes
do dbt, "receita líquida" morava dentro de uma query no BI, de um Excel e da
cabeça de duas pessoas. Depois, mora num arquivo com histórico no Git.

##### 3.3 dbt Core, dbt Cloud e o motor Fusion

| Sabor | O que é | Quando faz sentido |
|---|---|---|
| dbt Core | CLI open source, roda local ou em qualquer orquestrador | Todo projeto começa aqui, e muitos ficam |
| dbt Cloud | Plataforma gerenciada, com IDE, agendador, documentação e CI | Time sem engenheiro de plataforma disponível |
| Fusion | Motor escrito em Rust, com entendimento nativo de SQL por dialeto | Hoje é o padrão da instalação nova do dbt |

O Fusion merece atenção porque o cenário mudou rápido. A documentação oficial
descreve o Fusion como a experiência padrão ao instalar o dbt, construída sobre
o runtime Apache 2.0 do dbt Core 2.0. Ao mesmo tempo, a página de versões do
dbt Core lista o 2.0 como alpha, e o 1.12, de 2026-07-16, como a versão em
suporte ativo.

As duas coisas convivem, e a leitura honesta é: o Fusion é o caminho declarado,
e a linha 1.x é a que está em suporte ativo hoje. O laboratório deste módulo fixa
o dbt Core 1.12.0 por esse motivo. Quando você for escolher para um projeto real,
confira as duas páginas na data da decisão, porque essa fronteira anda.

Nada do que você aprende aqui muda de nome com o Fusion. Model, `ref`, teste,
materialização e contrato são o framework, não o motor.

#### 4. Model, ref e o DAG

##### 4.1 O model é um SELECT

**O que é**

Um model é um arquivo `.sql` dentro de `models/`, com um SELECT. O nome do
arquivo vira o nome do objeto no banco.

**Como funciona na prática**

Este é um model real do laboratório, o `stg_campanhas`:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```sql
select
    cast(campanha_id as integer)             as campanha_id,
    trim(nome)                               as nome_campanha,
    lower(trim(canal))                       as canal,
    cast(data_inicio as date)                as data_inicio,
    cast(orcamento_diario as decimal(10, 2)) as orcamento_diario
from {{ source('bruto', 'campanhas') }}
```

O passo a passo do que acontece quando você roda `dbt run`:

1. O dbt lê todos os arquivos do projeto e monta o manifesto, que é o mapa de
   tudo que existe e de quem depende de quem.
2. Ele resolve o `{{ source(...) }}` para o nome real da tabela ou do arquivo.
3. Ele envolve o SELECT no DDL da materialização escolhida.
4. Ele submete o SQL ao banco e registra o resultado.

**O equívoco comum**

Que o nome do model precisa ser declarado em algum lugar. Não precisa. O nome do
arquivo é o nome do model, e é ele que o `ref()` procura. Renomear o arquivo
renomeia o objeto e quebra todo `ref()` que apontava para o nome antigo.

**Como inspecionar**

O SQL final fica em `target/compiled/`. Abrir esse arquivo é o hábito que mais
acelera o aprendizado no começo, porque ele elimina a dúvida sobre o que o Jinja
virou.

##### 4.2 ref, a função que constrói o grafo

**O que é**

`ref('nome_do_model')` é como um model aponta para outro. Ela devolve o nome
qualificado do objeto no banco e, ao mesmo tempo, declara uma dependência.

**Como funciona na prática**

```sql
select * from {{ ref('stg_eventos_campanha') }}
```

O dbt lê isso e conclui duas coisas: onde buscar o dado e que este model precisa
rodar depois do `stg_eventos_campanha`. É a mesma linha respondendo às duas
perguntas, e é por isso que o grafo nunca desatualiza em relação ao código.

**O equívoco comum**

Escrever o nome da tabela direto, porque "funciona igual". Funciona na primeira
execução e falha na segunda. Sem o `ref()`, o dbt não sabe da dependência, roda
os dois models na ordem errada e você recebe um erro de tabela inexistente que
não tem relação aparente com o que você escreveu.

O mesmo vale para o `source()`: ele marca a fronteira entre o que o dbt produz e
o que ele apenas consome.

**Como inspecionar**

`dbt list --select stg_campanhas+` lista o model e tudo que depende dele. O `+`
à direita significa descendentes, e à esquerda, ancestrais.

##### 4.3 O DAG não é escrito, é derivado

**O que é**

O grafo acíclico dirigido do projeto é o conjunto de todas as dependências
declaradas por `ref()` e `source()`. Ninguém escreve a ordem de execução.

**O equívoco comum**

Achar que existe um arquivo de ordenação para editar quando a execução sai
errada. Não existe, e isso é a característica central. Se a ordem está errada,
a dependência está errada, e o conserto é no `ref()`.

**Como inspecionar**

No laboratório, o `dbt build` imprime a ordem que ele escolheu, numerada. Foi
assim que o Lab 2 mostrou os models de staging rodando antes do mart, sem que
nada no projeto declare isso.

#### 5. Materializações

##### 5.1 As cinco materializações

**O que é**

A materialização decide como o resultado do SELECT é persistido. A
documentação oficial lista cinco embutidas: `table`, `view`, `incremental`,
`ephemeral` e `materialized view`. O padrão, quando você não declara nada, é
`view`.

| Materialização | O que o dbt faz | Custo de armazenamento | Custo de leitura |
|---|---|---|---|
| `view` | Cria uma view, recriada a cada execução | nenhum | paga a transformação a cada consulta |
| `table` | Recria a tabela inteira a cada execução | tamanho do resultado | baixo |
| `incremental` | Processa só o que chegou desde a última vez | tamanho do resultado | baixo |
| `ephemeral` | Não cria objeto, injeta o SQL como CTE | nenhum | herdado de quem a consome |
| `materialized view` | Delega ao banco a atualização da view | depende do banco | baixo |

**Como funciona na prática**

Você declara no bloco `config` do próprio model, ou por pasta no
`dbt_project.yml`. O laboratório usa a segunda forma, porque a decisão é da
camada, não do arquivo:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  campanhas:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

**O equívoco comum**

Marcar tudo como `table` porque "table é mais rápido". Rápido para ler, caro
para construir. Uma camada de staging que só renomeia e converte tipo raramente
justifica o custo de reescrever a tabela inteira a cada execução.

A regra prática que funciona: staging em `view`, mart em `table`, e `incremental`
apenas quando a tabela cheia começa a doer no tempo ou na fatura.

##### 5.2 Incremental, o que muda de verdade

**O que é**

Um model incremental transforma todas as linhas na primeira execução e, nas
seguintes, apenas as que você filtrar. O filtro é seu, não do dbt.

**Como funciona na prática**

Este é o `fct_custo_diario` do laboratório:

<!-- verificacao: nivel 3, docker compose run --rm dbt run --select fct_custo_diario, dbt-core 1.12.0, 2026-07-31 -->

```sql
{{ config(materialized="incremental", unique_key=["campanha_id", "data_evento"]) }}

select
    campanha_id,
    data_evento,
    sum(custo) as custo
from {{ ref('stg_eventos_campanha') }}

{% if is_incremental() %}
    where data_evento > (
        select coalesce(max(data_evento), date '1900-01-01') from {{ this }}
    )
{% endif %}

group by campanha_id, data_evento
```

A macro `is_incremental()` devolve verdadeiro quando três condições valem ao
mesmo tempo, segundo a documentação oficial: o model já existe como tabela no
banco, a execução não passou `--full-refresh`, e o model está configurado como
`incremental`.

No Lab 4 você vê isso acontecer. Na primeira execução o bloco `{% if %}`
desaparece do SQL compilado. Na segunda, ele aparece:

<!-- verificacao: nivel 3, saida real de target/compiled na 2a execucao, 2026-07-31 -->

```sql
    where data_evento > (
        select coalesce(max(data_evento), date '1900-01-01')
        from "campanhas"."main"."fct_custo_diario"
    )
```

**O equívoco comum**

Achar que o `unique_key` faz o filtro. Ele não faz. O `unique_key` decide o que
acontece com uma linha que já existe, atualizar em vez de duplicar. Quem decide
o que sequer é lido é o `where` dentro do `is_incremental()`. Sem ele, o
incremental lê tudo e só economiza escrita.

**Como inspecionar**

Rode o model duas vezes e compare `target/compiled/` entre as execuções. É a
prova, não a explicação.

#### 6. Camadas: sources, staging e marts

##### 6.1 A fronteira do source

**O que é**

Um `source` declara uma tabela que o dbt lê mas não produz. É a fronteira do
projeto.

**Como funciona na prática**

No laboratório, os arquivos brutos são CSV lidos diretamente pelo adapter:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-duckdb 1.10.1, 2026-07-31 -->

```yaml
sources:
  - name: bruto
    meta:
      external_location: "dados_brutos/{name}.csv"
    tables:
      - name: campanhas
      - name: eventos_campanha
      - name: conversoes
```

A chave `external_location` é específica do dbt-duckdb, e existe para que o
adapter leia o arquivo no lugar de uma tabela do catálogo. Num data warehouse de
nuvem você não usaria isso: as tabelas cruas já estariam carregadas, e o source
apenas declararia schema e nome.

**O equívoco comum**

Usar `source()` para uma tabela que o próprio dbt cria. Isso desliga a
dependência, e o resultado é o mesmo erro de ordem de execução da seção 4.2. A
regra é curta: se o dbt cria, é `ref`. Se alguém entrega, é `source`.

##### 6.2 Staging, uma fonte por model

**O que é**

A camada de staging tem um model por tabela de origem. Ela faz apenas o que é
mecânico: renomear coluna, converter tipo, normalizar texto.

**O equívoco comum**

Colocar regra de negócio no staging. O sintoma aparece meses depois, quando dois
marts precisam da mesma origem com regras diferentes e alguém decide duplicar o
staging. A partir daí existem duas verdades.

O teste mental: se a resposta a "por que essa linha está aqui" envolve uma
decisão de negócio, a linha não é de staging.

##### 6.3 Marts, o modelo que o negócio consome

**O que é**

O mart é o modelo final por domínio. É onde vive a regra de negócio, a junção
entre fontes e o cálculo que a diretoria vai citar em reunião.

**Como funciona na prática**

O `fct_desempenho_campanha` junta veiculação, cadastro, conversão e o de para de
canal, e produz o número que o módulo prometeu na seção 2. Rodado no Lab 3, ele
responde:

<!-- verificacao: nivel 3, docker compose run --rm dbt show, saida real, 2026-07-31 -->

```
| grupo_de_canal |   custo | conversoes | custo_por_conversao |
| -------------- | ------- | ---------- | ------------------- |
| Social         | 4,747.9 |          7 |              678.27 |
| Search         | 4,126.8 |          5 |              825.36 |
```

O dado é fictício, e o formato da resposta não é. É esse recorte que encerra a
discussão de qual canal está mais caro.

**O equívoco comum**

Uma camada intermediária que ninguém consegue explicar. Modelos `int_` existem
para reaproveitar junção usada por mais de um mart. Quando existe um `int_` com
um consumidor só, ele geralmente é um mart mal nomeado.

#### 7. Seeds e snapshots

##### 7.1 Seed, o CSV que é código

**O que é**

Um seed é um arquivo CSV dentro de `seeds/`, carregado como tabela pelo comando
`dbt seed`. Ele serve para dado pequeno, estável e versionado.

**Como funciona na prática**

O laboratório usa um de para de canal:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```csv
canal,grupo_de_canal,e_pago
google_ads,Search,true
meta_ads,Social,true
tiktok_ads,Social,true
```

**O equívoco comum**

Usar seed para carregar dado de produção. Seed vive no Git, e Git não é lugar de
volume nem de dado pessoal. O critério é: cabe numa revisão de pull request e
muda por decisão humana? Então é seed.

##### 7.2 Snapshot, o histórico que a origem não guarda

**O que é**

Um snapshot registra como uma linha era em cada momento. É a resposta ao problema
de origem que sobrescreve o próprio dado, e implementa o padrão conhecido como
dimensão de mudança lenta, ou SCD tipo 2.

**Como funciona na prática**

A partir do dbt Core 1.9 o snapshot é declarado em YAML:

<!-- verificacao: nivel 3, docker compose run --rm dbt snapshot, dbt-core 1.12.0, 2026-07-31 -->

```yaml
snapshots:
  - name: snap_campanhas
    relation: ref('stg_campanhas')
    config:
      unique_key: campanha_id
      strategy: check
      check_cols: ["orcamento_diario"]
```

Existem duas estratégias. A `timestamp` usa uma coluna de data de alteração da
própria origem, e é a preferida quando ela existe. A `check` compara os valores
das colunas listadas a cada execução, e é o que sobra quando a origem não traz
data confiável.

O dbt acrescenta colunas de controle, entre elas `dbt_scd_id`, `dbt_valid_from`,
`dbt_valid_to` e `dbt_updated_at`. No Lab 5 você altera o orçamento de uma
campanha e vê o resultado:

<!-- verificacao: nivel 3, docker compose run --rm dbt show, saida real, 2026-07-31 -->

```
| campanha_id | orcamento_diario |       dbt_valid_from |         dbt_valid_to |
| ----------- | ---------------- | -------------------- | -------------------- |
|           3 |              450 | 2026-07-31 16:22:... | 2026-07-31 16:23:... |
|           3 |              500 | 2026-07-31 16:23:... |                      |
```

A linha antiga não foi apagada. Ela foi fechada, e a nova nasceu aberta. Quem
consome a tabela hoje filtra `dbt_valid_to is null`; quem precisa saber qual era
o orçamento em junho consulta pela data.

**O equívoco comum**

Rodar o snapshot uma vez por semana e esperar histórico diário. O snapshot só
enxerga o que existe no instante em que roda. Mudança que aconteceu e voltou
atrás entre duas execuções é invisível, para sempre. A frequência do snapshot é
a resolução do seu histórico.

#### 8. Jinja e macros

##### 8.1 Jinja é a parte que roda antes do SQL

**O que é**

Jinja é a linguagem de template que o dbt usa. Ela é processada antes de o SQL
chegar ao banco, e produz texto.

Duas sintaxes bastam para começar: `{{ ... }}` insere um valor no texto, e
`{% ... %}` executa lógica sem inserir nada.

**O equívoco comum**

Tratar Jinja como se fosse parte do SQL. O banco nunca vê Jinja. Isso explica
por que um validador de SQL puro rejeita um model do dbt: para ele, `{{` não é
sintaxe válida. Também explica por que erro de Jinja aparece na compilação, e
erro de SQL aparece na execução.

##### 8.2 Macro, a função que você escreve

**O que é**

Uma macro é um bloco reutilizável de Jinja e SQL, declarado em `macros/`.

**Como funciona na prática**

O laboratório tem uma macro pequena e útil, que evita divisão por zero:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```jinja
{% macro razao_segura(numerador, denominador) %}
    {{ numerador }} / nullif({{ denominador }}, 0)
{% endmacro %}
```

E o mart a chama:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```sql
cast(
    {{ razao_segura('eventos.custo', 'conversoes_por_dia.conversoes') }}
    as decimal(12, 2)
) as custo_por_conversao
```

Os argumentos vão entre aspas porque a macro recebe o **texto** do nome da
coluna, não o valor dela.

**O equívoco comum**

Criar macro cedo demais. Duas ocorrências de um trecho ainda são duas
ocorrências. Na terceira, o padrão está claro e a macro nasce com o nome certo.
Macro criada na primeira ocorrência costuma abstrair a coisa errada.

**Como inspecionar**

O `target/compiled/` mostra a macro já expandida. Se a expansão surpreende, o
problema é a macro, não o model.

#### 9. Testes: genéricos, singulares e unitários

##### 9.1 Os três tipos, e a pergunta de cada um

| Tipo | Pergunta que responde | Roda quando |
|---|---|---|
| Genérico | Este dado obedece a uma regra conhecida? | depois de o model existir |
| Singular | Esta condição específica do meu negócio se sustenta? | depois de o model existir |
| Unitário | Minha lógica está certa para uma entrada que eu escolhi? | antes de o model ser materializado |

A diferença entre os dois primeiros e o terceiro é a que mais confunde. Teste
genérico e singular olham o dado que existe. Unit test olha a lógica, com dado
que você inventou de propósito.

##### 9.2 Testes genéricos

**O que é**

O dbt traz quatro testes genéricos embutidos: `unique`, `not_null`,
`accepted_values` e `relationships`.

**Como funciona na prática**

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  - name: stg_campanhas
    columns:
      - name: campanha_id
        data_tests:
          - unique
          - not_null
      - name: canal
        data_tests:
          - accepted_values:
              arguments:
                values: ["google_ads", "meta_ads", "tiktok_ads"]
```

Duas mudanças de sintaxe importam aqui, e as duas já pegaram gente de surpresa:

1. A chave é `data_tests`, não `tests`. O nome antigo ainda aparece em muito
   material na internet.
2. Os argumentos do teste vivem dentro de `arguments`, disponível a partir da
   versão 1.10.5. Versões anteriores esperavam o argumento no nível de cima.

**O equívoco comum**

Achar que teste genérico é enfeite de projeto maduro. O Lab 6 mostra o
contrário: uma linha com canal desconhecido no CSV bruto derruba o build antes
que o número errado chegue ao mart.

**Como inspecionar**

Quando um teste falha, o dbt informa o caminho do SQL compilado. Abrir esse
arquivo e rodar a query mostra exatamente quais linhas quebraram a regra.

##### 9.3 Testes singulares

**O que é**

Um teste singular é um arquivo `.sql` em `tests/` com uma query que precisa
devolver zero linhas. Cada linha devolvida é uma violação.

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```sql
select
    campanha_id,
    data_evento,
    custo
from {{ ref('fct_desempenho_campanha') }}
where custo < 0
```

A inversão de lógica é a fonte de erro mais comum aqui. Você escreve a query que
encontra o **problema**, não a que confirma que está tudo bem.

##### 9.4 Unit tests

**O que é**

Unit tests chegaram no dbt Core 1.8. Eles validam a lógica do model com entradas
fixas, antes de materializar qualquer coisa.

**Como funciona na prática**

Este unit test do laboratório protege uma decisão de negócio real: dia sem
conversão precisa ter custo por conversão nulo, e não zero.

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
unit_tests:
  - name: test_dia_sem_conversao_nao_vira_zero
    model: fct_desempenho_campanha
    given:
      - input: ref('stg_eventos_campanha')
        rows:
          - {evento_id: 1, campanha_id: 1, data_evento: "2026-06-01", impressoes: 100, cliques: 10, custo: 50.00}
      - input: ref('stg_conversoes')
        rows: []
    expect:
      rows:
        - {campanha_id: 1, data_evento: "2026-06-01", conversoes: 0, custo_por_conversao: null}
```

Zero diria que a conversão saiu de graça, que é o contrário do que aconteceu.
Nenhum dado real do laboratório expõe essa diferença hoje, e é exatamente por
isso que ela precisa de um teste com dado inventado.

**O equívoco comum**

Escrever unit test para o que o banco já garante. Testar que `sum()` soma gasta
tempo e não protege nada. Unit test vale para lógica sua: janela, regex, cálculo
condicional, tratamento de nulo.

Uma restrição prática: todo `ref()` e `source()` que o model usa precisa
aparecer em `given`. Não dá para fornecer metade das entradas.

#### 10. Contratos, documentação e linhagem

##### 10.1 Contrato de model

**O que é**

Um contrato declara a forma que a saída do model precisa ter: nome e tipo de
cada coluna, e restrições opcionais. Com `enforced: true`, o model falha ao
construir quando a saída não bate.

**Como funciona na prática**

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  - name: fct_desempenho_campanha
    config:
      contract:
        enforced: true
    columns:
      - name: campanha_id
        data_type: integer
        constraints:
          - type: not_null
      - name: custo
        data_type: decimal(12,2)
```

O contrato faz duas coisas: uma checagem prévia comparando as colunas do SELECT
com as declaradas, e a inclusão de tipos e restrições no DDL enviado ao banco.

A segunda parte é visível. Depois do Lab 2, o DuckDB mostra a coluna como não
anulável de verdade:

<!-- verificacao: nivel 3, describe main.fct_desempenho_campanha, saida real, 2026-07-31 -->

```
│     column_name     │  column_type  │  null   │
├─────────────────────┼───────────────┼─────────┤
│ campanha_id         │ INTEGER       │ NO      │
│ custo               │ DECIMAL(12,2) │ YES     │
```

A restrição não ficou só no YAML. Ela virou DDL.

**O equívoco comum**

Confundir contrato com teste. Teste roda depois e reprova o dado. Contrato roda
junto da construção e reprova a **estrutura**. Uma coluna renomeada por engano
passa em todos os testes de valor e é barrada pelo contrato.

Vale saber o limite: contrato funciona em `table`, `view` com restrições
limitadas, e `incremental`. Não funciona em `ephemeral` nem em `materialized
view`.

##### 10.2 Documentação e linhagem

O `dbt docs generate` produz um site navegável com a descrição de cada model e
coluna, mais o DAG clicável. A descrição vem do mesmo YAML onde vivem os testes,
que é o ponto: documentação que mora longe do código envelhece sem que ninguém
perceba.

Este módulo não gera a documentação no laboratório. O comando existe e está na
referência oficial citada no fim da apostila, e o exercício 4 pede que você o
rode.

#### 11. Laboratório

O laboratório roda inteiro em Docker, com dbt Core 1.12.0, dbt-duckdb 1.10.1 e
DuckDB 1.5.5. Nada sai da sua máquina, e não há credencial de nuvem envolvida.

Os runbooks em `infrastructure/runbooks/` trazem o passo a passo completo. O
resumo abaixo diz o que cada laboratório prova.

##### Lab 0: Construir a imagem

Pré-condição: Docker Engine 28 ou superior e Docker Compose v2.

```bash
cd engenharia_de_dados/modulos/dbt/infrastructure
export DBT_UID=$(id -u)
export DBT_GID=$(id -g)
docker compose build
```

Saída esperada: ` mentoria-dbt:1.12.0  Built`.

As duas variáveis existem por um motivo prático: sem elas o container escreve
`target/` e `logs/` como root no seu disco, e você precisa de `sudo` para
limpar depois.

##### Lab 1: Conferir a conexão

```bash
docker compose run --rm dbt debug
```

Saída esperada: `Connection test: [OK connection ok]` e `All checks passed!`.

O `dbt debug` confere projeto, perfil, dependências e conexão. Quando ele
reclama, o problema está antes do seu SQL.

##### Lab 2: Rodar o projeto inteiro

```bash
docker compose run --rm dbt build
```

Saída esperada: `Done. PASS=22 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=22`.

Os 22 nós são 1 seed, 3 models de staging, 1 mart em `table`, 1 model
incremental, 1 snapshot, 14 data tests e 1 unit test. O `dbt build` executa
model, teste, snapshot e seed na ordem do DAG.

Repare na ordem impressa: o unit test roda **antes** do model que ele testa, e
os testes de staging rodam antes de o mart existir. Ninguém escreveu essa ordem.

##### Lab 3: Ler o resultado

```bash
docker compose run --rm dbt show --inline "select grupo_de_canal, sum(custo) as custo, sum(conversoes) as conversoes, round(sum(custo) / nullif(sum(conversoes), 0), 2) as custo_por_conversao from {{ ref('fct_desempenho_campanha') }} group by grupo_de_canal order by custo_por_conversao"
```

Saída esperada: `Social` com custo por conversão 678.27 e `Search` com 825.36.

Esta é a pergunta da seção 2 respondida com um número só.

##### Lab 4: Ver o incremental funcionar

Pré-condição: Lab 2 concluído.

```bash
docker compose run --rm dbt run --select fct_custo_diario
sed -n '1,20p' projeto_dbt/target/compiled/campanhas/models/marts/fct_custo_diario.sql
```

Saída esperada: o SQL compilado da segunda execução traz a cláusula `where
data_evento > (...)`, que não existia na primeira.

##### Lab 5: Ver o snapshot registrar uma mudança

Pré-condição: Lab 2 concluído.

```bash
sed -i 's/^3,Remarketing Carrinho,meta_ads,2026-06-03,450.00$/3,Remarketing Carrinho,meta_ads,2026-06-03,500.00/' projeto_dbt/dados_brutos/campanhas.csv
docker compose run --rm dbt snapshot
docker compose run --rm dbt show --inline "select campanha_id, orcamento_diario, dbt_valid_from, dbt_valid_to from {{ ref('snap_campanhas') }} where campanha_id = 3 order by dbt_valid_from"
sed -i 's/^3,Remarketing Carrinho,meta_ads,2026-06-03,500.00$/3,Remarketing Carrinho,meta_ads,2026-06-03,450.00/' projeto_dbt/dados_brutos/campanhas.csv
```

Saída esperada: duas linhas para a campanha 3, a de 450 com `dbt_valid_to`
preenchido e a de 500 com `dbt_valid_to` vazio.

O último comando devolve o CSV ao estado original.

##### Lab 6: Quebrar um teste de propósito

```bash
printf '6,Teste Linkedin,linkedin_ads,2026-06-07,200.00\n' >> projeto_dbt/dados_brutos/campanhas.csv
docker compose run --rm dbt build --select stg_campanhas
sed -i '$d' projeto_dbt/dados_brutos/campanhas.csv
```

Saída esperada:

```
[ERROR]: in test accepted_values_stg_campanhas_canal__google_ads__meta_ads__tiktok_ads
  Got 1 result, configured to fail if != 0
Done. PASS=6 WARN=0 ERROR=1 SKIP=0 NO-OP=0 REUSED=0 TOTAL=7
```

Este é o laboratório mais importante da lista. Ver o pipeline parar por causa de
um dado ruim é o que transforma teste de dados de burocracia em rede de
proteção.

##### Lab 7: Derrubar o ambiente

```bash
docker compose run --rm dbt clean
docker compose down --rmi local
```

A ordem importa. O `clean` precisa da imagem ainda de pé.

#### 12. Exercícios e entregáveis

**Exercício 1: Escolha de materialização**

Objetivo: justificar materialização por custo e frequência, não por hábito.

Contexto: os quatro models do laboratório, mais dois hipotéticos, uma tabela de
eventos com 400 milhões de linhas atualizada de hora em hora, e um relatório
executivo consultado três vezes por mês.

Entregável: tabela com uma linha por model, contendo materialização escolhida,
justificativa em uma frase e o que aconteceria com a escolha oposta.

**Exercício 2: Um teste que pega um erro real**

Objetivo: escrever teste a partir de uma falha plausível, não de uma lista.

Contexto: o `fct_desempenho_campanha` do laboratório.

Entregável: um teste genérico novo e um teste singular novo, os dois no projeto,
mais a demonstração de cada um falhando. Para demonstrar a falha, altere o CSV
bruto, rode, capture a saída e desfaça a alteração, como no Lab 6.

**Exercício 3: Camada intermediária**

Objetivo: reconhecer quando um `int_` se justifica.

Contexto: suponha um segundo mart, `fct_funil_por_canal`, que precisa da mesma
junção entre eventos, campanhas e de para de canal.

Entregável: proposta de refatoração indicando o que vira `int_`, o que fica no
mart, e o critério que você usou. Se a sua conclusão for que não vale a pena
criar o `int_`, defenda isso, que também é resposta.

**Exercício 4: Documentação e linhagem**

Objetivo: usar o material de documentação que o projeto já produz.

Contexto: o projeto do laboratório, depois do Lab 2.

Entregável: as descrições de coluna do `fct_desempenho_campanha` preenchidas no
YAML, mais a saída do comando de geração de documentação e uma observação sobre
o que o DAG mostrou que você não esperava.

#### 13. Mini-desafio com solução

**Enunciado**

O time de marketing pede uma tabela nova: receita por grupo de canal e semana,
com a variação percentual em relação à semana anterior. A tabela vai para um
painel executivo consultado algumas vezes por mês.

Requisitos:

1. Um model novo, com materialização justificada.
2. Reaproveitar o que já existe, sem reescrever junção.
3. Pelo menos um teste que proteja a conta.
4. Tratar o caso da primeira semana, que não tem semana anterior.

**Dicas**

- A junção entre eventos, campanhas e canal já existe em algum lugar do projeto.
- Variação percentual é uma divisão, e o projeto já tem uma macro para divisão
  que pode dar zero no denominador.
- A primeira semana é o mesmo problema do dia sem conversão da seção 9.4.

**Gabarito comentado**

Materialização `table`. O consumo é raro, então o custo de leitura importa pouco;
o volume é pequeno, então `incremental` só acrescenta complexidade. `view`
também funcionaria, e a diferença é irrelevante nessa escala. O que não se
justifica é `incremental`, e a razão é que a complexidade tem um custo de
manutenção que o ganho não paga.

Reaproveitamento: o model parte de `ref('fct_desempenho_campanha')`, que já
resolveu a junção. Partir do staging de novo criaria a segunda definição de
receita, que é o problema que o módulo inteiro existe para evitar.

Esqueleto da lógica:

```sql
with semanal as (
    select
        grupo_de_canal,
        date_trunc('week', data_evento) as semana,
        sum(receita) as receita
    from {{ ref('fct_desempenho_campanha') }}
    group by grupo_de_canal, date_trunc('week', data_evento)
)

select
    grupo_de_canal,
    semana,
    receita,
    lag(receita) over (partition by grupo_de_canal order by semana) as receita_anterior,
    {{ razao_segura(
        'receita - lag(receita) over (partition by grupo_de_canal order by semana)',
        'lag(receita) over (partition by grupo_de_canal order by semana)'
    ) }} as variacao
from semanal
```

<!-- verificacao: nivel 1, esqueleto didatico conferido contra a doc de macros e de window function, nao executado no laboratorio, 2026-07-31 -->

Este bloco é esqueleto de resposta, não código do laboratório. Ele foi conferido
contra a documentação de macro do dbt, e não foi executado. Rodá-lo é parte do
desafio.

Primeira semana: o `lag` devolve nulo, o `nullif` dentro da macro impede o erro
de divisão, e o resultado é nulo. Nulo é a resposta certa aqui, porque não houve
variação a medir. Preencher com zero afirmaria estabilidade que não existiu.

Teste que protege a conta: um teste singular que devolve as linhas onde
`variacao` é nula e `receita_anterior` não é. Se isso acontecer, a macro está
errada, não o dado.

**Interpretação**

O que separa a boa resposta da resposta correta é o item 2. Quem parte do mart
existente entendeu que o valor do dbt está na definição única. Quem reescreve a
junção produziu SQL que funciona e um problema de governança.

#### 14. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Papel do dbt | Descreve como orquestrador ou como banco | Situa como camada de transformação do ELT | Explica a fronteira com o Airflow e por que os dois convivem |
| ref e DAG | Escreve nome de tabela direto | Usa `ref` e `source` corretamente | Diagnostica erro de ordem de execução a partir da mensagem |
| Materialização | Usa `table` em tudo | Escolhe por custo e frequência, e justifica | Sabe quando `incremental` não compensa e defende a escolha |
| Camadas | Mistura regra de negócio no staging | Separa staging de mart com critério | Argumenta quando um `int_` se justifica e quando não |
| Testes | Só usa `not_null` e `unique` | Usa os três tipos na situação certa | Escreve teste a partir de uma falha real observada |
| Contrato | Confunde com teste de dado | Declara contrato e prevê o que ele barra | Explica o limite por materialização |
| Diagnóstico | Tenta e erra até funcionar | Lê a mensagem e vai ao ponto | Usa `target/compiled/` como primeiro passo |

A avaliação é feita na call, sobre o código que você entregou nos exercícios.

#### 15. Erros comuns e como corrigir

**O seed não encontra o próprio CSV**

Sintoma: `IO Error: No files found that match the pattern`, com um caminho
absoluto que não existe dentro do container.

Causa: o `target/` foi escrito por uma execução fora do Docker. O manifesto
guardou o caminho da máquina de fora, e o parse parcial reaproveitou.

Correção: `dbt clean` e rodar de novo. Esse erro apareceu de verdade na
construção deste laboratório, na primeira vez em que o projeto rodou no host e
depois no container.

**Model roda antes da dependência**

Sintoma: erro de tabela ou view inexistente, num model que estava funcionando.

Causa: nome de tabela escrito direto em vez de `ref()`. Sem o `ref()` não existe
aresta no grafo, e sem aresta não existe ordem.

Correção: trocar por `ref()`. Confirmar com `dbt list --select <model>+`.

**O incremental não economiza nada**

Sintoma: o tempo de execução não cai depois da primeira vez.

Causa: falta o bloco `{% if is_incremental() %}` com o filtro. O `unique_key`
sozinho evita duplicata, não evita leitura.

Correção: acrescentar o filtro e comparar `target/compiled/` entre duas
execuções.

**O teste passa e o número está errado**

Sintoma: todos os testes verdes, e o negócio aponta um valor que não fecha.

Causa: os testes existentes cobrem forma, não regra. `not_null` e `unique` não
sabem o que é uma conversão.

Correção: escrever teste singular a partir da regra de negócio, e unit test para
a lógica que o dado atual não exercita, como o caso do dia sem conversão.

**`tests:` não funciona como o tutorial mostra**

Sintoma: o teste declarado no YAML é ignorado, ou o parse reclama.

Causa: material antigo. A chave é `data_tests`, e o argumento do teste vive
dentro de `arguments` a partir da versão 1.10.5.

Correção: conferir a sintaxe na documentação da sua versão, e a versão com
`dbt --version`.

**Arquivos root no seu diretório**

Sintoma: `target/` e `logs/` que você não consegue apagar sem `sudo`.

Causa: container rodando como root sobre um volume montado.

Correção: exportar `DBT_UID` e `DBT_GID` antes do `docker compose`, como no
Lab 0.

**O `dbt debug` reclama de git**

Sintoma: `Could not find command, ensure it is in the user's PATH: "git"`.

Causa: imagem base enxuta sem git. O dbt usa git para baixar pacote.

Correção: instalar git na imagem. O `Dockerfile` do laboratório já faz isso, e
esse erro foi a razão.

#### 16. Plano de continuidade

**Antes da próxima call**

Termine os exercícios 1 e 2. Eles são a base da conversa.

**O que estudar em seguida, dentro da trilha**

O próximo bloco é Nuvem e escala. O módulo de cloud para dados mostra onde esse
projeto dbt rodaria de verdade, com o data warehouse no lugar do DuckDB. O de
infraestrutura como código trata de como esse ambiente nasce sem ninguém clicar
em console.

O módulo de orquestração com Airflow, que você já viu, ganha um recorte novo
depois deste: em produção o `dbt build` é uma tarefa chamada pelo agendador, e a
integração entre os dois DAGs é um assunto por si.

**O que aprofundar por conta**

Pacotes do ecossistema, a começar por `dbt_utils`, que resolve problema comum
com macro pronta. Depois, integração contínua: rodar apenas o que mudou num pull
request é o ganho que mais aparece quando o projeto passa de algumas dezenas de
models.

**O que não perseguir agora**

Semantic layer e exposures são úteis e não mudam nada até o projeto ter
consumidor de verdade. Deixe para quando existir painel apontando para o mart.

#### 17. Glossário

| Termo | Significado |
|---|---|
| Adapter | Biblioteca que traduz o SQL do dbt para um banco específico |
| Contrato | Declaração da forma da saída de um model, verificada na construção |
| DAG | Grafo de dependências entre models, derivado dos `ref` e `source` |
| Data test | Teste que avalia o dado depois de o model existir |
| Ephemeral | Materialização que não cria objeto, injetada como CTE |
| Incremental | Materialização que processa apenas o recorte filtrado por você |
| Jinja | Linguagem de template processada antes de o SQL chegar ao banco |
| Macro | Bloco reutilizável de Jinja e SQL, declarado em `macros/` |
| Manifesto | Arquivo em `target/` com o mapa completo do projeto |
| Mart | Camada final, por domínio de negócio |
| Materialização | Estratégia de persistência do resultado de um model |
| Model | Arquivo `.sql` com um SELECT que o dbt transforma em objeto no banco |
| ref | Função que aponta para outro model e cria a dependência |
| SCD tipo 2 | Padrão que guarda cada versão de uma linha ao longo do tempo |
| Seed | CSV versionado, carregado como tabela por `dbt seed` |
| Snapshot | Captura periódica que registra mudança de linha ao longo do tempo |
| source | Função e declaração de tabela que o dbt lê mas não produz |
| Staging | Camada de limpeza mecânica, um model por origem |
| Unit test | Teste da lógica do model com entradas fixas, antes de materializar |

#### Referências

Documentação oficial do dbt, consultada em 2026-07-31:

- Materializações: https://docs.getdbt.com/docs/build/materializations
- Models incrementais: https://docs.getdbt.com/docs/build/incremental-models
- Snapshots: https://docs.getdbt.com/docs/build/snapshots
- Jinja e macros: https://docs.getdbt.com/docs/build/jinja-macros
- Data tests: https://docs.getdbt.com/reference/resource-properties/data-tests
- Unit tests: https://docs.getdbt.com/docs/build/unit-tests
- Contratos de model: https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- Comandos: https://docs.getdbt.com/reference/dbt-commands
- Comando build: https://docs.getdbt.com/reference/commands/build
- Versões do dbt Core: https://docs.getdbt.com/docs/dbt-versions/core
- Motor Fusion: https://docs.getdbt.com/docs/fusion/about-fusion
- Adapter dbt-duckdb: https://github.com/duckdb/dbt-duckdb

#### Fontes verificadas (2026-07-31)

- O dbt tem cinco materializações embutidas, `table`, `view`, `incremental`,
  `ephemeral` e `materialized view`, e o padrão é `view`.
  https://docs.getdbt.com/docs/build/materializations
- `is_incremental()` é verdadeiro quando o model já existe como tabela, a
  execução não passou `--full-refresh` e o model é `incremental`.
  https://docs.getdbt.com/docs/build/incremental-models
- O snapshot é declarado em YAML com `relation`, `unique_key`, `strategy` e
  `check_cols`, e o dbt acrescenta `dbt_scd_id`, `dbt_valid_from`,
  `dbt_valid_to` e `dbt_updated_at`. https://docs.getdbt.com/docs/build/snapshots
- Os quatro testes genéricos embutidos são `unique`, `not_null`,
  `accepted_values` e `relationships`, declarados sob `data_tests`.
  https://docs.getdbt.com/reference/resource-properties/data-tests
- A chave `arguments` para argumento de teste genérico está disponível a partir
  da versão 1.10.5, e versões anteriores usam o argumento no nível de cima.
  https://docs.getdbt.com/reference/resource-properties/data-tests
- Unit tests foram introduzidos no dbt Core 1.8, exigem todos os `ref` e
  `source` do model em `given`, e não suportam `materialized view`.
  https://docs.getdbt.com/docs/build/unit-tests
- Contrato com `enforced: true` faz checagem prévia das colunas e inclui tipos e
  restrições no DDL, e falha o build quando violado. Ele suporta `table`,
  `view` com restrições limitadas e `incremental`, e não suporta `ephemeral`
  nem `materialized view`.
  https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- O `dbt build` executa models, tests, snapshots, seeds e funções definidas pelo
  usuário, em ordem do DAG. https://docs.getdbt.com/reference/commands/build
- O dbt Core 1.12 foi lançado em 2026-07-16 e está em suporte ativo; o 1.11 é de
  2025-12-19 e o dbt Core 2.0 aparece como alpha.
  https://docs.getdbt.com/docs/dbt-versions/core
- O motor Fusion é escrito em Rust e é descrito como a experiência padrão da
  instalação do dbt, sobre o runtime Apache 2.0 do dbt Core 2.0.
  https://docs.getdbt.com/docs/fusion/about-fusion
- O dbt-duckdb 1.10.1 foi publicado em 2026-02-17, exige Python 3.10 ou
  superior, `dbt-core>=1.8.0` e `duckdb>=1.0.0`.
  https://pypi.org/project/dbt-duckdb/
- O dbt-duckdb lê arquivo externo como source pela chave `external_location`
  declarada em `meta`. https://github.com/duckdb/dbt-duckdb
- As saídas de laboratório citadas nesta apostila, incluindo
  `PASS=22 WARN=0 ERROR=0`, o SQL compilado do incremental, as duas linhas do
  snapshot e a coluna `campanha_id` como não anulável, foram capturadas em
  execução real com dbt Core 1.12.0, dbt-duckdb 1.10.1 e DuckDB 1.5.5. O
  registro completo, com comando e nível, está em `lab.json`.

---

## Capitulo 9, Cloud para dados

Fonte: `modulos/cloud-para-dados/apostila.md`

### Apostila, cloud para dados: o que muda quando o dado sai da sua máquina

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

#### Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O que a nuvem realmente muda](#3-o-que-a-nuvem-realmente-muda)
- [4. Modelos de serviço e responsabilidade compartilhada](#4-modelos-de-serviço-e-responsabilidade-compartilhada)
- [5. As quatro primitivas](#5-as-quatro-primitivas)
- [6. Armazenamento de objetos e o custo de esquecer a classe](#6-armazenamento-de-objetos-e-o-custo-de-esquecer-a-classe)
- [7. Compute, do controle total ao serverless](#7-compute-do-controle-total-ao-serverless)
- [8. O destino analítico](#8-o-destino-analítico)
- [9. Identidade, o novo perímetro](#9-identidade-o-novo-perímetro)
- [10. Rede, a VPC](#10-rede-a-vpc)
- [11. FinOps, o custo é decisão de arquitetura](#11-finops-o-custo-é-decisão-de-arquitetura)
- [12. O mapa entre provedores](#12-o-mapa-entre-provedores)
- [13. Mão na massa sem gastar](#13-mão-na-massa-sem-gastar)
- [14. Exercícios e entregáveis](#14-exercícios-e-entregáveis)
- [15. Mini-desafio com solução](#15-mini-desafio-com-solução)
- [16. Rubrica de validação da aprendizagem](#16-rubrica-de-validação-da-aprendizagem)
- [17. Erros comuns e como corrigir](#17-erros-comuns-e-como-corrigir)
- [18. Plano de continuidade](#18-plano-de-continuidade)
- [19. Glossário](#19-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

#### 0. Como usar esta apostila

**Leitura linear.** As seções 3 a 5 montam o vocabulário. Da 6 à 11 cada seção
trata de uma decisão que você vai tomar de verdade. A 12 é consulta, não
leitura.

**Revisão pontual.** Se você já trabalha em nuvem e veio atrás de um assunto,
vá direto: classes de armazenamento na 6, IAM na 9, custo na 11.

**Pré-requisitos.** Os módulos de object storage, particionamento e formatos de
tabela. Este módulo assume que você já sabe o que é um data lake e por que a
chave de partição decide o custo da query. Aqui a pergunta é outra: o que muda
quando isso tudo roda na infraestrutura de outra pessoa.

**Este módulo não tem laboratório.** Subir recurso de verdade custa dinheiro e
exige credencial, e a trilha não pede que você abra conta em nuvem. O que dá
para provar sem conta está provado: os blocos de código desta apostila passam
por `scripts/verificar_blocos.py`, que confere sintaxe de SQL, de política IAM e
de comando da AWS CLI sem tocar a rede. Nível 2 da escada de verificação, e a
apostila diz onde ele para.

**Este módulo é um mapa, não um destino.** Quase todo assunto tratado aqui tem
dono em outro módulo da trilha. A seção diz quem é o dono e trata apenas do
recorte de nuvem.

#### 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** o que a nuvem troca em relação ao servidor próprio, em termos de
   custo e de risco, sem cair em "é mais barato".
2. **Situar** um serviço no espectro IaaS, PaaS e SaaS, e dizer o que sobra para
   você em cada ponto do espectro.
3. **Escolher** a classe de armazenamento de um conjunto de dados a partir do
   padrão de acesso, e prever o que a escolha errada custa.
4. **Escrever** uma política IAM de menor privilégio para um caso concreto de
   leitura de data lake.
5. **Traduzir** um serviço entre AWS, GCP e Azure quando ler uma vaga, uma
   arquitetura ou um artigo.
6. **Identificar** as três ou quatro decisões que respondem pela maior parte da
   fatura de um pipeline de dados.

#### 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha chegou até aqui rodando
tudo em Docker na máquina de quem desenvolve: MinIO fazendo o papel do object
storage, Trino consultando, Airflow orquestrando, Kafka transportando evento e
dbt transformando.

Isso funcionou para aprender e não funciona para operar. Três fatos empurram a
mudança:

1. O volume de eventos de campanha cresceu, e a máquina que roda tudo é a mesma
   que alguém usa para trabalhar.
2. O relatório precisa existir quando quem trabalha está dormindo.
3. Se o notebook morrer, o histórico morre junto.

A pergunta deste módulo é: **o que exatamente estamos alugando, o que continua
sendo nossa responsabilidade, e onde o dinheiro vai embora.**

O que este módulo acrescenta ao projeto:

| Camada | Local, até aqui | Na nuvem |
|---|---|---|
| Object storage | MinIO em container | S3, Cloud Storage ou Blob |
| Query engine | Trino em container | Athena, BigQuery ou Redshift |
| Orquestração | Airflow em container | Airflow gerenciado |
| Transformação | dbt na sua máquina | o mesmo dbt, chamado pelo orquestrador |
| Responsabilidade por backup, disco e rede | sua | dividida, e a divisão tem regra |

#### 3. O que a nuvem realmente muda

##### 3.1 A troca de investimento por consumo

**O que é**

No servidor próprio, você compra capacidade antes de precisar dela e paga por
ela parada. Na nuvem, você aluga capacidade e paga pelo que consome.

**Como funciona na prática**

A consequência prática não é o preço, é **quando** você decide. Comprar servidor
obriga a acertar a previsão de carga com meses de antecedência. Alugar permite
errar a previsão e corrigir no mesmo dia.

**O equívoco comum**

Que nuvem é mais barata. Não é, por unidade de recurso. Um servidor próprio bem
utilizado, com carga estável e previsível, costuma sair mais barato por hora de
CPU. O que a nuvem vende é elasticidade e a eliminação do risco de errar a
compra, e isso tem preço.

Quem migra carga estável esperando economia se decepciona. Quem migra carga
irregular esperando não decidir com antecedência acerta.

##### 3.2 Região e zona de disponibilidade

**O que é**

Uma região é uma área geográfica separada. Dentro de cada região existem várias
zonas de disponibilidade, que são locais isolados entre si.

A AWS declara hoje 39 regiões lançadas e 123 zonas de disponibilidade, com cada
região tendo pelo menos três zonas independentes e fisicamente separadas.

**Como funciona na prática**

Você escolhe a região por três motivos, nesta ordem de frequência: onde o dado
pode legalmente ficar, onde estão seus usuários, e o preço, que varia por região.

Distribuir a carga entre zonas protege da falha de um local dentro da região.
Distribuir entre regiões protege da falha da região inteira, e custa muito mais.

**O equívoco comum**

Achar que a nuvem replica tudo sozinha. A documentação da AWS é explícita: as
regiões são isoladas umas das outras e os recursos **não são replicados
automaticamente** entre elas. Quem não configurou a replicação não tem
replicação, e descobre isso no pior dia possível.

**Como inspecionar**

Ao listar recursos no console ou na CLI, você vê apenas o que existe na região
selecionada. Recurso que "sumiu" quase sempre está em outra região.

#### 4. Modelos de serviço e responsabilidade compartilhada

##### 4.1 O espectro IaaS, PaaS e SaaS

**O que é**

Os três nomes descrevem quanto da pilha o provedor opera por você.

| Modelo | Você opera | O provedor opera | Exemplo em dados |
|---|---|---|---|
| IaaS | Sistema operacional, runtime e aplicação | Hardware, rede e virtualização | Uma VM rodando seu Spark |
| PaaS | Apenas sua aplicação e seus dados | A plataforma inteira | Um data warehouse gerenciado |
| SaaS | Apenas a configuração e o uso | Tudo | Uma ferramenta de BI |

**O equívoco comum**

Ler o espectro como uma escada de qualidade, em que o mais gerenciado é sempre
melhor. É uma escada de **troca**: quanto menos você opera, menos você controla
e menos consegue prever o custo em carga atípica.

##### 4.2 O que continua sendo seu

**O que é**

O modelo de responsabilidade compartilhada divide a segurança em duas partes. A
AWS descreve a sua como "segurança **da** nuvem" e a sua parte como "segurança
**na** nuvem".

| Lado | Do que responde |
|---|---|
| Provedor | Infraestrutura que roda os serviços: hardware, software, rede, instalações, sistema operacional do hospedeiro e camada de virtualização |
| Você | Sistema operacional convidado e seus patches, aplicação instalada, configuração de security group, gestão e criptografia dos dados, permissões de IAM |

**O equívoco comum**

Ler "gerenciado" como "seguro". O provedor garante que o serviço funciona e que
o data center é protegido. Bucket aberto para a internet, chave de acesso
commitada e permissão ampla demais são responsabilidade sua, e são a origem da
maioria dos vazamentos noticiados.

A própria documentação registra que a divisão varia por serviço: um serviço de
infraestrutura exige mais configuração sua, e um serviço abstrato transfere mais
operação ao provedor.

#### 5. As quatro primitivas

Quase todo serviço de nuvem é combinação de quatro coisas. Entender as quatro
destrava o catálogo inteiro, que tem centenas de nomes.

| Primitiva | O que resolve | Onde aparece em dados |
|---|---|---|
| Compute | Executar código | Ingestão, transformação, query |
| Storage | Guardar bytes | Data lake, warehouse, backup |
| Rede | Ligar e isolar | Acesso privado ao lake, saída de dados |
| Identidade | Dizer quem pode o quê | Todo o resto |

A ordem não é acidental. Identidade vem por último na lista e primeiro na
consequência: um erro de compute derruba um job, e um erro de identidade
vaza a base inteira.

#### 6. Armazenamento de objetos e o custo de esquecer a classe

O conceito de object storage tem dono na trilha, que é o módulo de object
storage com MinIO. Aqui tratamos só do que é específico de nuvem: as classes de
armazenamento e o que elas cobram.

##### 6.1 Durabilidade não é o problema

**O que é**

A AWS declara durabilidade de 99,999999999 por cento, os onze noves, para todas
as classes do S3 exceto a Reduced Redundancy Storage, que fica em 99,99 por
cento e a própria AWS recomenda não usar.

**O equívoco comum**

Confundir durabilidade com disponibilidade. Durabilidade é a chance de o objeto
continuar existindo. Disponibilidade é a chance de você conseguir lê-lo agora.
São números diferentes e a diferença importa: a S3 One Zone-IA tem os mesmos
onze noves de durabilidade da Standard, e disponibilidade projetada de 99,5 por
cento contra 99,99 por cento, porque vive em uma zona só.

E há um detalhe que a palavra durabilidade esconde: nenhuma classe protege
contra você apagar o objeto. Isso é versionamento e política de retenção, não
durabilidade.

##### 6.2 A tabela que decide a fatura

**Como funciona na prática**

| Classe | Disponibilidade projetada | Zonas | Duração mínima | Tamanho mínimo faturável |
|---|---|---|---|---|
| S3 Standard | 99,99% | 3 ou mais | nenhuma | nenhum |
| S3 Intelligent-Tiering | 99,9% | 3 ou mais | nenhuma | nenhum |
| S3 Standard-IA | 99,9% | 3 ou mais | 30 dias | 128 KB |
| S3 One Zone-IA | 99,5% | 1 | 30 dias | 128 KB |
| S3 Glacier Instant Retrieval | 99,9% | 3 ou mais | 90 dias | 128 KB |
| S3 Glacier Flexible Retrieval | 99,99% após restaurar | 3 ou mais | 90 dias | sem mínimo declarado |
| S3 Glacier Deep Archive | 99,99% após restaurar | 3 ou mais | 180 dias | sem mínimo declarado |

Duas colunas fazem mais estrago do que o preço por gigabyte:

**A duração mínima.** Objeto movido para Standard-IA e apagado em 5 dias é
cobrado por 30. Em Deep Archive, por 180. Uma política de ciclo de vida mal
calibrada em cima de dado que gira rápido aumenta a fatura em vez de reduzir.

**O tamanho mínimo faturável.** Objeto de 8 KB em Standard-IA é cobrado como
128 KB. Um lake com milhões de arquivos pequenos, que é exatamente o que uma
ingestão de streaming mal configurada produz, paga dezesseis vezes o que
armazena.

**O equívoco comum**

Mover o lake inteiro para uma classe fria para economizar. As classes de acesso
infrequente cobram taxa de recuperação por gigabyte. Dado que a análise lê toda
semana sai mais caro em Standard-IA do que em Standard.

A regra prática: a classe segue o padrão de acesso, não a idade do dado. Idade é
apenas um bom palpite sobre o padrão de acesso, e palpite erra.

##### 6.3 Quando você não sabe o padrão de acesso

A classe Intelligent-Tiering existe para esse caso. Ela move o objeto entre
camadas conforme o acesso observado, cobra uma taxa de monitoramento por objeto
e não cobra taxa de recuperação.

Um detalhe muda a conta: objetos com menos de 128 KB não são monitorados e ficam
sempre na camada de acesso frequente. Num lake de arquivos pequenos, a taxa de
monitoramento é paga sem o benefício correspondente.

#### 7. Compute, do controle total ao serverless

**O que é**

Compute na nuvem é um espectro, do controle total do servidor até a função que
escala a zero.

| Forma | Você gerencia | Bom para | Ruim para |
|---|---|---|---|
| Máquina virtual | Sistema operacional e tudo acima | Carga contínua, software exigente | Carga esporádica, paga parada |
| Container gerenciado | A imagem | Job de pipeline, serviço de médio porte | Escala a zero com latência sensível |
| Serverless | Apenas o código | Evento esporádico, cola entre serviços | Job longo, dependência pesada |

O conceito de orquestração de containers tem dono na trilha, que é o módulo de
Kubernetes. Aqui interessa uma decisão só: **quanto do seu pipeline precisa
estar de pé o tempo todo.**

**O equívoco comum**

Colocar transformação pesada em serverless porque "escala a zero". Serviços de
função têm limite de tempo de execução e de memória, e um job que ultrapassa o
limite falha no meio, sem estado. O que escala a zero bem é a cola: reagir a um
arquivo que chegou, disparar um pipeline, notificar.

#### 8. O destino analítico

Os formatos de arquivo e os tipos de tabela têm dono na trilha, que é o módulo
de formatos e tipos de tabela. Aqui tratamos da escolha do destino.

##### 8.1 Warehouse, lake e lakehouse

**O que é**

O data warehouse guarda o dado num formato proprietário, otimizado para query, e
cobra por armazenamento e processamento. O data lake guarda arquivo em formato
aberto no object storage, e alguma engine consulta por cima. O lakehouse é a
tentativa de ter o armazenamento barato do lake com a garantia transacional do
warehouse, através de formato de tabela aberto.

| Critério | Warehouse | Lake com engine | Lakehouse |
|---|---|---|---|
| Custo de armazenamento | maior | menor | menor |
| Facilidade de começar | maior | menor | média |
| Portabilidade do dado | menor | maior | maior |
| Garantia transacional | forte | fraca ou nenhuma | forte |

**O equívoco comum**

Escolher pela arquitetura de referência de um fornecedor. A pergunta que decide
é mais simples: quantos consumidores diferentes vão ler esse dado? Um consumidor
só, com equipe pequena, é caso de warehouse gerenciado, e a discussão de formato
aberto é prematura. Muitos consumidores com ferramentas diferentes é caso de
formato aberto, e aí o lakehouse paga o próprio custo de complexidade.

##### 8.2 Query sobre o lake, e o modelo de cobrança que ela traz

**Como funciona na prática**

Serviços que consultam direto no object storage cobram por dado escaneado. Isso
muda o que significa uma query cara: não é a que demora, é a que lê muito.

A documentação de preço do Athena é explícita sobre a alavanca: comprimir o
arquivo e convertê-lo para um formato colunar como o Parquet permite que a
engine leia apenas a coluna relevante, e isso reduz o que você paga. A mesma
página usa a taxa de 5 dólares por terabyte como exemplo ilustrativo do cálculo.

Este é o ponto onde o módulo de particionamento e performance deixa de ser
teoria. Lá você aprendeu que a chave de partição decide quanto o engine lê. Aqui
a mesma decisão aparece na fatura, com nome e valor.

<!-- verificacao: nivel 2, sqlglot 30.14.0 dialetos hive e trino, scripts/verificar_blocos.py, 2026-07-31 -->

```sql
CREATE EXTERNAL TABLE raw.eventos_campanha (
    evento_id   BIGINT,
    campanha_id INT,
    impressoes  BIGINT,
    cliques     BIGINT,
    custo       DECIMAL(12, 2)
)
PARTITIONED BY (data_evento DATE)
STORED AS PARQUET
LOCATION 's3://empresa-data-lake/raw/eventos_campanha/'
```

E a query que aproveita a partição:

<!-- verificacao: nivel 2, sqlglot 30.14.0 dialeto trino, scripts/verificar_blocos.py, 2026-07-31 -->

```sql
SELECT canal, sum(custo) AS custo
FROM raw.eventos_campanha
WHERE data_evento BETWEEN DATE '2026-06-01' AND DATE '2026-06-30'
GROUP BY canal
```

Os dois blocos passaram no parse, o que prova a sintaxe e nada além. Não existe
tabela, não existe bucket e ninguém executou a query. Isso é o teto honesto de
um módulo sem laboratório em nuvem.

#### 9. Identidade, o novo perímetro

##### 9.1 Menor privilégio, escrito

**O que é**

Uma política concede o acesso estritamente necessário, e nada mais. A frase é
fácil e a prática é chata, porque escrever a permissão exata dá mais trabalho do
que conceder acesso amplo.

**Como funciona na prática**

Esta política permite ler apenas o prefixo `raw/` de um bucket, e listar apenas
esse prefixo:

<!-- verificacao: nivel 2, json valido com 2 statements, scripts/verificar_blocos.py, 2026-07-31 -->

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LerApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::empresa-data-lake/raw/*"
    },
    {
      "Sid": "ListarApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::empresa-data-lake",
      "Condition": {"StringLike": {"s3:prefix": ["raw/*"]}}
    }
  ]
}
```

Repare que são dois blocos com recursos diferentes. Ler objeto age sobre o
objeto, e o recurso termina em `/raw/*`. Listar age sobre o bucket, e o recurso é
o bucket, com a restrição de prefixo indo na condição. Confundir os dois é o
erro mais comum de quem escreve a primeira política, e o sintoma é uma listagem
que não funciona apesar de a leitura funcionar.

Este bloco foi validado como JSON. Isso prova a sintaxe, e não prova que a
política concede exatamente o que você quer: para isso é preciso testar contra a
conta, o que este módulo não faz.

**O equívoco comum**

Usar credencial de longa duração no código. Chave de acesso em repositório é a
origem clássica do incidente. A alternativa existe em toda nuvem: papel assumido
pelo serviço, sem chave escrita em lugar nenhum, e segredo em cofre gerenciado
quando a credencial for de terceiro.

##### 9.2 Criptografia

Dado em repouso e em trânsito cifrado é o padrão, não a exceção. O que costuma
faltar é a decisão sobre a chave: gerenciada pelo provedor resolve a maior parte
dos casos, e chave própria só se justifica quando há exigência regulatória ou de
auditoria que a peça por escrito.

#### 10. Rede, a VPC

**O que é**

A rede virtual privada isola seus recursos num espaço de endereços próprio, com
sub-redes públicas e privadas, e regras de firewall por recurso.

**Como funciona na prática**

Para engenharia de dados, três decisões cobrem quase tudo:

1. **Sub-rede privada para o que processa.** Quem transforma dado não precisa de
   endereço público. Se precisa sair para a internet, sai por um gateway
   controlado.
2. **Acesso privado ao object storage.** Um endpoint privado faz o tráfego para
   o storage não passar pela internet pública, o que ajuda em segurança e, em
   alguns casos, no custo de transferência.
3. **Regra de firewall por origem e porta.** A porta do banco aberta para o
   mundo é falha de configuração, e configuração é o seu lado do modelo de
   responsabilidade compartilhada.

**O equívoco comum**

Tratar rede como assunto de outra equipe. A conta de transferência de dados e a
lentidão inexplicável de um job frequentemente moram aqui, e quem lê a fatura é
quem toca o pipeline.

#### 11. FinOps, o custo é decisão de arquitetura

##### 11.1 O que responde pela fatura

**O que é**

Numa carga de dados, a maior parte do custo costuma vir de poucas decisões:

| Decisão | Efeito na fatura |
|---|---|
| Formato e particionamento do dado | Define quanto a query lê, e a query é cobrada por leitura |
| Classe de armazenamento e ciclo de vida | Define o preço por gigabyte e as multas de duração mínima |
| Recurso ligado sem uso | Paga hora parada, principalmente cluster e VM |
| Transferência de dados entre regiões e para fora | Cobrada por gigabyte, e não aparece até chegar |

O primeiro item é o mais importante e o menos citado. Melhorar o formato do dado
reduz o custo de toda query futura, e nenhuma negociação comercial faz isso.

##### 11.2 Os três modelos de preço

| Modelo | Como funciona | Bom para |
|---|---|---|
| Sob demanda | Paga pelo uso, sem compromisso | Carga nova ou irregular |
| Compromisso de uso | Desconto em troca de compromisso de prazo | Baseline previsível e medida |
| Capacidade interrompível | Desconto grande, o provedor pode retomar o recurso | Job tolerante a falha e reinício |

**O equívoco comum**

Assinar compromisso de uso antes de ter medida. O desconto é real e o
compromisso também: você paga o prazo inteiro mesmo que a carga caia. A ordem
certa é medir por alguns meses, achar o piso de consumo, e comprometer apenas o
piso.

##### 11.3 O que fazer antes de otimizar

Sem rótulo de custo por time e por projeto, otimização vira palpite. Rotular
recurso e ligar alerta de orçamento custa pouco tempo e é o que transforma "a
fatura subiu" em "a fatura subiu por causa disto".

#### 12. O mapa entre provedores

Três provedores dominam a infraestrutura de nuvem. Segundo dados da Synergy
Research Group para o primeiro trimestre de 2026, a AWS tinha 28 por cento do
mercado, a Microsoft Azure 21 por cento e o Google Cloud 14 por cento, num
mercado de 129 bilhões de dólares no trimestre.

O mesmo conceito muda de nome em cada nuvem. Esta tabela existe para você ler
uma arquitetura ou uma vaga sem travar no nome:

| Conceito | AWS | GCP | Azure |
|---|---|---|---|
| Object storage | S3 | Cloud Storage | Blob Storage |
| Data warehouse | Redshift | BigQuery | Synapse |
| Query sobre o lake | Athena | BigQuery | Synapse Serverless |
| Streaming gerenciado | Kinesis e MSK | Pub/Sub | Event Hubs |
| ETL gerenciado | Glue | Dataflow | Data Factory |
| Spark gerenciado | EMR | Dataproc | Synapse Spark |
| Airflow gerenciado | MWAA | Cloud Composer | Data Factory Managed Airflow |
| Função serverless | Lambda | Cloud Functions | Azure Functions |
| Container gerenciado | ECS e EKS | GKE | AKS |
| Identidade | IAM | IAM | Entra ID |
| Chaves | KMS | Cloud KMS | Key Vault |

**O equívoco comum**

Escolher provedor pelo catálogo. Os três atendem engenharia de dados com folga.
O que decide na prática é onde a empresa já está, qual contrato já existe, e
quem no time já sabe operar. Multi-nuvem evita dependência de fornecedor e
multiplica a complexidade operacional por dois ou três, o que raramente compensa
em time pequeno.

#### 13. Mão na massa sem gastar

Você não precisa de conta para ler o que um comando faz. A AWS CLI interpreta o
comando localmente, e dois recursos dela permitem conferir a sintaxe sem
credencial e sem chamada de rede.

**O esqueleto do comando** mostra a estrutura de entrada de uma operação de API:

<!-- verificacao: nivel 2, AWS CLI 2.25.5, codigo 0 sem credencial e sem rede, scripts/verificar_blocos.py, 2026-07-31 -->

```bash
aws s3api create-bucket --generate-cli-skeleton
aws athena start-query-execution --generate-cli-skeleton
```

**O modo de ensaio** mostra o que aconteceria, sem acontecer:

<!-- verificacao: nivel 2, AWS CLI 2.25.5, codigo 0 sem credencial e sem rede, scripts/verificar_blocos.py, 2026-07-31 -->

```bash
aws s3 cp vendas.parquet s3://empresa-data-lake/raw/vendas/ --dryrun
```

A saída é a linha `(dryrun) upload: ...`, e nada foi enviado.

Uma diferença que confunde: o modo de ensaio existe nos comandos de alto nível
`aws s3`, e não em todos. O `aws s3 mb` não aceita a opção, e a forma
verificável dele é o esqueleto do `aws s3api create-bucket`.

Para conferir tudo de uma vez, no diretório do módulo:

<!-- verificacao: nivel 3, execucao real do proprio script, codigo 0 com 7 checagens, 2026-07-31 -->

```bash
python3 scripts/verificar_blocos.py
```

Saída esperada: sete linhas começando com `OK` e a linha final
`7 checagem(ns), todas em nivel 2`.

#### 14. Exercícios e entregáveis

**Exercício 1: Classe de armazenamento por padrão de acesso**

Objetivo: escolher classe a partir do acesso, não da idade.

Contexto: quatro conjuntos do projeto de campanhas.

- Eventos crus do mês corrente, lidos várias vezes por dia pelo pipeline.
- Eventos crus de meses anteriores, lidos uma vez por mês no fechamento.
- Exportações para auditoria, lidas quase nunca, guardadas por sete anos.
- Arquivos de log de aplicação, milhões de objetos de poucos kilobytes cada.

Entregável: tabela com classe escolhida por conjunto, justificativa em uma
frase, e o que a escolha erraria se você decidisse apenas pela idade do dado.
O quarto item tem uma pegadinha, e ela está na seção 6.

**Exercício 2: Política de menor privilégio**

Objetivo: escrever permissão exata, não permissão que funciona.

Contexto: uma ferramenta de BI precisa ler apenas o prefixo `curated/` do bucket
do lake, e precisa listar esse prefixo para navegar.

Entregável: a política em JSON, validada com `python3 -m json.tool`, mais uma
frase explicando por que os dois blocos apontam para recursos diferentes.

**Exercício 3: De onde vem a fatura**

Objetivo: ligar decisão técnica a linha de custo.

Contexto: um pipeline que lê 2 TB de CSV não particionado por execução, roda de
hora em hora, e alimenta um painel consultado três vezes por dia.

Entregável: lista das três mudanças que mais reduziriam o custo, em ordem de
impacto, com a justificativa de cada uma. Diga também o que você mediria antes
de assinar qualquer compromisso de uso.

**Exercício 4: Tradução entre nuvens**

Objetivo: ler arquitetura sem travar no nome.

Contexto: uma descrição de vaga pede experiência com S3, Glue, Athena e MWAA.

Entregável: a mesma arquitetura escrita com os serviços equivalentes do GCP e do
Azure, mais uma observação sobre qual equivalência é a menos exata e por quê.

#### 15. Mini-desafio com solução

**Enunciado**

O time decidiu levar o pipeline de campanhas para a nuvem. O volume é de cerca
de 50 GB novos por mês em eventos de campanha. O pipeline roda de hora em hora,
o painel é consultado algumas dezenas de vezes por dia, e a auditoria exige
guardar o dado cru por cinco anos.

Proponha a arquitetura mínima e diga, para cada escolha, o que ela custa e o que
ela deixa de fora.

**Dicas**

- Comece pela pergunta de negócio, não pelo catálogo de serviços.
- Cinco anos de retenção e acesso diário são requisitos diferentes sobre o mesmo
  dado, e isso sugere mais de uma classe de armazenamento.
- O maior custo recorrente de um pipeline de query sobre lake não costuma ser o
  armazenamento.

**Gabarito comentado**

Armazenamento em duas faixas. O mês corrente em classe padrão, porque o pipeline
lê todo dia. O histórico movido por política de ciclo de vida para uma classe de
acesso infrequente, que tem duração mínima de 30 dias, prazo compatível com dado
que só será relido no fechamento. Para os cinco anos de auditoria, uma cópia em
arquivamento profundo, cuja duração mínima de 180 dias não é problema para dado
que ninguém pretende ler.

Formato e particionamento antes de qualquer serviço. Converter para Parquet e
particionar por data de evento é a decisão que mais reduz custo, porque ela
reduz o que **toda** query futura lê. Fazer isso depois de escolher a engine é a
ordem errada, ainda que funcione.

Query sobre o lake, não warehouse dedicado. Com 50 GB por mês e algumas dezenas
de consultas por dia, um warehouse dedicado cobra capacidade parada. Cobrança
por dado escaneado combina melhor com esse perfil, e a conta muda se o número de
consultas crescer uma ordem de grandeza.

Orquestração gerenciada. O Airflow que você já conhece, sem o servidor para
manter de pé. É a troca típica: paga mais por hora e não paga o custo de operar.

Identidade desde o primeiro dia. Um papel para o pipeline com escrita apenas nos
prefixos que ele produz, um papel para o BI com leitura apenas do curado.
Deixar isso para depois significa nunca fazer.

**O que a solução deixa de fora, e isso faz parte da resposta**

Não há alta disponibilidade entre regiões. A perda de uma região inteira
interrompe o pipeline, e a decisão é consciente: o custo de duplicar não se
justifica para um painel de marketing. Escrever isso é parte do entregável,
porque risco não declarado é risco assumido sem querer.

Também não há estimativa de custo em reais. Preço varia por região e muda sem
aviso, e este material não cita valor que não pôde ser conferido na data. O
caminho certo é a calculadora oficial do provedor, com os seus números.

**Interpretação**

A resposta fraca lista serviços. A resposta boa liga cada serviço a um requisito
e diz o que ficou de fora. Quem escreveu o parágrafo sobre o que a solução não
cobre entendeu o que este módulo ensina.

#### 16. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Trade-off da nuvem | Diz que nuvem é mais barata | Explica a troca entre investimento e consumo | Identifica quando o servidor próprio ainda ganha |
| Responsabilidade compartilhada | Assume que gerenciado é seguro | Sabe o que fica do seu lado | Aponta o próprio risco numa arquitetura concreta |
| Classe de armazenamento | Escolhe pela idade do dado | Escolhe pelo padrão de acesso | Antecipa duração mínima e tamanho mínimo faturável |
| IAM | Concede acesso amplo que funciona | Escreve menor privilégio correto | Explica a diferença entre recurso de objeto e de bucket |
| Custo | Trata custo como assunto financeiro | Liga decisão técnica a linha de fatura | Ordena as mudanças por impacto e diz o que mediria antes |
| Tradução entre nuvens | Trava fora da nuvem que conhece | Traduz os serviços principais | Aponta onde a equivalência é imperfeita |
| Honestidade técnica | Afirma número que não conferiu | Cita fonte e data | Declara explicitamente o que não foi verificado |

A última linha vale para todos os módulos, e é a que mais separa profissional de
entusiasta.

#### 17. Erros comuns e como corrigir

**Recurso que sumiu**

Sintoma: o bucket ou a instância não aparece no console nem na listagem.

Causa: você está em outra região. Regiões são isoladas e não replicam nada
automaticamente.

Correção: conferir a região selecionada antes de qualquer outra hipótese.

**A fatura de armazenamento subiu depois de uma política de ciclo de vida**

Sintoma: mover dado para classe fria aumentou o custo.

Causa: duração mínima ou tamanho mínimo faturável. Dado que gira antes do prazo
paga o prazo inteiro, e arquivo pequeno paga como se tivesse 128 KB.

Correção: comparar o tempo de vida real do objeto com a duração mínima da
classe, e consolidar arquivos pequenos antes de mover.

**A listagem falha, mas a leitura funciona**

Sintoma: a aplicação lê o objeto quando recebe o caminho, e falha ao listar.

Causa: a política concedeu `s3:GetObject` no prefixo e esqueceu `s3:ListBucket`
no bucket. São recursos diferentes.

Correção: dois blocos na política, como na seção 9.

**A query custa caro e ninguém sabe por quê**

Sintoma: o valor da consulta ao lake não cai mesmo com filtros.

Causa: o filtro não é de partição, ou o dado está em formato de linha. A
cobrança é por dado escaneado, e o filtro em coluna comum não evita a leitura.

Correção: particionar pela coluna que aparece no filtro e converter para formato
colunar. O módulo de particionamento e performance é o dono deste assunto.

**Credencial no repositório**

Sintoma: chave de acesso encontrada num commit.

Causa: uso de credencial de longa duração em vez de papel assumido pelo serviço.

Correção: revogar a chave imediatamente, migrar para papel, e mover o que sobrar
para um cofre de segredos. Trocar depois de vazar é obrigatório; o histórico do
Git guarda o valor antigo para sempre.

#### 18. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 1 e 3. Os dois cobram a mesma habilidade por ângulos
diferentes, que é ligar decisão técnica a consequência de custo.

**O que estudar em seguida, dentro da trilha**

O próximo módulo do bloco é infraestrutura como código, e ele responde à
pergunta que este deixa aberta: como esse ambiente nasce sem ninguém clicar em
console. Depois vêm processamento distribuído e Kubernetes, que tratam do
compute em escala.

Vale reler o módulo de particionamento e performance com a seção 11 desta
apostila na cabeça. O mesmo conteúdo lido depois de entender a cobrança por dado
escaneado tem outro peso.

**O que aprofundar por conta**

A calculadora de preço do seu provedor, com números do seu projeto. Uma hora
nela ensina mais sobre arquitetura de custo do que qualquer texto, inclusive
este.

**O que não perseguir agora**

Certificação. Ela cobra amplitude de catálogo, e você precisa de profundidade em
poucos serviços. Se for buscar uma, faça depois do capstone da trilha, não
antes.

#### 19. Glossário

| Termo | Significado |
|---|---|
| Classe de armazenamento | Faixa de preço e desempenho de um objeto no object storage |
| Compromisso de uso | Desconto concedido em troca de compromisso de consumo por prazo |
| Disponibilidade | Probabilidade de conseguir acessar o recurso num dado momento |
| Duração mínima | Prazo pelo qual a classe cobra, mesmo que o objeto seja apagado antes |
| Durabilidade | Probabilidade de o objeto continuar existindo |
| Elasticidade | Capacidade de aumentar e reduzir recurso conforme a carga |
| Endpoint privado | Acesso a um serviço sem passar pela internet pública |
| IaaS | Modelo em que o provedor entrega infraestrutura e você opera o resto |
| IAM | Serviço que define quem pode fazer o quê sobre qual recurso |
| Lakehouse | Arquitetura que une o armazenamento do lake à garantia do warehouse |
| Menor privilégio | Conceder apenas o acesso estritamente necessário |
| PaaS | Modelo em que o provedor opera a plataforma e você cuida da aplicação |
| Região | Área geográfica isolada, com várias zonas de disponibilidade |
| Responsabilidade compartilhada | Divisão de segurança entre provedor e cliente |
| Serverless | Modelo em que você entrega código e não gerencia servidor |
| Tamanho mínimo faturável | Tamanho pelo qual a classe cobra, mesmo em objeto menor |
| VPC | Rede virtual isolada onde seus recursos vivem |
| Zona de disponibilidade | Local isolado dentro de uma região |

#### Referências

Documentação oficial, consultada em 2026-07-31:

- Classes de armazenamento do Amazon S3: https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Modelo de responsabilidade compartilhada da AWS: https://aws.amazon.com/compliance/shared-responsibility-model/
- Infraestrutura global da AWS: https://aws.amazon.com/about-aws/global-infrastructure/
- Regiões e zonas de disponibilidade: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
- Preço do Amazon Athena: https://aws.amazon.com/athena/pricing/
- Preço do Google BigQuery: https://cloud.google.com/bigquery/pricing
- Referência da AWS CLI: https://docs.aws.amazon.com/cli/latest/reference/

Dados de mercado, consultados em 2026-07-31:

- Participação de mercado de nuvem no primeiro trimestre de 2026, com atribuição à Synergy Research Group: https://www.cloudzero.com/blog/cloud-service-providers/

#### Fontes verificadas (2026-07-31)

- A AWS declara 39 regiões lançadas e 123 zonas de disponibilidade, com cada
  região tendo pelo menos três zonas independentes e fisicamente separadas.
  https://aws.amazon.com/about-aws/global-infrastructure/
- Cada região é isolada das demais e os recursos não são replicados
  automaticamente entre regiões.
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
- No modelo de responsabilidade compartilhada, a AWS responde pela infraestrutura
  que roda os serviços, incluindo hardware, software, rede, instalações, sistema
  operacional do hospedeiro e camada de virtualização; o cliente responde pelo
  sistema operacional convidado, aplicação, configuração de security group,
  gestão e criptografia dos dados e permissões de IAM.
  https://aws.amazon.com/compliance/shared-responsibility-model/
- Todas as classes do S3 citadas na seção 6 são projetadas para durabilidade de
  99,999999999 por cento, exceto a Reduced Redundancy Storage, projetada para
  99,99 por cento e não recomendada pela própria AWS.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Disponibilidade projetada, zonas, duração mínima e tamanho mínimo faturável de
  cada classe são os da tabela comparativa da documentação: Standard 99,99 por
  cento sem mínimos; Standard-IA 99,9 por cento, 30 dias e 128 KB; One Zone-IA
  99,5 por cento em uma zona, 30 dias e 128 KB; Glacier Instant Retrieval 99,9
  por cento, 90 dias e 128 KB; Glacier Flexible Retrieval 90 dias; Glacier Deep
  Archive 180 dias.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Objetos com menos de 128 KB não são monitorados pelo Intelligent-Tiering e
  ficam sempre na camada de acesso frequente.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- A página de preço do Athena afirma que comprimir o arquivo e convertê-lo para
  um formato colunar como o Parquet permite ler apenas a coluna relevante,
  reduzindo o valor pago, e usa 5 dólares por terabyte como taxa ilustrativa do
  exemplo de cálculo. O preço por região não foi conferido nesta data e por isso
  não é afirmado aqui. https://aws.amazon.com/athena/pricing/
- Participação de mercado no primeiro trimestre de 2026, atribuída à Synergy
  Research Group: AWS 28 por cento, Microsoft Azure 21 por cento e Google Cloud
  14 por cento, num mercado de 129 bilhões de dólares no trimestre. Este é um
  número de pesquisa de mercado, não de documentação de fornecedor.
  https://www.cloudzero.com/blog/cloud-service-providers/
- Os blocos de SQL, a política em JSON e os comandos da AWS CLI desta apostila
  foram verificados em nível 2 por `scripts/verificar_blocos.py`, com sqlglot
  30.14.0 nos dialetos hive e trino e AWS CLI 2.25.5 em modo esqueleto e em modo
  de ensaio, sem credencial e sem chamada de rede. As sete checagens passaram e o
  script saiu com código 0 em 2026-07-31. Nenhum recurso de nuvem foi criado, e
  nenhuma query foi executada.

---

## Capitulo 10, Infraestrutura como codigo

Fonte: `modulos/infraestrutura-como-codigo/apostila.md`

### Apostila, infraestrutura como código para plataforma de dados

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

#### Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O problema do ambiente artesanal](#3-o-problema-do-ambiente-artesanal)
- [4. Os três princípios](#4-os-três-princípios)
- [5. O ecossistema, e o que cada ferramenta resolve](#5-o-ecossistema-e-o-que-cada-ferramenta-resolve)
- [6. Os blocos da linguagem](#6-os-blocos-da-linguagem)
- [7. State, o coração e o ponto de falha](#7-state-o-coração-e-o-ponto-de-falha)
- [8. Módulos e composição](#8-módulos-e-composição)
- [9. for_each e count, e por que a escolha importa](#9-for_each-e-count-e-por-que-a-escolha-importa)
- [10. Ambientes e raio de impacto](#10-ambientes-e-raio-de-impacto)
- [11. Segredo nunca entra no código](#11-segredo-nunca-entra-no-código)
- [12. Testes e a pirâmide que existe de verdade](#12-testes-e-a-pirâmide-que-existe-de-verdade)
- [13. O fluxo que tira o apply do terminal](#13-o-fluxo-que-tira-o-apply-do-terminal)
- [14. Laboratório](#14-laboratório)
- [15. Exercícios e entregáveis](#15-exercícios-e-entregáveis)
- [16. Mini-desafio com solução](#16-mini-desafio-com-solução)
- [17. Rubrica de validação da aprendizagem](#17-rubrica-de-validação-da-aprendizagem)
- [18. Erros comuns e como corrigir](#18-erros-comuns-e-como-corrigir)
- [19. Plano de continuidade](#19-plano-de-continuidade)
- [20. Glossário](#20-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

#### 0. Como usar esta apostila

**Leitura linear.** As seções 3 e 4 explicam por que a prática existe. Da 6 à 11
cada seção trata de uma decisão concreta. A 12 e a 13 são sobre operar, e são as
que mais separam quem escreveu Terraform uma vez de quem mantém uma plataforma.

**Revisão pontual.** State na 7, `for_each` na 9, segredo na 11, diagnóstico na
18.

**Pré-requisitos.** O módulo de cloud para dados. Este material assume que você
já sabe o que é bucket, classe de armazenamento, IAM e região. Aqui a pergunta é
como isso nasce sem ninguém clicar.

**O teto deste módulo é o nível 2 da escada de verificação, e isso é decisão.**
`terraform plan` e `terraform apply` mudam infraestrutura de verdade e custam
dinheiro de verdade. Eles são do operador humano ou do pipeline, e não entram em
laboratório de estudo. O que o laboratório prova está declarado no `lab.json`, e
o que ele não prova também.

**Versões.** Verificado com Terraform v1.15.8, TFLint v0.64.0 e provider
`hashicorp/aws` 6.57.1, em 2026-07-31.

#### 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** por que ambiente criado no console é dívida, em termos de risco e
   de tempo, sem recorrer a "é boa prática".
2. **Ler** um arquivo em HCL e dizer o que cada bloco faz.
3. **Escrever** um módulo com contrato claro: poucas variáveis, saídas úteis e
   validação declarada.
4. **Escolher** entre `for_each` e `count`, e prever o que acontece ao acrescentar
   um item no meio.
5. **Explicar** o que o state guarda, por que ele é sensível e o que o torna
   seguro.
6. **Ler** um plano de mudança e identificar o que vai ser destruído.
7. **Descrever** o fluxo em que ninguém aplica infraestrutura do próprio
   terminal, e por que isso não é burocracia.

#### 2. Contexto de negócio

A startup fictícia de marketing e e-commerce decidiu levar a plataforma para a
nuvem, e alguém fez isso pelo console. Funcionou.

Três meses depois, o problema apareceu de três formas ao mesmo tempo:

1. Pediram um ambiente de homologação igual ao de produção, e ninguém sabe o que
   exatamente existe em produção.
2. A fatura tem um bucket que ninguém reconhece, e o console não diz quem criou
   nem por quê.
3. A pessoa que montou o ambiente saiu, e o conhecimento saiu com ela.

Nenhum dos três é problema de nuvem. Os três são problema de **procedência**: não
existe registro de qual decisão criou cada recurso.

A pergunta deste módulo é: **como transformar o ambiente em artefato revisável,
reproduzível e auditável, sem que a criação de infraestrutura dependa da memória
de alguém.**

O que este módulo acrescenta ao projeto:

| Aspecto | Console | Código versionado |
|---|---|---|
| Recriar o ambiente | de memória, com divergência | do repositório, igual |
| Saber quem mudou o quê | log de auditoria da nuvem, sem o porquê | histórico do Git, com a justificativa |
| Revisão antes da mudança | conversa, quando acontece | pull request, sempre |
| Diferença entre ambientes | descoberta ao quebrar | visível no diff |

#### 3. O problema do ambiente artesanal

##### 3.1 O que o clique custa

**O que é**

Criar recurso pelo console é rápido e não deixa rastro de intenção. O resultado é
um ambiente que existe e que ninguém consegue descrever.

**O equívoco comum**

Achar que o problema é a criação. O problema é a **segunda** criação. O console
resolve bem a primeira vez, e falha quando alguém precisa de um ambiente igual,
ou de entender por que dois ambientes diferem.

**Como inspecionar**

O teste é uma pergunta: se este ambiente for perdido hoje, quanto tempo até
existir um idêntico? Se a resposta envolve alguém lembrando de algo, o ambiente é
artesanal.

##### 3.2 O repositório como descrição do ambiente

Quando o ambiente é código, o repositório para de ser documentação e passa a ser
a descrição real. A diferença é que documentação envelhece em silêncio, e código
que divergiu do real aparece na próxima execução.

Esse "aparecer" tem nome, e é o assunto da seção 7.

#### 4. Os três princípios

**Declarativo**

Você descreve o resultado, não o caminho. Não existe "crie o bucket, depois ligue
o versionamento": existe um bucket com versionamento ligado, e a ferramenta
descobre a ordem.

**Idempotente**

Aplicar duas vezes o mesmo código não cria duas vezes o mesmo recurso. A segunda
execução compara e não faz nada. Isso é o que permite que o código seja executado
com segurança por um pipeline.

**Imutável**

Mudança relevante substitui o recurso em vez de alterar o que está vivo. É o
mesmo princípio do Pod do módulo de Kubernetes, e a consequência prática é a
mesma: você precisa saber quais mudanças provocam substituição.

**A consequência que junta os três**

Ambiente descartável deixa de ser risco e vira estratégia. Se recriar é
confiável, testar em ambiente separado passa a ser barato.

**O equívoco comum**

Ler "imutável" como garantia de segurança. Substituir um bucket significa perder
o conteúdo dele. O princípio descreve o comportamento da ferramenta, e não
promete que ele é inofensivo.

#### 5. O ecossistema, e o que cada ferramenta resolve

**O que é**

Provisionar e configurar são camadas diferentes, e confundir as duas é a origem
de muita escolha errada.

| Ferramenta | Camada | Escopo |
|---|---|---|
| Terraform | provisionamento | multi-provedor, em linguagem própria |
| OpenTofu | provisionamento | fork do Terraform, sob licença MPL 2.0 |
| CloudFormation | provisionamento | um provedor só, integração profunda |
| Pulumi e CDK | provisionamento | em linguagem de programação de uso geral |
| Ansible | configuração | dentro da máquina, depois de ela existir |
| Crossplane | provisionamento | pela API do Kubernetes |

**Sobre a divisão do ecossistema**

O Terraform mudou de licença em 2023 e deixou de ser software livre no sentido
estrito. O OpenTofu nasceu como fork em resposta, e está sob a Mozilla Public
License 2.0.

A base de linguagem e de providers é comum, então migrar costuma ser direto. Como
os dois projetos evoluem em paralelo, a paridade não é permanente, e isso deve
entrar na decisão de quem começa um projeto novo hoje.

Esta apostila usa o Terraform porque é o que aparece com mais frequência em vaga
e em código existente. Quase tudo aqui vale para os dois.

**O que não conferi, e por isso não afirmo**

O deck da aula cita a data da aquisição da HashiCorp pela IBM, a versão exata em
que a licença mudou e o status do OpenTofu numa fundação. Não confirmei esses três
pontos em fonte oficial na data desta apostila, então eles não aparecem aqui como
fato. Se você for citá-los, confira antes.

#### 6. Os blocos da linguagem

**O que é**

Poucos blocos cobrem a maior parte do código. O resto é composição.

| Bloco | Papel |
|---|---|
| `terraform` | Versão exigida, providers e backend |
| `provider` | Região e opções do alvo |
| `resource` | Recurso gerenciado, criado e destruído pela ferramenta |
| `data` | Consulta de algo que já existe, sem assumir a gestão |
| `variable` | Entrada parametrizada, com tipo e validação |
| `output` | Valor exportado, para outro módulo ou para o operador |
| `locals` | Expressão nomeada, para não repetir cálculo |

**Como funciona na prática**

O bloco `terraform` do módulo do laboratório fixa duas coisas que evitam surpresa:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8 e provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

A restrição `~> 6.0` permite atualização dentro da linha 6 e recusa a 7. Sem
isso, o lançamento de um provider novo muda a sua infraestrutura sem nenhum
commit no seu repositório.

**A diferença entre `resource` e `data`**

`resource` é o que você passa a gerenciar: a ferramenta cria e, se você remover
do código, ela destrói. `data` é leitura de algo que continua sendo de outra
pessoa. Confundir os dois é como confundir `ref` com `source` no dbt, e o efeito
é igualmente concreto: você assume a gestão de algo que não é seu.

**Validação como parte do contrato**

O módulo do laboratório recusa um valor errado antes de qualquer chamada de API:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
variable "dias_para_acesso_infrequente" {
  type    = number
  default = 90

  validation {
    condition     = var.dias_para_acesso_infrequente >= 30
    error_message = "A duracao minima da classe de acesso infrequente e de 30 dias."
  }
}
```

Aquele 30 não é opinião. É a duração mínima cobrada pela classe de acesso
infrequente, do módulo de cloud para dados. O bloco `validation` transforma
conhecimento de custo em erro que a ferramenta emite.

**Atenção a um limite real, que o laboratório mostra.** Esse `validation` **não**
é avaliado pelo `terraform validate`. Ele roda no `plan`. No Lab 6 você põe o
valor 10 ali, roda o `validate`, e recebe `Success`. A rede de proteção existe, e
não é essa ferramenta que a aciona.

#### 7. State, o coração e o ponto de falha

##### 7.1 O que o state é

**O que é**

O state é o mapa entre o seu código e os recursos reais. Ele guarda o
identificador de cada recurso e os atributos conhecidos da última execução.

Sem state, a ferramenta não sabe se o bucket declarado no código é aquele que
existe na nuvem, ou se deve criar outro.

**Como funciona na prática**

A comparação que a ferramenta faz é de três pontas: o código diz o desejado, o
state diz o que ela criou, e a nuvem diz o que existe agora. O plano é a
diferença entre os três.

**O equívoco comum**

Tratar o state como arquivo temporário. Perder o state não apaga a
infraestrutura: apaga o conhecimento de que ela é sua. O próximo plano propõe
criar tudo de novo, e o que existe fica órfão.

##### 7.2 Backend remoto e trava

**O que é**

State em arquivo local não sobrevive à segunda pessoa do time. Backend remoto
guarda o state num lugar compartilhado e trava a execução concorrente.

A trava é o que impede dois `apply` simultâneos de corromperem o mapa. Sem ela, a
segunda execução escreve por cima do que a primeira ainda estava fazendo.

**Como funciona na prática**

No laboratório o bloco `backend` está comentado, e o comentário explica por quê:
o bucket de state precisa existir **antes** do código que o usa, então ele não
pode ser provisionado pelo mesmo código. Criar esse recurso à mão, uma única vez,
é uma das poucas exceções legítimas ao princípio deste módulo.

##### 7.3 O state guarda segredo em texto claro

**O que é**

Este é o ponto que mais gera incidente. A documentação da ferramenta é explícita:
ao desenvolver localmente, o state é um arquivo em texto plano, e ele inclui
qualquer valor secreto definido na configuração.

As recomendações oficiais são quatro: guardar o state remotamente, criptografá-lo
em repouso, restringir quem acessa, e manter log de auditoria de acesso.

**O equívoco comum**

Marcar uma saída como sensível e considerar o assunto resolvido. Isso esconde o
valor da tela, não do arquivo. Quem lê o state lê o valor.

**Como inspecionar**

O `.gitignore` do laboratório ignora `*.tfstate` e `terraform.tfvars`. Se algum
dia um desses arquivos aparecer num diff, o commit não deve ser feito, e o
segredo que estava nele precisa ser rotacionado.

##### 7.4 Drift

**O que é**

Drift é a divergência entre o que o código descreve e o que existe na nuvem,
criada por mudança manual.

O plano revela drift, e é essa a maior utilidade rotineira dele. Um plano que
propõe mudança sem que ninguém tenha mudado código significa que alguém mexeu no
console.

O conserto não é aplicar por cima sem pensar. As opções corretas estão no
runbook do operador: `import` para trazer ao código algo que existe fora dele,
`moved` para renomear sem destruir. Aplicar por cima é a terceira opção, e às
vezes a mudança manual era um conserto de emergência que ninguém documentou.

#### 8. Módulos e composição

**O que é**

Módulo é uma pasta com código reutilizável. É a unidade que evita copiar a mesma
infraestrutura em cada ambiente.

O contrato de um módulo são três arquivos: `main.tf` com os recursos,
`variables.tf` com as entradas e `outputs.tf` com as saídas.

**Como funciona na prática**

O módulo `camada-do-lake` do laboratório provisiona uma camada completa do data
lake: o bucket, o versionamento, a criptografia, o bloqueio de acesso público, a
política de ciclo de vida e o banco no catálogo.

Repare em duas escolhas que vêm direto do módulo de cloud para dados:

O bloqueio de acesso público é aplicado no nível do bucket, e não por permissão
individual. Fechar ali significa que uma configuração errada depois não consegue
abrir por acidente.

A política de ciclo de vida inclui uma regra que quase todo projeto esquece:

<!-- verificacao: nivel 2, terraform validate com provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
```

Envio interrompido no meio deixa pedaços que não aparecem na listagem e são
cobrados. É a linha mais barata do arquivo e a mais frequentemente ausente.

**A regra de ouro**

Módulo bom expõe poucas variáveis e esconde a complexidade. O `camada-do-lake`
expõe seis, e três têm valor padrão. Quem usa não precisa saber que existem seis
recursos lá dentro.

**Versionamento de módulo remoto**

Módulo de registro remoto precisa de versão fixa. Apontar para a branch
principal é aceitar que a sua infraestrutura mude quando outra pessoa fizer merge.

#### 9. for_each e count, e por que a escolha importa

**O que é**

Os dois criam vários recursos a partir de uma declaração. A diferença está em
como cada instância é identificada.

`count` identifica por índice numérico. `for_each` identifica por chave de um
mapa ou conjunto.

**Como funciona na prática**

O ambiente do laboratório instancia o módulo uma vez por camada:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
module "camada" {
  source   = "../../modulos/camada-do-lake"
  for_each = var.camadas

  nome_da_camada = each.key
  ambiente       = var.ambiente
}
```

**O equívoco comum, e ele é caro**

Usar `count` com lista para recurso nomeado. Suponha as camadas
`["bronze", "silver", "gold"]`, criadas com `count`. Elas viram os índices 0, 1 e
2. Agora acrescente `landing` no início da lista.

Com `count`, o índice 0 deixa de ser bronze e passa a ser landing, o 1 deixa de
ser silver e passa a ser bronze, e assim por diante. Do ponto de vista da
ferramenta, **todos** os recursos mudaram de identidade, e o plano propõe
destruir e recriar todos eles. Num data lake, isso é perder o conteúdo.

Com `for_each`, a chave é o nome. Acrescentar `landing` cria uma instância nova e
não toca nas outras.

A regra prática: `count` para ligar e desligar um recurso com condicional,
`for_each` para tudo que tem nome.

**Como inspecionar**

O plano mostra a diferença de forma inequívoca, com `-/+` nas instâncias que vão
ser recriadas. É a razão pela qual a seção 13 insiste em ler o plano.

#### 10. Ambientes e raio de impacto

**O que é**

Separar dev, homologação e produção é decisão de arquitetura, porque ela define
o quanto um erro alcança.

| Abordagem | Como funciona | Quando serve |
|---|---|---|
| Workspaces | Vários states no mesmo código | Experimento, ambiente descartável |
| Pastas por ambiente | State e variáveis isolados por pasta | O caminho mais comum em empresa |
| Ferramenta de orquestração | Reduz repetição e ordena stacks | Muitos ambientes ou muitas stacks |

O laboratório usa pastas. `ambientes/dev/` tem o próprio `main.tf` e o próprio
backend, e um erro ali não alcança outra pasta.

**Raio de impacto**

Quebrar o state por domínio, por exemplo rede, dados e aplicação, limita o dano
de um erro e deixa o plano rápido. State único gigante tem dois problemas: o
plano demora, e um erro alcança tudo.

**Sobre Terraform Stacks**

O deck da aula apresenta Stacks como modelo oficial para orquestrar várias
configurações. A documentação oficial descreve Stacks como uma camada da
plataforma gerenciada HCP Terraform, e afirma que não está disponível na edição
comunitária. Não encontrei confirmação da afirmação de disponibilidade geral no
CLI principal, então este material não a repete.

#### 11. Segredo nunca entra no código

**O que é**

Boa parte dos vazamentos de credencial nasce em repositório de infraestrutura, e
por um motivo simples: é o repositório que fala com tudo.

Três regras cobrem quase todos os casos:

1. **Nada de valor de segredo em arquivo versionado.** Nem em `tfvars`, nem em
   valor padrão de variável, nem em comentário.
2. **O segredo vem de um cofre.** A configuração busca o valor em tempo de
   execução, em vez de carregá-lo.
3. **A identidade não é uma chave.** No pipeline, o provider assume um papel. Não
   existe chave para vazar.

**Como funciona na prática**

O bloco `provider` do laboratório não tem nenhuma credencial:

<!-- verificacao: nivel 2, terraform validate com provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
provider "aws" {
  region = var.regiao

  default_tags {
    tags = local.etiquetas_do_ambiente
  }
}
```

O `default_tags` merece atenção por outro motivo. Ele aplica as etiquetas a todo
recurso do provider, e etiqueta é o que transforma "a fatura subiu" em "a fatura
subiu por causa deste time". É a contrapartida prática da seção de custo do
módulo de cloud para dados.

**O equívoco comum**

Confiar que apagar o commit resolve. O histórico do Git guarda o valor antigo. Um
segredo que apareceu num commit precisa ser rotacionado, não apagado.

#### 12. Testes e a pirâmide que existe de verdade

**O que é**

Infraestrutura tem pirâmide de testes, e a base dela é barata.

| Camada | O que verifica | Custo |
|---|---|---|
| `fmt` | Formatação | instantâneo |
| `validate` | Sintaxe e schema do provider | segundos |
| Linter | Regras de boa prática | segundos |
| Plano revisado | O que vai acontecer de verdade | minutos, e precisa de credencial |
| Teste com infraestrutura efêmera | Comportamento real | minutos ou horas, e custa dinheiro |
| Política como código | O que a revisão humana deixaria passar | integra ao pipeline |

**Como funciona na prática**

As três primeiras camadas são o que este módulo executa, e é o que o
`scripts/verificar_iac.py` faz num comando:

<!-- verificacao: nivel 3, execucao real do proprio script, codigo 0 com 6 checagens, 2026-07-31 -->

```
OK    terraform fmt, recursivo: codigo 0
OK    terraform init sem backend, ambientes/dev: codigo 0
OK    terraform validate, ambientes/dev: codigo 0
OK    terraform init sem backend, modulos/camada-do-lake: codigo 0
OK    terraform validate, modulos/camada-do-lake: codigo 0
OK    tflint, recursivo: codigo 0
6 checagem(ns), todas em nivel 2
```

**Por que o `init` é necessário, e por que ele é seguro aqui**

O `validate` sozinho confere sintaxe. Para conferir se um recurso aceita
determinado argumento, ele precisa do schema, que vem do provider. Sem `init`, o
Lab 5 passaria: trocar `status` por `statuss` num bloco só é detectado com o
provider baixado.

O `init` do laboratório roda com `-backend=false`. Ele baixa o provider do
registro público e não configura backend, não lê state e não fala com conta de
nuvem.

**Onde este módulo para, e por quê**

As três camadas de baixo da pirâmide são o teto desta trilha. `plan` e `apply`
são proibidos pelo guardrail do workspace, porque mudam infraestrutura real e
custam dinheiro real.

Isso é declarado no `lab.json` do módulo, com o motivo escrito, e o próprio script
recusa qualquer subcomando destrutivo por construção. Se alguém editar o arquivo e
acrescentar `plan`, a checagem falha em vez de executar.

**O que o gate não pega**

O Lab 6 existe para mostrar isso, e é o laboratório mais honesto do módulo. Um
valor que viola o bloco `validation` da própria variável passa pelo `validate` sem
erro, porque essa checagem acontece no `plan`.

Saber onde a rede de proteção termina vale tanto quanto saber que ela existe. Um
gate verde não significa que a infraestrutura está correta; significa que ela está
sintaticamente válida e bem formatada.

#### 13. O fluxo que tira o apply do terminal

**O que é**

O valor real da prática aparece quando ninguém aplica infraestrutura do próprio
terminal.

1. Você abre um pull request com a mudança de código.
2. O pipeline roda o gate de formatação, sintaxe e linter.
3. O pipeline roda o plano e publica o resultado no pull request.
4. Alguém revisa o código **e** o plano.
5. Depois do merge, o pipeline aplica.

**Como ler um plano**

| Símbolo | Significado |
|---|---|
| `+` | será criado |
| `~` | será alterado no lugar |
| `-/+` | será **destruído e recriado** |
| `-` | será destruído |

As duas últimas linhas são as que exigem atenção. Num bucket de data lake, `-/+`
significa perder o conteúdo, e a causa costuma ser a mudança de um atributo que o
provider trata como imutável, como o nome do bucket.

A regra é curta: **destroy inesperado no plano é aviso, nunca detalhe.** Se você
não sabe explicar por que aquele recurso está sendo recriado, não aprove.

**O equívoco comum**

Tratar o fluxo por pull request como burocracia. Sem ele não existe revisão, não
existe rastreio de quem mudou o quê e por quê, e não existe trava contra dois
`apply` simultâneos. Os três aparecem no primeiro incidente.

#### 14. Laboratório

O laboratório valida código de infraestrutura sem tocar nenhuma nuvem. Não
precisa de conta, não precisa de credencial e não custa nada.

Verificado com Terraform v1.15.8, TFLint v0.64.0 e provider `hashicorp/aws`
6.57.1. Os runbooks em `infrastructure/runbooks/` trazem o passo a passo.

##### Lab 0: Conferir as ferramentas

Pré-condição: Terraform 1.9 ou superior e TFLint 0.60 ou superior.

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
terraform version
tflint --version
```

##### Lab 1: Rodar o gate completo

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo
python3 scripts/verificar_iac.py
```

Saída esperada: seis linhas começando com `OK` e a linha final
`6 checagem(ns), todas em nivel 2`.

##### Lab 2: Rodar cada passo à mão

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
terraform fmt -check -recursive
cd ambientes/dev
terraform init -backend=false -input=false
terraform validate
```

Saída esperada: o `fmt` não imprime nada, e o `validate` responde
`Success! The configuration is valid.`

##### Lab 3: Quebrar a formatação

Acrescente espaços antes de um sinal de igual em
`modulos/camada-do-lake/main.tf` e rode o `fmt -check -recursive`.

Saída esperada: o caminho do arquivo impresso, com código de saída 3.

```
modulos/camada-do-lake/main.tf
```

Conserte com `terraform fmt -recursive`.

##### Lab 4: Quebrar uma referência

Troque `var.ambiente` por `var.ambient` em `ambientes/dev/main.tf` e rode o
`validate` na pasta do ambiente.

Saída esperada:

```
Error: Reference to undeclared input variable

  on main.tf line 53, in module "camada":
  53:   ambiente          = var.ambient

An input variable with the name "ambient" has not been declared. Did you mean
"ambiente"?
```

Desfaça a mudança.

##### Lab 5: Quebrar contra o schema do provider

Troque `status` por `statuss` dentro do bloco `versioning_configuration` em
`modulos/camada-do-lake/main.tf` e rode o `validate` na pasta do módulo.

Saída esperada:

```
Error: Missing required argument

  on main.tf line 34, in resource "aws_s3_bucket_versioning" "camada":
  34:   versioning_configuration {

The argument "status" is required, but no definition was found.
```

Este é o laboratório que justifica o `init`. Sem o provider baixado, a ferramenta
não sabe quais argumentos o recurso aceita, e o erro passaria. Desfaça a mudança.

##### Lab 6: Ver o que o gate não pega

Mude o default de `dias_para_acesso_infrequente` para 10 em
`modulos/camada-do-lake/variables.tf` e rode o `validate`.

Saída observada:

```
Success! The configuration is valid.
```

O valor viola o bloco `validation` da própria variável, que exige no mínimo 30
dias, e o `validate` aprova. Validação de variável é avaliada no `plan`, que está
fora do escopo deste módulo por regra do workspace.

Este é o laboratório mais importante da lista, porque ele mede a rede de
proteção em vez de confiar nela. Desfaça a mudança e rode o gate outra vez.

##### O que este laboratório não faz

Não roda `plan`, não roda `apply` e não roda `destroy`. Não cria recurso, não
consulta recurso existente e não usa credencial. O `lab.json` declara o teto de
nível 2 com o motivo escrito, e o script recusa subcomando destrutivo por
construção.

#### 15. Exercícios e entregáveis

**Exercício 1: for_each contra count**

Objetivo: entender o custo de identificar recurso por índice.

Contexto: as três camadas do laboratório.

Entregável: descreva por escrito o que aconteceria ao acrescentar uma camada
`landing` no **início** da lista, nos dois casos, e diga por que um deles é
aceitável e o outro não. Não é necessário rodar plano; a explicação é o
entregável.

**Exercício 2: uma camada nova**

Objetivo: usar o módulo sem alterá-lo.

Contexto: o time pediu uma camada `landing` com esfriamento agressivo, porque o
dado ali é descartado depois de processado.

Entregável: a camada acrescentada em `ambientes/dev/variables.tf`, com os prazos
escolhidos e justificados, e o gate de validação passando.

**Exercício 3: o módulo que falta**

Objetivo: escrever um módulo com contrato claro.

Contexto: além dos buckets, a plataforma precisa de um papel de acesso somente
leitura ao prefixo curado, para a ferramenta de BI. Você já escreveu essa
política no módulo de cloud para dados.

Entregável: um módulo novo com `main.tf`, `variables.tf` e `outputs.tf`,
consumindo as saídas do módulo de camada, e o gate passando. Exponha no máximo
quatro variáveis.

**Exercício 4: ler um plano**

Objetivo: identificar destruição antes de ela acontecer.

Contexto: procure um plano de Terraform público, num artigo ou numa
documentação, ou peça um ao mentor.

Entregável: a lista dos recursos que seriam destruídos ou recriados, a
justificativa de cada um, e a decisão de aprovar ou recusar, com o motivo.

#### 16. Mini-desafio com solução

**Enunciado**

O time quer que a política de ciclo de vida de produção seja diferente da de
desenvolvimento: em produção o dado bruto precisa ficar cinco anos, e o custo
importa mais. Em desenvolvimento o dado pode ser apagado em trinta dias.

Além disso, alguém quer poder impedir a destruição acidental dos buckets de
produção, sem duplicar o módulo.

Proponha uma solução e diga o que ela custa.

**Dicas**

- O módulo já recebe os prazos como variável, e o ambiente já é uma pasta.
- Existe um meta-argumento que impede a destruição de um recurso.
- Duplicar módulo por ambiente é a solução óbvia, e é a que o enunciado proíbe.

**Gabarito comentado**

Uma pasta `ambientes/prod/` com os próprios valores. O módulo não muda: ele já
recebe os prazos por variável, e é exatamente para isso que a variável existe.
Duplicar o módulo criaria duas definições da mesma camada, e elas divergiriam na
primeira correção aplicada em apenas uma.

Para os cinco anos de retenção, uma regra de expiração além das transições, com o
prazo em produção e um prazo curto em desenvolvimento. Vale conferir a duração
mínima da classe de destino antes de escolher o prazo, porque objeto apagado
antes dela é cobrado por ela.

Para a proteção contra destruição, o meta-argumento `lifecycle` com
`prevent_destroy`. Aqui está a parte que o enunciado esconde: no Terraform esse
valor precisa ser conhecido no momento da análise, e não aceita variável. Tentar
produz este erro, que foi observado de verdade:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, saida real, 2026-07-31 -->

```
Error: Variables not allowed

  on main.tf line 20, in resource "aws_s3_bucket" "teste":
  20:     prevent_destroy = var.proteger

Variables may not be used here.
```

Então a proteção não pode ser ligada por ambiente com a mesma abordagem das
outras diferenças. O deck da aula menciona que o OpenTofu passou a aceitar
`prevent_destroy` dinâmico por variável; não confirmei isso em fonte oficial
nesta data, e se você depender disso, confira na versão que for usar.

As saídas honestas são três, e escolher entre elas é o exercício:

1. Ligar `prevent_destroy` para todos os ambientes. Simples, e transforma cada
   remoção legítima em duas etapas, inclusive em desenvolvimento.
2. Aceitar a duplicação apenas desse bloco, com um recurso condicional. Resolve e
   acrescenta um caminho de código.
3. Não usar `prevent_destroy` e proteger por permissão: negar a exclusão do bucket
   de produção na política de IAM, fora do Terraform. É a única que protege
   também contra quem age pelo console.

A terceira é a que eu defenderia, e a razão é a do módulo de cloud para dados:
identidade é a camada que vale em todos os caminhos, e o Terraform é apenas um
deles.

**Interpretação**

A resposta fraca duplica o módulo. A resposta boa usa a variável que já existe e
percebe que o `prevent_destroy` não segue o mesmo padrão das outras diferenças.
Quem chegou à terceira alternativa entendeu que a proteção mais forte não está na
ferramenta de provisionamento.

#### 17. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Por que IaC existe | Diz que é boa prática | Explica procedência e reprodutibilidade | Usa o teste da segunda criação para avaliar um ambiente real |
| Blocos da linguagem | Copia de exemplo | Sabe o papel de cada bloco | Distingue `resource` de `data` e explica a consequência |
| State | Trata como arquivo temporário | Explica o mapa e a trava | Trata o state como dado sensível e sabe o que fazer se ele vazar |
| Módulo | Copia código entre ambientes | Escreve módulo com contrato | Módulo com poucas variáveis, validação e saídas úteis |
| for_each e count | Usa os dois sem critério | Escolhe `for_each` para o que tem nome | Explica o efeito de inserir item no meio de uma lista |
| Segredo | Deixa valor em tfvars | Usa cofre e papel assumido | Sabe que apagar o commit não resolve |
| Ler o plano | Aprova sem ler | Identifica criação e alteração | Recusa plano com destruição que não sabe explicar |
| Honestidade sobre o gate | Trata gate verde como garantia | Sabe o que cada ferramenta cobre | Sabe onde a proteção termina, como no Lab 6 |

#### 18. Erros comuns e como corrigir

**O `fmt -check` falha no pipeline e ninguém sabe por quê**

Sintoma: o pipeline recusa a mudança e imprime apenas um caminho de arquivo.

Causa: o arquivo não está no formato canônico. O código de saída é 3, não 1.

Correção: `terraform fmt -recursive` e commitar. Vale ligar isso num gancho de
pré-commit, porque é a falha mais boba de descobrir no pipeline.

**O `validate` aprova e o `plan` falha**

Sintoma: o gate passa e o plano do pipeline quebra.

Causa: são checagens diferentes. O `validate` confere sintaxe e schema; o `plan`
avalia expressão, valida variável e consulta a nuvem.

Correção: entender que o gate é a primeira porta, não a última. O Lab 6 mostra
exatamente um caso em que o `validate` aprova o que o `plan` recusaria.

**O `validate` reclama de provider não inicializado**

Sintoma: o comando pede `terraform init` antes de qualquer outra coisa.

Causa: sem `init`, não existe schema de provider para conferir.

Correção: `terraform init -backend=false`. A opção importa: sem ela, a ferramenta
tenta configurar o backend declarado, e num projeto real isso significa falar com
o bucket de state.

**O plano quer recriar tudo depois de uma mudança pequena**

Sintoma: uma inserção na lista de camadas produz destruição em massa.

Causa: `count` com lista. Os recursos são identificados por índice, e inserir no
meio muda a identidade de todos os seguintes.

Correção: `for_each` com mapa ou conjunto. Migrar exige o bloco `moved`, ou o
recurso é destruído no processo.

**O nome do bucket já existe**

Sintoma: a criação falha dizendo que o nome está em uso.

Causa: nome de bucket é único no mundo inteiro, não na sua conta.

Correção: prefixo próprio no nome. É por isso que o laboratório tem a variável
`prefixo_do_bucket`, com um valor de exemplo que precisa ser trocado.

**O state foi perdido**

Sintoma: o plano propõe criar tudo de novo, e a infraestrutura já existe.

Causa: state local apagado, ou backend trocado sem migração.

Correção: `import` recurso por recurso, o que é lento e chato. A prevenção é
backend remoto desde o primeiro dia, e é por isso que ele aparece no runbook do
operador.

**Alguém mexeu no console**

Sintoma: o plano propõe mudança sem que ninguém tenha alterado código.

Causa: drift.

Correção: entender **o que** foi mudado antes de decidir. `import` para trazer ao
código, `moved` para renomear sem destruir, ou aplicar por cima. A terceira
opção reescreve a mudança manual, e às vezes ela era um conserto de emergência.

#### 19. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 1 e 2. O primeiro é conceitual e o segundo prova que você
entendeu o contrato do módulo.

**O que estudar em seguida, dentro da trilha**

Este é o segundo módulo do bloco de nuvem e escala. Vêm depois processamento
distribuído e Kubernetes. Vale reler o módulo de Kubernetes com este na cabeça: o
manifesto declarativo e a reconciliação são a mesma ideia deste módulo, aplicada
ao cluster em vez da nuvem.

**O que aprofundar por conta**

Rode um `plan` no seu próprio ambiente, com a sua conta e a sua conta de custo. É
a parte que esta trilha não faz por decisão, e é onde se aprende mais. Comece com
um recurso barato e leia o plano inteiro antes de aplicar.

Depois, política como código. É o que bloqueia no pipeline o que a revisão humana
deixaria passar, e ela existe justamente porque revisão humana cansa.

**O que não perseguir agora**

Escrever provider próprio, e migrar tudo para uma ferramenta em linguagem de
programação de uso geral. Os dois são decisões grandes, e nenhuma delas melhora o
seu dia enquanto o fluxo por pull request não existir.

#### 20. Glossário

| Termo | Significado |
|---|---|
| Backend | Onde o state é guardado, local ou remoto |
| `count` | Meta-argumento que repete recurso por índice numérico |
| `data` | Bloco que consulta recurso existente, sem assumir a gestão |
| Declarativo | Descrever o resultado, não o passo a passo |
| Drift | Divergência entre o código e o que existe de fato |
| `for_each` | Meta-argumento que repete recurso por chave estável |
| HCL | Linguagem de configuração do Terraform |
| Idempotente | Aplicar duas vezes produz o mesmo resultado que aplicar uma |
| `import` | Trazer para o state um recurso que já existe |
| `lifecycle` | Meta-argumento que altera o comportamento de criação e destruição |
| Lock | Trava que impede duas execuções simultâneas sobre o mesmo state |
| Módulo | Pasta com código reutilizável, com entradas e saídas |
| `moved` | Bloco que renomeia um recurso no código sem destruí-lo |
| Plano | Diferença entre o desejado, o state e o real |
| `prevent_destroy` | Opção que recusa a destruição de um recurso |
| Provider | Plugin que traduz a configuração em chamadas de API |
| Raio de impacto | Quanto da infraestrutura um erro alcança |
| `resource` | Bloco que declara recurso gerenciado pela ferramenta |
| State | Mapa entre o código e os recursos reais |
| `validation` | Bloco que recusa valor inválido de variável, avaliado no plano |

#### Referências

Documentação oficial, consultada em 2026-07-31:

- Dado sensível no state: https://developer.hashicorp.com/terraform/language/state/sensitive-data
- Terraform Stacks: https://developer.hashicorp.com/terraform/language/stacks
- Repositório do OpenTofu: https://github.com/opentofu/opentofu
- TFLint: https://github.com/terraform-linters/tflint

Referência do módulo de cloud para dados, para as durações mínimas das classes de
armazenamento citadas nas validações:

- Classes de armazenamento do Amazon S3: https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html

#### Fontes verificadas (2026-07-31)

- A documentação oficial afirma que, ao desenvolver localmente, o Terraform
  guarda o state num arquivo em texto plano que inclui qualquer valor secreto
  definido na configuração, e recomenda guardar o state remotamente,
  criptografá-lo em repouso, restringir o acesso e manter log de auditoria.
  https://developer.hashicorp.com/terraform/language/state/sensitive-data
- O Terraform Stacks é descrito pela documentação oficial como uma camada de
  configuração do HCP Terraform, e a mesma página afirma que não está disponível
  para a edição comunitária. A afirmação do deck de que Stacks está em
  disponibilidade geral no CLI principal não foi confirmada nesta data, e por
  isso não é repetida nesta apostila.
  https://developer.hashicorp.com/terraform/language/stacks
- O OpenTofu está sob a Mozilla Public License 2.0.
  https://github.com/opentofu/opentofu
- A duração mínima de 30 dias da classe de acesso infrequente e de 180 dias da
  classe de arquivamento profundo, usadas nos blocos `validation` do módulo, vêm
  da tabela comparativa de classes do S3.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- O código Terraform deste módulo foi verificado em nível 2 com Terraform
  v1.15.8, TFLint v0.64.0 com o conjunto de regras `terraform` 0.15.0 embutido, e
  provider `hashicorp/aws` 6.57.1. As seis checagens do
  `scripts/verificar_iac.py` passaram com código 0 em 2026-07-31. Nenhum recurso
  foi criado, nenhum plano foi gerado e nenhuma credencial foi usada.
- O teto de nível 2 é regra do workspace, não limitação técnica: `terraform plan`
  e `terraform apply` não são executados por esta trilha nem por este script, que
  recusa subcomando destrutivo por construção.
- A saída `Success! The configuration is valid.` para um valor que viola o bloco
  `validation` da variável foi observada de verdade em 2026-07-31, com
  `dias_para_acesso_infrequente` igual a 10. É a origem do Lab 6 e do limite
  declarado no `lab.json`.
- O `prevent_destroy` do bloco `lifecycle` não aceita variável no Terraform
  v1.15.8. O erro `Variables not allowed`, seguido de
  `Unsuitable value: value must be known`, foi obtido em execução real de
  `terraform validate` em 2026-07-31.
- As afirmações do deck sobre a data da aquisição da HashiCorp pela IBM, a versão
  exata da mudança de licença do Terraform, a filiação do OpenTofu a uma fundação
  e o `prevent_destroy` dinâmico do OpenTofu não foram confirmadas em fonte
  oficial nesta data, e por isso não aparecem nesta apostila como fato.

---

## Capitulo 11, Streaming com Apache Kafka

Fonte: `modulos/streaming-kafka/apostila.md`

### Apostila, Streaming com Apache Kafka

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto com Paulo Shindi.

#### Sumario

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagogico](#1-objetivo-pedagogico)
- [2. Contexto de negocio](#2-contexto-de-negocio)
- [3. O log particionado](#3-o-log-particionado)
- [4. Chave, particao e ordem](#4-chave-particao-e-ordem)
- [5. Grupo de consumo e offset](#5-grupo-de-consumo-e-offset)
- [6. Semanticas de entrega](#6-semanticas-de-entrega)
- [7. Laboratorio](#7-laboratorio)
- [8. Exercicios e entregaveis](#8-exercicios-e-entregaveis)
- [9. Mini-desafio com solucao](#9-mini-desafio-com-solucao)
- [10. Rubrica de validacao da aprendizagem](#10-rubrica-de-validacao-da-aprendizagem)
- [11. Erros comuns e como corrigir](#11-erros-comuns-e-como-corrigir)
- [12. Plano de continuidade](#12-plano-de-continuidade)
- [13. Glossario](#13-glossario)
- [Referencias](#referencias)
- [Fontes verificadas](#fontes-verificadas)

#### 0. Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

O laboratorio da secao 7 foi executado de ponta a ponta e as saidas registradas sao reais, nao
ilustrativas. Cada `Lab N` existe no `lab.json` deste modulo, com o comando e a saida esperada.

Pre-requisito: o modulo de Docker e ambiente local. Voce precisa conseguir subir um Compose.

#### 1. Objetivo pedagogico

Ao terminar este modulo voce consegue:

- explicar por que o Kafka e um log particionado e nao uma fila;
- prever em qual particao uma mensagem vai cair, a partir da chave;
- dizer o que o Kafka garante sobre ordem, e o que ele nao garante;
- ler o offset de um grupo de consumo e interpretar o lag;
- escolher a semantica de entrega adequada, sabendo onde a garantia termina.

#### 2. Contexto de negocio

A startup de marketing do Projeto 1 acompanha campanhas pagas. Ate aqui o pipeline era batch:
o dado chegava de hora em hora e o relatorio fechava no dia seguinte.

Surgiu uma pergunta que o batch nao responde: quando uma campanha comeca a queimar orcamento
sem converter, quanto tempo o time leva para perceber? Com carga de hora em hora, ate uma hora.
Com o orcamento diario de uma campanha grande, uma hora e dinheiro.

Streaming entra aqui para reduzir a latencia entre o evento acontecer e alguem poder agir. Nao
para substituir o batch, que continua fazendo o fechamento correto.

#### 3. O log particionado

**O que e**

Um topico do Kafka nao e uma fila. E um **log**: uma sequencia de registros que so cresce no
fim, dividida em particoes, e da qual ninguem remove nada ao ler.

Essa diferenca muda tudo. Numa fila, ler consome. No Kafka, ler apenas move um marcador de
posicao, e o mesmo registro pode ser lido de novo, por outro consumidor ou pelo mesmo mais tarde.

**Por que particionar**

A particao e a unidade de paralelismo. Um topico com 3 particoes pode ser lido por ate 3
consumidores do mesmo grupo em paralelo. Com 1 particao, so um consumidor trabalha, por mais
que voce suba dez.

**O que o Lab 3 mostra**

Ao descrever o topico, cada particao aparece com um `Leader`. O lider e o broker responsavel
por aquela particao: toda escrita e leitura passa por ele. Em cluster de um no so, o lider e
sempre o mesmo, e por isso o laboratorio nao demonstra failover.

#### 4. Chave, particao e ordem

**A regra**

Quando a mensagem tem chave, o Kafka escolhe a particao por hash da chave. Mesma chave, mesma
particao, sempre. Sem chave, a distribuicao e circular entre as particoes.

**O que isso garante**

Ordem **dentro da particao**, e so. O Kafka nao garante ordem global no topico, e nao tem como:
particoes sao independentes e escritas em paralelo.

Na pratica isso e suficiente quase sempre, porque o que importa e a ordem dos eventos **do
mesmo titular**. Se todos os eventos do usuario `u1` caem na mesma particao, a sequencia
`click`, depois `purchase`, chega nessa ordem.

**O equivoco comum**

Achar que aumentar particoes so melhora. Aumentar particoes aumenta paralelismo e **redistribui
as chaves**: uma chave que caia na particao 1 com 3 particoes pode cair na 4 com 6. Eventos
antigos ficam onde estavam, e a ordem por chave se quebra na fronteira da mudanca.

Por isso o numero de particoes e decisao de projeto, nao de ajuste fino.

**O que o Lab 5 mostra**

A saida real do laboratorio:

```
Partition:0	u2	{"user_id":"u2","evento":"view"}
Partition:1	u1	{"user_id":"u1","evento":"click"}
Partition:1	u1	{"user_id":"u1","evento":"purchase"}
```

As duas mensagens de `u1` cairam na particao 1, e nessa ordem. A de `u2` foi para a 0. A regra
de hash da chave nao e teoria, esta ali.

#### 5. Grupo de consumo e offset

**O que e um grupo**

Consumidores que compartilham o mesmo `group.id` dividem as particoes entre si. Cada particao
e lida por exatamente um membro do grupo, o que da paralelismo sem duplicar processamento.

Consumidores de grupos diferentes leem o mesmo topico de forma independente. E por isso que o
mesmo fluxo alimenta o time de analytics e o de operacoes sem um atrapalhar o outro.

**Offset**

O offset e a posicao do grupo em cada particao. Ele fica guardado no proprio Kafka, num topico
interno, e nao no consumidor. Se o consumidor morre e volta, retoma de onde parou.

**Lag**

Lag e a diferenca entre o fim do log e a posicao do grupo. Lag zero significa que o grupo leu
tudo. Lag crescendo significa que a producao esta mais rapida que o consumo, e e a metrica que
merece alerta.

**O que o Lab 6 mostra**

```
GROUP           TOPIC         PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
time-analytics  eventos-mkt   0          1               1               0
time-analytics  eventos-mkt   1          2               2               0
```

O grupo commitou 1 mensagem na particao 0 e 2 na particao 1, que e exatamente a distribuicao
observada no Lab 5. Lag zero nas duas.

Repare que a particao 2 nao aparece: nenhuma mensagem caiu nela, entao o grupo nao tem offset
commitado ali.

#### 6. Semanticas de entrega

| Semantica | O que garante | Custo |
|---|---|---|
| At-most-once | Nunca duplica, pode perder | Commit antes de processar |
| At-least-once | Nunca perde, pode duplicar | Commit depois de processar |
| Exactly-once | Cada evento uma vez, **dentro do Kafka** | Producer idempotente e transacao |

**Onde a garantia termina**

O exactly-once do Kafka e `read-process-write`: consumir de um topico, processar, produzir em
outro e commitar o offset, tudo ou nada. E atomico **dentro do Kafka**.

Seu S3, seu Postgres e sua tabela Iceberg nao participam dessa transacao. No instante em que o
dado atravessa essa borda, voce voltou para at-least-once.

Na pratica, o caminho mais simples e mais barato e assumir at-least-once e tornar a duplicata
inofensiva no destino, com chave de negocio explicita e escrita idempotente.

**CDC nao mora aqui**

Change Data Capture aparece com frequencia junto de Kafka, via Debezium. O **conceito** de CDC
pertence ao modulo `cdc`, que cobre captura log-based sem broker. Este modulo trata apenas do
**transporte**: como o evento de mudanca viaja pelo Kafka depois de capturado.

#### 7. Laboratorio

Todos os passos abaixo foram executados em 2026-07-30 e as saidas sao reais. O manifesto
`lab.json` deste modulo registra comando e saida esperada de cada um.

Antes de comecar, leia `infrastructure/runbooks/00_pre_requisitos.md`.

- **Lab 1**, subir a stack do Kafka
- **Lab 2**, criar o topico com 3 particoes
- **Lab 3**, inspecionar particoes e lider
- **Lab 4**, produzir eventos com chave
- **Lab 5**, consumir e observar a particao de cada chave
- **Lab 6**, inspecionar offset do grupo de consumo
- **Lab 7**, derrubar a stack

Os scripts Python em `scripts/producers/` e `scripts/consumers/` cobrem os mesmos conceitos com
a biblioteca cliente, para quem quiser ir alem do CLI.

#### 8. Exercicios e entregaveis

**Exercicio 1: prever a particao**

Objetivo: aplicar a regra de hash da chave.

Contexto: o topico `eventos-mkt` tem 3 particoes. Voce vai produzir eventos das chaves `u1`,
`u2`, `u3` e `u4`.

Entregavel: antes de rodar, escreva sua previsao de qual chave cai em qual particao. Depois
rode o Lab 4 e o Lab 5 com essas chaves e compare. Explique os acertos e os erros.

---

**Exercicio 2: o efeito de mudar particoes**

Objetivo: entender por que o numero de particoes e decisao de projeto.

Contexto: partindo do topico com 3 particoes ja populado, aumente para 6 com
`kafka-topics.sh --alter --partitions 6`.

Entregavel: produza de novo as mesmas chaves, consuma tudo desde o inicio e mostre uma chave
cujos eventos ficaram divididos entre duas particoes. Explique o impacto na ordem.

---

**Exercicio 3: lag sob pressao**

Objetivo: ler o lag como metrica operacional.

Contexto: produza 1000 eventos e consuma com um unico consumidor lento, com pausa artificial
entre mensagens.

Entregavel: tabela com o lag medido em tres momentos, e uma frase dizendo o que voce alertaria
em producao e a partir de qual limiar.

---

**Exercicio 4: escolher a semantica**

Objetivo: decidir com criterio, nao por reflexo.

Contexto: dois casos. O primeiro contabiliza cliques para cobranca de anunciante. O segundo
atualiza um painel de monitoramento que refaz o calculo a cada minuto.

Entregavel: para cada caso, a semantica escolhida, a justificativa e o que precisa existir no
destino para que a escolha se sustente.

#### 9. Mini-desafio com solucao

**Enunciado**

O time de operacoes reclama que o painel mostra o evento de `purchase` de um usuario **antes**
do `click` que o originou. Os dois eventos sao produzidos pelo mesmo servico, na ordem certa,
para o mesmo topico. O topico tem 6 particoes.

Por que isso acontece, e como corrigir sem mudar o numero de particoes?

**Dicas antes do gabarito**

- O Kafka garante ordem em que escopo?
- O que decide a particao de uma mensagem?
- O produtor esta enviando chave?

**Gabarito comentado**

Os eventos estao sendo produzidos **sem chave**. Sem chave, o Kafka distribui de forma circular
entre as 6 particoes, entao `click` e `purchase` do mesmo usuario caem em particoes diferentes.

Particoes sao lidas em paralelo e independentes entre si. O Kafka garante ordem **apenas dentro
da particao**, entao nada impede o consumidor de processar a particao que tem o `purchase`
antes da que tem o `click`. Nao ha bug: e o comportamento correto de um log particionado.

A correcao e produzir com `user_id` como chave. A partir dai, todos os eventos do mesmo usuario
caem na mesma particao e chegam na ordem em que foram produzidos.

Cuidado ao aplicar: a correcao vale para os eventos **novos**. Os que ja estao no topico
continuam onde foram gravados, e a ordem so se restabelece na janela posterior a mudanca.

#### 10. Rubrica de validacao da aprendizagem

| Criterio | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Ordem | Diz que o Kafka garante ordem | Diz que garante dentro da particao | Explica por que ordem global e impossivel com particoes paralelas |
| Chave | Nao relaciona chave e particao | Sabe que a chave decide a particao | Antecipa o efeito de mudar o numero de particoes sobre a ordem |
| Offset | Confunde offset com posicao do consumidor | Sabe que o offset e do grupo e vive no Kafka | Interpreta lag como sinal operacional e propoe limiar |
| Semantica | Escolhe exactly-once por reflexo | Escolhe com base no caso | Aponta onde a garantia termina e o que fazer no destino |
| Laboratorio | Nao roda | Reproduz os labs | Modifica o cenario e explica a saida diferente |

#### 11. Erros comuns e como corrigir

| Sintoma | Causa | Correcao |
|---|---|---|
| Eventos do mesmo usuario fora de ordem | Produzir sem chave | Usar a chave de negocio como chave da mensagem |
| Subir varios consumidores e so um trabalhar | Mais consumidores que particoes no grupo | Aumentar particoes no projeto, ou aceitar o teto |
| Consumidor nao ve mensagem antiga | Grupo novo comeca do fim por padrao | Usar `--from-beginning` ou configurar `auto.offset.reset` |
| Script no host nao conecta | Listener anunciado errado | Conferir `KAFKA_ADVERTISED_LISTENERS`, o EXTERNAL precisa anunciar `localhost:9092` |
| Lag cresce sem parar | Consumo mais lento que producao | Paralelizar por particao ou otimizar o processamento |
| Reprocessar duplica no destino | Confiar no exactly-once atravessando a borda | Escrita idempotente com chave de negocio no destino |

#### 12. Plano de continuidade

Proximo passo natural na trilha e o modulo `kubernetes`, que cobre como esse tipo de servico
roda em producao com limite de recurso e reinicio controlado.

Para aprofundar o assunto deste modulo: `cdc`, que e o dono do conceito de Change Data Capture,
e trata da captura que muitas vezes alimenta um topico como este.

#### 13. Glossario

| Termo | Significado |
|---|---|
| Broker | Servidor que armazena e serve as particoes |
| Topico | Nome logico do log, dividido em particoes |
| Particao | Unidade de paralelismo e de ordem, um log que so cresce no fim |
| Offset | Posicao de um grupo dentro de uma particao |
| Grupo de consumo | Conjunto de consumidores que divide as particoes entre si |
| Lag | Distancia entre o fim do log e a posicao do grupo |
| KRaft | Modo de consenso do Kafka que dispensa o ZooKeeper |
| Listener | Endereco e protocolo pelo qual o broker aceita conexao |

#### Referencias

- Documentacao do Apache Kafka, secao de design e de consumidores. https://kafka.apache.org/documentation/
- Imagem oficial `apache/kafka` no Docker Hub. https://hub.docker.com/r/apache/kafka

#### Fontes verificadas

Verificado em 2026-07-30, com Kafka 3.9.0 em modo KRaft, via Docker Compose 2.39.1.

- A saida de particao por chave da secao 4 e a execucao real do Lab 5 neste ambiente.
- A tabela de offset e lag da secao 5 e a execucao real do Lab 6 neste ambiente.
- As imagens `apache/kafka:3.9.0` e `provectuslabs/kafka-ui:v0.7.2` foram confirmadas no
  registry com `docker manifest inspect` na mesma data.
- O manifesto `lab.json` deste modulo registra nivel 3 para os sete laboratorios.

---

## Capitulo 12, Kubernetes para engenharia de dados

Fonte: `modulos/kubernetes/apostila.md`

### Apostila, Kubernetes para engenharia de dados

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

#### Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O problema que o Kubernetes resolve](#3-o-problema-que-o-kubernetes-resolve)
- [4. Arquitetura do cluster](#4-arquitetura-do-cluster)
- [5. Pod, a unidade de execução](#5-pod-a-unidade-de-execução)
- [6. Workloads, quem gerencia os Pods](#6-workloads-quem-gerencia-os-pods)
- [7. Configuração e segredo](#7-configuração-e-segredo)
- [8. Rede, do Service ao que entra no cluster](#8-rede-do-service-ao-que-entra-no-cluster)
- [9. Recursos, limites e QoS](#9-recursos-limites-e-qos)
- [10. Agendamento, onde o Pod roda](#10-agendamento-onde-o-pod-roda)
- [11. Escalonamento](#11-escalonamento)
- [12. Segurança](#12-segurança)
- [13. Kubernetes na engenharia de dados](#13-kubernetes-na-engenharia-de-dados)
- [14. Laboratório](#14-laboratório)
- [15. Exercícios e entregáveis](#15-exercícios-e-entregáveis)
- [16. Mini-desafio com solução](#16-mini-desafio-com-solução)
- [17. Rubrica de validação da aprendizagem](#17-rubrica-de-validação-da-aprendizagem)
- [18. Erros comuns e como corrigir](#18-erros-comuns-e-como-corrigir)
- [19. Plano de continuidade](#19-plano-de-continuidade)
- [20. Glossário](#20-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

#### 0. Como usar esta apostila

**Leitura linear.** As seções 3 a 6 constroem o modelo mental, e sem elas o
resto vira decoreba de YAML. Da 7 à 12 cada seção trata de uma decisão concreta.
A 13 é o recorte de engenharia de dados, e é onde tudo se junta.

**Revisão pontual.** Se você já opera Kubernetes e veio atrás de um assunto:
recursos e QoS na 9, agendamento na 10, segurança na 12, diagnóstico na 18.

**Pré-requisitos.** O módulo de Docker e ambiente local. Você precisa saber o
que é uma imagem, o que é um container e por que a imagem é imutável. Não
precisa de cluster no trabalho, e não precisa de nuvem.

**O laboratório é o centro deste módulo.** Kubernetes é conceito simples com
consequência não óbvia, e a única forma de fixar é ver o cluster reagir. A seção
14 tem oito laboratórios, todos executados de verdade, com saída capturada.

**Versões.** Tudo foi verificado com Kubernetes v1.36.1 no cluster, kind v0.32.0
e kubectl v1.36.3, em 2026-07-31. Onde a versão muda o comportamento, a apostila
diz qual.

#### 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** o modelo de estado desejado e por que ninguém "sobe" um Pod.
2. **Ler** um manifesto e dizer o que cada bloco faz, sem copiar de exemplo.
3. **Escolher** entre Deployment, StatefulSet, DaemonSet e Job para uma carga de
   dados, e justificar.
4. **Definir** requests e limits de uma tarefa, prever a classe de QoS
   resultante e o que acontece sob pressão de memória.
5. **Diagnosticar** as quatro assinaturas de falha mais comuns a partir do que o
   cluster mostra, sem tentativa e erro.
6. **Relacionar** o Kubernetes ao Airflow que você já conhece, entendendo o que
   o executor faz por baixo.

#### 2. Contexto de negócio

A startup fictícia de marketing e e-commerce chegou aqui com um pipeline que
funciona e um problema novo.

O Airflow orquestra tarefas de ingestão, transformação e carga. Cada tarefa tem
dependências próprias: uma precisa de uma biblioteca de scraping, outra de um
cliente de banco, outra de uma versão específica de uma biblioteca de dados. Com
tudo rodando no mesmo processo, atualizar a dependência de uma tarefa quebra
outra. O time já perdeu uma manhã por causa disso.

Existe também o problema do custo. A carga é irregular: quase nada durante o
dia, um pico grande na madrugada. A máquina precisa ser dimensionada para o
pico, e fica parada o resto do tempo.

A pergunta deste módulo é: **como dar a cada tarefa o seu próprio ambiente e a
sua própria fatia de máquina, sem manter servidor ocioso e sem que uma tarefa
contamine a outra.**

O que este módulo acrescenta:

| Aspecto | Como estava | Com Kubernetes |
|---|---|---|
| Dependências | Compartilhadas, conflito entre tarefas | Uma imagem por tarefa |
| Capacidade | Dimensionada para o pico, ociosa o resto | Alocada por tarefa e devolvida |
| Falha de uma tarefa | Pode derrubar o processo | Isolada no próprio Pod |
| Recuperação | Alguém percebe e reinicia | Reconciliação contínua |

#### 3. O problema que o Kubernetes resolve

##### 3.1 O que o container não resolve

**O que é**

O container resolveu empacotar: a aplicação e suas dependências viajam juntas e
rodam igual em qualquer lugar. Ele não resolveu operar dezenas ou centenas
deles.

Falta escolher em qual máquina cada container roda, reiniciar o que morreu,
substituir sem derrubar o serviço, dar endereço estável ao que muda de lugar e
distribuir capacidade entre cargas que competem.

**O equívoco comum**

Achar que Kubernetes é "Docker em escala". Ele é um sistema de reconciliação
que por acaso executa containers. Entender isso muda o modo de pensar: você não
manda executar, você declara o que quer existir.

##### 3.2 Estado desejado e reconciliação

**O que é**

Você escreve o resultado que quer. O cluster compara continuamente o estado real
com o desejado e age para reduzir a diferença. Esse laço nunca termina.

**Como funciona na prática**

No Lab 2 você apaga um Pod à mão. Ninguém manda criar outro, e outro aparece:

```
NAME                                   READY   STATUS    RESTARTS   AGE
servico-de-consulta-7d69958dfb-65j9q   1/1     Running   0          9s
servico-de-consulta-7d69958dfb-f7mlm   1/1     Running   0          3m13s
servico-de-consulta-7d69958dfb-kddqw   1/1     Running   0          3m40s
```

O Pod de 9 segundos é o substituto. O controller do Deployment viu que existiam
menos réplicas do que o declarado e criou a diferença.

**O equívoco comum**

Tentar consertar o cluster com comandos imperativos. Apagar um Pod problemático
funciona por trinta segundos, porque o controller recria exatamente o mesmo Pod
a partir do mesmo manifesto. O conserto é sempre no estado desejado.

**Como inspecionar**

`kubectl get pods` com a coluna `AGE`. Idade que reinicia é sinal de que algo
está sendo recriado, e a coluna `RESTARTS` diz se é o container ou o Pod.

#### 4. Arquitetura do cluster

**O que é**

Um cluster tem dois planos. O control plane decide, os nodes executam.

| Componente | Papel |
|---|---|
| kube-apiserver | Porta de entrada única. Valida e persiste todo objeto |
| etcd | Banco chave-valor que guarda o estado desejado |
| kube-scheduler | Escolhe em qual node cada Pod novo vai rodar |
| controller-manager | Laços de reconciliação que aproximam real do desejado |
| kubelet | Agente do node, sobe e vigia os containers |
| runtime de container | Executa de fato, via containerd ou equivalente |

**Como funciona na prática**

Tudo passa pelo apiserver, inclusive o `kubectl`. Quando você aplica um
manifesto, o `kubectl` não fala com o node: ele fala com o apiserver, que valida
e grava. O scheduler percebe um Pod sem node, escolhe um, e o kubelet daquele
node percebe que tem trabalho.

Nenhum desses componentes chama o outro diretamente. Todos observam o apiserver.
É por isso que o cluster continua funcionando quando um controller cai: o estado
está no etcd, e a reconciliação recomeça quando o controller volta.

**O equívoco comum**

Achar que o control plane executa as cargas. Ele decide. Num cluster gerenciado
de nuvem você nem enxerga essas máquinas. No laboratório o cluster tem dois
nodes justamente para a diferença ficar visível.

**Como inspecionar**

```bash
kubectl get nodes
```

No Lab 0 a saída mostra `mentoria-dados-control-plane` com a role
`control-plane` e `mentoria-dados-worker` sem role, os dois em `Ready` e na
versão v1.36.1.

#### 5. Pod, a unidade de execução

##### 5.1 O Pod não é um container

**O que é**

O Kubernetes não agenda containers, agenda Pods. Um Pod é um ou mais containers
que compartilham rede e volumes, e que vivem e morrem juntos.

Containers do mesmo Pod conversam por `localhost`, porque compartilham o
namespace de rede. O Pod tem um IP, não cada container.

**O equívoco comum**

Colocar dois processos independentes no mesmo Pod porque "andam juntos". Se um
pode escalar sem o outro, são dois Pods. O Pod é a unidade de escala, e o que
está junto escala junto.

##### 5.2 Init containers e sidecars

**O que é**

Um init container roda antes dos containers principais, em ordem, até terminar.
Serve para preparar dado ou esperar dependência.

O sidecar nativo é um init container com `restartPolicy: Always`, o que faz com
que ele continue rodando durante toda a vida do Pod, em vez de apenas na
inicialização.

```yaml
initContainers:
  - name: coletor-de-log
    image: alpine:3.22
    restartPolicy: Always
    command: ["sh", "-c", "tail -F /opt/logs.txt"]
```

**Atenção à versão, porque o deck da aula generaliza aqui.** O recurso está
ativo por padrão desde o Kubernetes 1.29, e passou a **estável** no 1.33. São
coisas diferentes: entre 1.29 e 1.32 ele funcionava como recurso ainda em
evolução, sujeito a mudança. Em cluster nessa faixa, confira antes de depender.

##### 5.3 O Pod é efêmero

**O que é**

Pod não é atualizado, é substituído. Mudar a imagem cria Pods novos e apaga os
antigos.

**O equívoco comum**

Depender do IP ou do nome de um Pod. Os dois mudam. É exatamente por isso que
existe o Service, e é por isso que o laboratório mostra o nome do Pod mudando a
cada substituição.

##### 5.4 Probes

| Probe | Pergunta que responde | O que acontece se falhar |
|---|---|---|
| `readinessProbe` | Está pronto para receber tráfego? | Sai do balanceamento do Service |
| `livenessProbe` | Ainda está vivo? | O container é reiniciado |
| `startupProbe` | Já terminou de subir? | Protege o lento de ser morto cedo |

**O equívoco comum**

Confundir `readiness` com `liveness`. Uma aplicação que está subindo e ainda não
respondeu ao primeiro tráfego não está quebrada, está ocupada. Configurar
`liveness` agressivo nesse caso cria um laço de reinício sem causa real.

#### 6. Workloads, quem gerencia os Pods

**O que é**

Na prática você quase nunca cria um Pod diretamente. Você declara um controller,
e ele cuida de criar, substituir e escalar.

| Controller | Para que serve | Exemplo em dados |
|---|---|---|
| Deployment | Aplicação sem estado, com rollout e rollback | Serviço de query, API interna |
| StatefulSet | Identidade e disco estáveis por réplica | Banco, broker de mensagem |
| DaemonSet | Um Pod por node | Agente de log ou de métrica |
| Job | Executa até concluir, com repetição em caso de falha | Transformação diária |
| CronJob | Job com agenda | Carga periódica sem orquestrador |

**Como funciona na prática**

O laboratório usa dois. O `servico-de-consulta` é um Deployment, porque é um
serviço sem estado que precisa de rollout controlado. A `transformacao-diaria` é
um Job, porque roda, termina e sai.

Na saída do Lab 1 os dois convivem, com estados diferentes e ambos corretos:

```
servico-de-consulta-7d69958dfb-7hvfr   1/1     Running     0   34s
transformacao-diaria-4b75d             0/1     Completed   0   34s
```

`Completed` com `0/1` pronto não é falha. É um Job que fez o que devia.

**O equívoco comum**

Usar Deployment para carga que termina. O Deployment quer réplicas rodando o
tempo todo, então ele reinicia o processo que terminou com sucesso, e você
recebe um `CrashLoopBackOff` de algo que funcionou. Carga que termina é Job.

**Como inspecionar**

`kubectl get all -n <namespace>` mostra a cadeia Deployment, ReplicaSet e Pod. O
ReplicaSet no meio é o que permite o rollback: cada versão tem o seu.

#### 7. Configuração e segredo

**O que é**

A imagem é imutável, então configuração precisa entrar de fora. É isso que
separa uma imagem reaproveitável de uma imagem por ambiente.

O ConfigMap guarda parâmetro não sensível. O Secret guarda credencial e token.

**Como funciona na prática**

O ConfigMap do laboratório carrega dois parâmetros e um arquivo inteiro:

```yaml
data:
  JANELA_DIAS: "7"
  CANAIS: "google_ads,meta_ads,tiktok_ads"
  transformar.sh: |
    #!/bin/sh
    echo "janela de ${JANELA_DIAS} dias"
```

O Job injeta os parâmetros como variáveis de ambiente e monta o script como
arquivo. No Lab 3 o resultado aparece no log:

```
janela de 7 dias
canais: google_ads,meta_ads,tiktok_ads
processando google_ads
processando meta_ads
processando tiktok_ads
canais processados: 3
```

Nada disso está na imagem. A mesma imagem `alpine:3.22` roda outro script se o
ConfigMap mudar.

**O equívoco comum**

Achar que Secret é criptografia. Não é. O valor é codificado em base64, e quem
tem permissão de leitura no objeto lê o conteúdo. O que protege um Secret é RBAC
restrito mais criptografia em repouso no etcd.

Em ambiente real o Secret não vive no Git. Ele vem de um cofre gerenciado, por
um operador que o injeta no cluster. O arquivo `11-secret.yaml` do laboratório
existe para ser lido, e o valor dele é um marcador.

**Como inspecionar**

Um Secret mudado não chega sozinho ao Pod que o consome por variável de
ambiente. Variável de ambiente é lida na criação do processo, então mudar o
Secret exige recriar o Pod. Montado como volume o comportamento é outro, e o
arquivo é atualizado.

#### 8. Rede, do Service ao que entra no cluster

##### 8.1 O Service dá endereço estável

**O que é**

Pods nascem e morrem com IPs diferentes. O Service dá um nome DNS estável e
balanceia entre os Pods que casam com o seletor.

**Como funciona na prática**

No Lab 5 um Pod alcança o serviço pelo nome completo, de dentro do cluster:

```
http://servico-de-consulta.campanhas.svc.cluster.local/
```

O formato é `<service>.<namespace>.svc.cluster.local`. Dentro do mesmo
namespace, `servico-de-consulta` basta.

Repare numa sutileza do laboratório: o Service escuta na porta 80 e o container
na 8080. O `targetPort` faz a tradução. Isso é comum quando a imagem roda como
usuário sem privilégio, porque portas abaixo de 1024 exigem capacidade extra.

**O equívoco comum**

Achar que o Service aponta para o Deployment. Ele não aponta para nada: ele
seleciona por label. Um erro de label faz o Service existir com zero endpoints,
e o sintoma é conexão recusada sem nenhum erro no Deployment.

**Como inspecionar**

```bash
kubectl -n campanhas get endpoints servico-de-consulta
```

Lista vazia significa que o seletor não casou com nenhum Pod pronto.

##### 8.2 Como o tráfego externo entra

| Recurso | O que faz |
|---|---|
| ClusterIP | Endereço interno, o padrão |
| NodePort | Abre uma porta em cada node |
| LoadBalancer | Pede um balanceador ao provedor de nuvem |
| Gateway API | Roteamento HTTP com papéis separados entre infra e aplicação |

**Uma decisão de projeto, não de detalhe.** O Ingress NGINX, que foi o padrão de
fato por anos, foi arquivado em 24 de março de 2026, e o próprio projeto
recomenda que quem não o usa hoje não comece a usar, escolhendo uma
implementação da Gateway API. Material anterior a 2026 vai ensinar Ingress
NGINX, e é preciso saber que aquele caminho fechou.

Para desenvolvimento, nada disso é necessário. O `port-forward` do Lab 5 leva a
porta do Service para a sua máquina e resolve o dia a dia.

#### 9. Recursos, limites e QoS

##### 9.1 requests e limits fazem coisas diferentes

**O que é**

`requests` é o que o scheduler reserva, e decide **onde** o Pod cabe. `limits` é
teto rígido, e decide **o que acontece** quando o processo passa dele.

| Recurso | Passar do limite causa |
|---|---|
| Memória | O processo é morto, com `OOMKilled` |
| CPU | O processo é afunilado, e fica lento |

A assimetria é importante. Memória não tem como ser emprestada, então a única
saída do kernel é matar. CPU é divisível no tempo, então dá para atrasar.

**Como funciona na prática**

O Lab 4 mostra o caso. O Pod pede 200 MiB contra um limite de 64 MiB:

```
      Reason:       OOMKilled
      Exit Code:    137
    Limits:
      memory:  64Mi
```

O código 137 é 128 mais 9, o sinal `SIGKILL`. Quem matou foi o kernel, e o
Kubernetes apenas reportou. Isso importa no diagnóstico: não adianta procurar
erro no log da aplicação, porque ela não teve chance de escrever nada.

**O equívoco comum**

Definir `limits` de CPU generosos achando que ajuda. Limite de CPU produz
afunilamento mesmo com a máquina ociosa, porque o teto é por período de tempo,
não por disponibilidade. Em carga de dados, é comum definir `requests` de CPU e
deixar o `limits` de CPU de fora, mantendo o de memória.

##### 9.2 As classes de QoS

**O que é**

A classe é derivada, não declarada. Ela decide quem é despejado primeiro quando
o node fica sem memória.

| Classe | Como se obtém | Ordem de despejo |
|---|---|---|
| Guaranteed | `requests` igual a `limits`, em todos os containers | último |
| Burstable | `requests` menor que `limits`, ou só um dos dois | meio |
| BestEffort | Nenhum `requests` nem `limits` | primeiro |

**Como inspecionar**

No laboratório, todas as cargas saem como `Burstable`, porque em todas o
`requests` é menor que o `limits`:

```
POD                                    QOS         NODE
consumidor-de-memoria                  Burstable   mentoria-dados-worker
servico-de-consulta-7d69958dfb-7hvfr   Burstable   mentoria-dados-worker
transformacao-diaria-4b75d             Burstable   mentoria-dados-worker
```

Para obter `Guaranteed`, iguale os dois valores. Vale para a tarefa que não pode
morrer no meio, e custa reserva de capacidade que fica sua mesmo sem uso.

##### 9.3 Mudar recurso sem recriar o Pod

Desde o Kubernetes 1.35, redimensionar CPU e memória de um Pod em execução é
recurso estável. Antes disso, mudar recurso significava substituir o Pod.

Para carga de dados isso muda um hábito: dá para ajustar uma tarefa longa que
está apertada, em vez de matá-la e recomeçar do zero.

#### 10. Agendamento, onde o Pod roda

**O que é**

Em cluster de dados os nodes não são iguais. Existe node com muita memória, node
com GPU e node barato que pode ser retomado a qualquer momento.

| Mecanismo | O que faz |
|---|---|
| `nodeSelector` | Filtro simples por label do node |
| Affinity | Regras ricas, obrigatórias ou preferenciais |
| Taints e tolerations | O node repele Pods; só entra quem tolera |
| Topology spread | Distribui réplicas entre zonas e nodes |
| PriorityClass | Define quem é despejado primeiro quando falta capacidade |

**Como funciona na prática**

O cluster do laboratório declara um label no node worker:

```yaml
  - role: worker
    labels:
      workload: batch
```

E o Job pede exatamente aquele node:

```yaml
      nodeSelector:
        workload: batch
```

É o padrão real de separar carga de lote da carga que responde a usuário.

**O equívoco comum**

Confundir `nodeSelector` com taint. O seletor diz onde o Pod **quer** ir, e não
impede que outro Pod vá para o mesmo node. O taint é o inverso: o node repele
quem não declara tolerância. Para reservar node caro, o seletor sozinho não
basta.

#### 11. Escalonamento

**O que é**

Escala tem dois níveis, e eles são complementares: mais réplicas da aplicação, e
mais máquinas no cluster.

| Mecanismo | Escala o quê | Reage a |
|---|---|---|
| HPA | Réplicas do Pod | CPU, memória ou métrica customizada |
| VPA | `requests` e `limits` do Pod | Consumo observado |
| Escalonamento por evento | Réplicas, inclusive até zero | Fila, lag de tópico, evento externo |
| Autoscaler de node | Máquinas do cluster | Pods que não couberam |

**Como funciona na prática**

Escalar à mão é uma linha, e o Lab 6 começa por ela:

```bash
kubectl -n campanhas scale deploy/servico-de-consulta --replicas=5
```

Em produção o número não é escrito à mão. Para pipeline de dados o gatilho
raramente é CPU: o sinal útil costuma ser o tamanho da fila ou o atraso do
consumidor, e é por isso que escalonamento por evento externo domina esse
cenário.

**O equívoco comum**

Ligar escalonamento de Pod sem escalonamento de node. Os Pods novos são criados,
não cabem em lugar nenhum e ficam em `Pending`. A métrica de escala sobe, o
número de réplicas sobe, e nada é processado.

#### 12. Segurança

##### 12.1 RBAC e identidade do Pod

**O que é**

O RBAC define permissões por verbo e recurso, ligadas a uma identidade. Um Pod
tem identidade própria, a ServiceAccount.

**O equívoco comum**

Guardar chave de nuvem em Secret para o Pod usar. Existe caminho melhor em toda
nuvem: associar a ServiceAccount a um papel do provedor, e o Pod recebe
credencial temporária sem que nenhuma chave seja escrita. Menos coisa para
vazar, e rotação automática.

##### 12.2 Pod Security Admission

**O que é**

O Pod Security Admission é o controlador que recusa Pod fora do padrão. Ele é
estável desde o Kubernetes 1.25 e substituiu o PodSecurityPolicy.

Ele tem três níveis e três modos:

| Nível | O que permite |
|---|---|
| `privileged` | Tudo |
| `baseline` | Bloqueia o que é notoriamente perigoso |
| `restricted` | Exige boas práticas: sem root, sem escalar privilégio, sem capacidades |

| Modo | O que faz na violação |
|---|---|
| `enforce` | Recusa o Pod |
| `audit` | Registra no log de auditoria |
| `warn` | Mostra aviso a quem aplicou |

A configuração é por label no namespace, no formato
`pod-security.kubernetes.io/<MODO>: <NÍVEL>`.

**Como funciona na prática**

O namespace do laboratório aplica o nível mais estrito nos três modos:

```yaml
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

E toda carga foi escrita para satisfazê-lo:

```yaml
      securityContext:
        runAsNonRoot: true
        runAsUser: 101
        seccompProfile:
          type: RuntimeDefault
```

Por isso a saída do Lab 1 não tem nenhum aviso. Isso é resultado, não acaso: a
primeira versão deste laboratório usava a imagem oficial do nginx, que roda como
root e precisa da capacidade `CHOWN` para preparar o próprio cache. Ela entrou
em `CrashLoopBackOff` com a mensagem
`chown("/var/cache/nginx/client_temp", 101) failed (1: Operation not permitted)`.
A correção não foi devolver a capacidade, e sim trocar por uma imagem que já roda
sem privilégio.

**O equívoco comum**

Começar por `enforce: restricted` num namespace que já tem carga rodando. Você
recusa Pod em produção. O caminho é ligar `warn` e `audit` primeiro, corrigir o
que aparecer, e só então mudar o `enforce`. O laboratório pode começar no
estrito porque nasceu assim.

##### 12.3 Imagem

Tag imutável, registro privado e varredura de vulnerabilidade no processo de
entrega. O laboratório usa `nginxinc/nginx-unprivileged:1.29-alpine` e não
`latest`, e a razão aparece no Lab 6: sem tag fixa, você não sabe para onde o
rollback está voltando.

#### 13. Kubernetes na engenharia de dados

##### 13.1 O que muda no pipeline

**O que é**

Para o time de dados o Kubernetes é o substrato que dá isolamento de dependência
e elasticidade por tarefa.

| Ferramenta | Como aparece no cluster |
|---|---|
| Airflow | Um Pod por task, com imagem e recursos próprios |
| Spark | Um operador dedicado, com o job como recurso do cluster |
| dbt | Um Job efêmero que roda e sai |
| Query engine | Um Deployment, porque precisa estar de pé |

O `transformacao-diaria` do laboratório é o formato de todos os itens de lote
dessa tabela: um Job, com sua imagem, seus recursos e seu node.

##### 13.2 Airflow no Kubernetes

**Como funciona na prática**

Com o `KubernetesPodOperator`, cada task vira um Pod. É isso que resolve o
conflito de dependências que abriu a seção 2 desta apostila.

```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

extrair = KubernetesPodOperator(
    task_id="extrair_precos",
    image="registry.exemplo/etl-python:1.0.0",
    cmds=["python", "-m", "coletores.precos"],
    container_resources=k8s.V1ResourceRequirements(
        requests={"cpu": "1", "memory": "2Gi"},
        limits={"memory": "2Gi"},
    ),
    node_selector={"workload": "batch"},
    on_finish_action="delete_pod",
)
```

<!-- verificacao: nivel 1, conferido contra a referencia do provider cncf.kubernetes, nao executado, 2026-07-31 -->

Dois detalhes deste bloco custam tempo de quem descobre sozinho, e por isso
estão aqui:

**`container_resources` espera um objeto, não um dicionário.** O tipo é
`kubernetes.client.models.V1ResourceRequirements`. Passar um dicionário é o erro
mais comum de quem migra de exemplo antigo.

**`on_finish_action` substituiu `is_delete_operator_pod`.** Os valores são
`delete_pod`, `delete_succeeded_pod`, `keep_pod` e `delete_active_pod`. Material
que ainda usa o parâmetro antigo está desatualizado.

Este bloco foi conferido contra a referência oficial do provider, e **não foi
executado**. O laboratório deste módulo não sobe Airflow, e afirmar mais do que
isso seria inventar.

##### 13.3 O que o Kubernetes não resolve

Ele não agenda por tempo com dependência entre tarefas, não observa fonte
externa e não faz backfill. Isso continua sendo do orquestrador, que é o assunto
do módulo de Airflow. O CronJob resolve carga periódica simples e não substitui
um DAG.

#### 14. Laboratório

O laboratório roda num cluster local criado com kind, em Docker, com Kubernetes
v1.36.1. Não precisa de nuvem e não custa nada.

Os runbooks em `infrastructure/runbooks/` trazem o passo a passo completo,
inclusive como isolar o seu kubeconfig antes de começar. Faça isso: se você usa
Kubernetes no trabalho, um comando no contexto errado não tem desfazer.

##### Lab 0: Criar o cluster local

Pré-condição: Docker, kind 0.32.0 ou superior, kubectl 1.35 ou superior.

```bash
cd engenharia_de_dados/modulos/kubernetes/infrastructure
export KUBECONFIG="$PWD/kubeconfig-mentoria"
kind create cluster --config kind-cluster.yaml
kubectl get nodes
```

Saída esperada: `mentoria-dados-control-plane` e `mentoria-dados-worker`, ambos
em `Ready` e na versão `v1.36.1`.

##### Lab 1: Aplicar o estado desejado

```bash
kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/
kubectl -n campanhas rollout status deploy/servico-de-consulta
```

Saída esperada: `deployment "servico-de-consulta" successfully rolled out`, sem
nenhum aviso de `PodSecurity`.

O namespace vai primeiro de propósito. Aplicar a pasta inteira num cluster novo
pode falhar, porque os objetos seguintes referenciam um namespace que ainda não
existe.

##### Lab 2: Apagar um Pod e ver o cluster reconciliar

```bash
POD=$(kubectl -n campanhas get pods -l app=servico-de-consulta -o jsonpath='{.items[0].metadata.name}')
kubectl -n campanhas delete pod "$POD"
kubectl -n campanhas get pods -l app=servico-de-consulta
```

Saída esperada: a contagem de Pods continua a mesma, e um deles tem nome novo e
poucos segundos de idade.

##### Lab 3: Ver ConfigMap e Secret injetados

```bash
kubectl -n campanhas logs job/transformacao-diaria
```

Saída esperada: a janela de 7 dias, os três canais e a linha
`canais processados: 3`. Nada disso está dentro da imagem.

##### Lab 4: Ler a assinatura do OOMKilled

```bash
kubectl -n campanhas get pod consumidor-de-memoria
kubectl -n campanhas describe pod consumidor-de-memoria
```

Saída esperada: `STATUS OOMKilled` na listagem, e `Reason: OOMKilled` com
`Exit Code: 137` no detalhe.

Este Pod é quebrado de propósito. Ver a assinatura aqui é mais barato do que
encontrá-la pela primeira vez com o pipeline parado.

##### Lab 5: Alcançar o Service

```bash
kubectl apply -f manifests/50-pod-testador.yaml
kubectl -n campanhas logs testador-de-dns
kubectl -n campanhas port-forward svc/servico-de-consulta 18080:80
```

Saída esperada: o HTML de boas vindas do nginx no log do testador, e código 200
ao acessar `http://127.0.0.1:18080/` com o `port-forward` de pé.

O testador é um manifesto e não um `kubectl run` de uma linha por um motivo
concreto: o namespace aplica o perfil `restricted`, e o Pod padrão que o
`kubectl run` monta não o satisfaz.

##### Lab 6: Escalar, quebrar o rollout e desfazer

```bash
kubectl -n campanhas scale deploy/servico-de-consulta --replicas=5
kubectl -n campanhas set image deploy/servico-de-consulta servidor=nginxinc/nginx-unprivileged:9.9-inexistente
kubectl -n campanhas get pods -l app=servico-de-consulta
```

Saída esperada, com os dois estados convivendo:

```
servico-de-consulta-7686d488b9-lqj6q   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7686d488b9-rc4lr   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7686d488b9-rvnct   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7d69958dfb-bpw7w   1/1     Running            0   112s
servico-de-consulta-7d69958dfb-kddqw   1/1     Running            0   64s
```

Este é o laboratório mais importante da lista. O serviço não caiu, porque o
rollout só derruba um Pod antigo depois que o novo fica pronto, e o novo nunca
ficou. É o mecanismo que transforma um deploy errado em incidente sem impacto.

Desfazendo:

```bash
kubectl -n campanhas rollout undo deploy/servico-de-consulta
```

Leia o aviso que aparece. Ele diz que a anotação de última configuração aplicada
não é atualizada, e isso tem consequência: num fluxo em que o Git é a fonte da
verdade, o `undo` conserta o cluster e deixa o repositório errado. O próximo
`apply` traz a imagem quebrada de volta. O conserto real é reverter o commit.

##### Lab 7: Derrubar o cluster

```bash
kind delete cluster --name mentoria-dados
```

Saída esperada: `Deleting cluster "mentoria-dados"` seguido de `Deleted nodes`.

#### 15. Exercícios e entregáveis

**Exercício 1: Escolha de controller**

Objetivo: escolher o controller pela natureza da carga.

Contexto: cinco cargas do projeto de campanhas.

- Um serviço de query que responde ao painel.
- A transformação diária, que roda e termina.
- Um agente de coleta de métrica que precisa existir em todo node.
- Um broker de mensagem com disco próprio por réplica.
- Uma carga de reprocessamento que roda uma vez, sob demanda.

Entregável: tabela com o controller escolhido por carga, a justificativa em uma
frase, e o que quebraria com a escolha errada.

**Exercício 2: Recursos e QoS**

Objetivo: prever comportamento a partir do manifesto.

Contexto: os manifestos do laboratório.

Entregável: para cada carga, a classe de QoS resultante e por quê; depois, a
alteração necessária para o `servico-de-consulta` virar `Guaranteed`, aplicada e
confirmada com `kubectl get pods -o custom-columns`. Diga também o que essa
mudança custa.

**Exercício 3: Ler a falha**

Objetivo: diagnosticar pela assinatura, não por tentativa.

Contexto: crie três falhas de propósito no cluster do laboratório.

1. Um Pod que pede mais memória do que qualquer node tem.
2. Um Pod com uma imagem que não existe.
3. Um Deployment cujo Service não encontra nenhum Pod.

Entregável: para cada uma, o `STATUS` observado, o comando que revelou a causa e
a correção. O terceiro caso não gera erro no Deployment, e descobrir isso é o
exercício.

**Exercício 4: Do Airflow para o cluster**

Objetivo: ligar o que você já sabe ao que acabou de aprender.

Contexto: uma DAG com três tasks que hoje compartilham o mesmo ambiente e têm
dependências conflitantes.

Entregável: a descrição de como cada task viraria um Pod, com imagem, recursos e
seletor de node propostos, mais uma observação sobre o que **não** melhora com a
mudança.

#### 16. Mini-desafio com solução

**Enunciado**

A transformação diária passou a falhar de forma intermitente. Nos dias de maior
volume ela termina com `OOMKilled`; nos demais, funciona. O time aumentou o
limite de memória e o problema diminuiu, mas não sumiu, e o custo do cluster
subiu porque a reserva foi aplicada a todas as execuções.

Proponha uma solução e explique por que ela é melhor do que aumentar o limite.

**Dicas**

- `requests` e `limits` fazem coisas diferentes, e só um deles reserva
  capacidade.
- Existe mais de uma forma de dar mais memória a uma tarefa, e uma delas não
  exige recriar o Pod.
- A pergunta "quanto ela realmente usa" ainda não foi respondida por ninguém.

**Gabarito comentado**

Primeiro, medir. Ninguém sabe o consumo real, e todas as decisões até agora
foram palpite. Sem a curva de uso por execução, qualquer número novo é outro
palpite mais caro.

Segundo, separar `requests` de `limits`. O que subiu o custo foi mexer nos dois
juntos: o `requests` é o que reserva capacidade em todo dia, inclusive nos dias
pequenos. Manter o `requests` no consumo típico e o `limits` no pico absorve o
dia atípico sem reservar para o dia normal. O custo disso é a classe de QoS, que
deixa de ser `Guaranteed`, e portanto a tarefa passa a ser candidata a despejo
antes das que reservam.

Terceiro, considerar o redimensionamento em execução, estável desde o 1.35. Para
uma tarefa longa que aperta no meio, ajustar sem recriar evita perder o trabalho
já feito.

Quarto, olhar a causa. `OOMKilled` proporcional ao volume quase sempre significa
que o processo carrega o conjunto inteiro na memória. Processar em blocos resolve
o problema em vez de administrá-lo, e é a única alternativa que não fica mais
cara conforme o dado cresce.

**Interpretação**

A resposta fraca escolhe um número novo. A resposta boa mede antes, separa
`requests` de `limits` com intenção, e reconhece que aumentar limite é comprar
tempo. Quem chegou no quarto ponto entendeu que o Kubernetes estava reportando o
sintoma de um problema de código.

#### 17. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Estado desejado | Trata o cluster com comandos imperativos | Explica reconciliação | Diagnostica um problema pelo desvio entre real e desejado |
| Pod e workload | Cria Pod solto | Escolhe o controller certo | Justifica pela natureza da carga e prevê o que quebra |
| Recursos e QoS | Copia valores de exemplo | Define requests e limits com intenção | Prevê a classe de QoS e o comportamento sob pressão |
| Rede | Confunde Service com Deployment | Entende seletor e endpoints | Diagnostica Service sem endpoint por erro de label |
| Segurança | Deixa tudo como veio | Aplica securityContext e entende PSA | Planeja a migração de baseline para restricted |
| Diagnóstico | Tenta e erra | Lê a assinatura e vai à causa | Sabe quando o log da aplicação não vai ter nada |
| Ligação com dados | Vê Kubernetes como assunto de infra | Liga ao executor do Airflow | Sabe o que o cluster não resolve e continua no orquestrador |

#### 18. Erros comuns e como corrigir

**Pending**

Sintoma: o Pod fica em `Pending` sem sair do lugar.

Causa: nenhum node tem recurso suficiente, ou nenhum node satisfaz o seletor, a
afinidade ou a tolerância declarada.

Correção: `kubectl describe pod` e ler os eventos, que dizem qual filtro
eliminou cada node. Ajustar `requests`, o seletor, ou acrescentar capacidade.

**CrashLoopBackOff**

Sintoma: o container sobe e morre em laço, e o intervalo entre tentativas cresce.

Causa: o processo termina logo depois de iniciar. Falta de configuração e
permissão insuficiente são as causas mais comuns.

Correção: `kubectl logs <pod> --previous`, que lê o container que já morreu. Sem
o `--previous` você lê o container atual, que ainda não escreveu nada.

Foi assim que o próprio laboratório foi corrigido: a primeira versão usava a
imagem oficial do nginx com todas as capacidades removidas, e o log anterior
mostrou `chown(...) failed (1: Operation not permitted)`.

**OOMKilled**

Sintoma: `STATUS OOMKilled` e código de saída 137.

Causa: o processo passou do limite de memória e foi morto pelo kernel.

Correção: medir o consumo real antes de mexer no número. Depois separar
`requests` de `limits`, e investigar se o processo carrega tudo em memória.

Não procure erro no log da aplicação. Ela foi morta com `SIGKILL` e não teve
chance de escrever nada.

**ImagePullBackOff**

Sintoma: o Pod não sai do lugar e a imagem nunca chega.

Causa: tag inexistente, nome errado, ou falta de credencial no registro privado.

Correção: conferir a tag e o registro; se for privado, conferir o
`imagePullSecrets`. No Lab 6 essa falha é provocada de propósito, e o ponto é
que os Pods antigos continuam servindo.

**Service sem endpoint**

Sintoma: conexão recusada, sem nenhum erro no Deployment nem nos Pods.

Causa: o seletor do Service não casa com os labels dos Pods, ou nenhum Pod está
pronto pela `readinessProbe`.

Correção: `kubectl get endpoints <service>`. Lista vazia confirma o diagnóstico.

**O rollback conserta o cluster e deixa o Git errado**

Sintoma: você desfaz um deploy ruim, e ele volta na próxima sincronização.

Causa: `kubectl rollout undo` altera o cluster e não altera o repositório. O
próprio comando avisa que a anotação de última configuração aplicada não é
atualizada.

Correção: reverter o commit. Num fluxo em que o Git é a fonte da verdade, o
`undo` serve para parar o sangramento, não para consertar.

**O apply da pasta falha em cluster novo**

Sintoma: `namespaces "campanhas" not found` em vários arquivos de uma vez.

Causa: os objetos referenciam um namespace que está sendo criado no mesmo
comando, e a ordem não é garantida.

Correção: aplicar o namespace primeiro, como faz o Lab 1. O mesmo vale para
`--dry-run=server`, que falha em cascata porque nada é realmente criado.

#### 19. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 2 e 3. O terceiro é o que mais se parece com o trabalho real.

**O que estudar em seguida, dentro da trilha**

O módulo de infraestrutura como código, que responde como esse cluster nasce sem
ninguém digitar comando. Depois, revisite o módulo de Airflow: o
`KubernetesPodOperator` e o executor que cria um Pod por task passam a fazer
sentido completo agora.

**O que aprofundar por conta**

Empacotamento e entrega. Helm e Kustomize resolvem o mesmo problema de formas
diferentes, e entrega baseada em Git fecha o ciclo. O ganho que mais aparece é
revisão por pull request e rollback por commit.

**O que não perseguir agora**

Operar o control plane, ajustar rede do cluster e escrever operator. É trabalho
de plataforma, e você precisa primeiro ser um bom usuário do cluster. A leitura
de manifesto e o diagnóstico de falha valem mais no seu dia a dia do que
qualquer detalhe do etcd.

#### 20. Glossário

| Termo | Significado |
|---|---|
| ConfigMap | Objeto que guarda parâmetro não sensível |
| Control plane | Conjunto de componentes que decide o que roda onde |
| DaemonSet | Controller que mantém um Pod por node |
| Deployment | Controller de aplicação sem estado, com rollout e rollback |
| Estado desejado | O que você declara que deve existir |
| Job | Controller de carga que executa até concluir |
| kubelet | Agente do node que sobe e vigia containers |
| limits | Teto rígido de recurso para o container |
| Namespace | Divisão lógica de objetos dentro do cluster |
| Node | Máquina que executa cargas |
| OOMKilled | Estado do container morto pelo kernel por estourar a memória |
| Pod | Unidade de execução, um ou mais containers que vivem juntos |
| Pod Security Admission | Controlador que recusa Pod fora do perfil do namespace |
| Probe | Verificação periódica de prontidão ou de vida do container |
| QoS | Classe derivada de requests e limits que decide a ordem de despejo |
| RBAC | Controle de permissão por verbo e recurso |
| Reconciliação | Laço que aproxima o estado real do desejado |
| requests | Recurso que o scheduler reserva para o container |
| Secret | Objeto que guarda credencial, codificado e não criptografado |
| Service | Nome e endereço estáveis para um conjunto de Pods |
| ServiceAccount | Identidade de um Pod dentro do cluster |
| StatefulSet | Controller com identidade e disco estáveis por réplica |
| Taint e toleration | Mecanismo pelo qual um node repele Pods que não o toleram |

#### Referências

Documentação oficial do Kubernetes, consultada em 2026-07-31:

- Versões e suporte: https://kubernetes.io/releases/
- Sidecar containers: https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
- Pod Security Admission: https://kubernetes.io/docs/concepts/security/pod-security-admission/
- Redimensionar recursos do container: https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/

Outras fontes oficiais, consultadas em 2026-07-31:

- Repositório do Ingress NGINX, com o aviso de arquivamento: https://github.com/kubernetes/ingress-nginx
- Referência do KubernetesPodOperator: https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html
- Projeto kind: https://kind.sigs.k8s.io/

#### Fontes verificadas (2026-07-31)

- O sidecar nativo está ativo por padrão desde o Kubernetes 1.29 e passou a
  estável no 1.33. A sintaxe é um init container com `restartPolicy: Always`.
  https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
- O Pod Security Admission é estável desde o Kubernetes 1.25 e substituiu o
  PodSecurityPolicy. Os níveis são `privileged`, `baseline` e `restricted`, os
  modos são `enforce`, `audit` e `warn`, e a configuração é por label no formato
  `pod-security.kubernetes.io/<MODO>: <NÍVEL>`.
  https://kubernetes.io/docs/concepts/security/pod-security-admission/
- O redimensionamento de CPU e memória de Pod em execução é estável desde o
  Kubernetes 1.35.
  https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/
- A versão mais recente do Kubernetes em 2026-07-31 é a 1.36.2, de 2026-06-09, e
  as versões com suporte são 1.34, 1.35 e 1.36. https://kubernetes.io/releases/
- O repositório do Ingress NGINX foi arquivado em 24 de março de 2026, está em
  modo somente leitura, e o próprio projeto recomenda que quem ainda não o usa
  escolha uma implementação da Gateway API em vez dele.
  https://github.com/kubernetes/ingress-nginx
- No `KubernetesPodOperator`, o parâmetro `container_resources` espera
  `kubernetes.client.models.V1ResourceRequirements`, e `on_finish_action`
  substitui o antigo `is_delete_operator_pod`, aceitando `delete_pod`,
  `delete_succeeded_pod`, `keep_pod` e `delete_active_pod`. O bloco Python da
  seção 13 foi conferido contra essa referência e não foi executado.
  https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html
- Todas as saídas de laboratório citadas nesta apostila foram capturadas em
  execução real num cluster kind v0.32.0 com Kubernetes v1.36.1, kubectl v1.36.3
  e containerd 2.3.1, em 2026-07-31. Isso inclui a reconciliação do Pod apagado,
  o log do Job com ConfigMap injetado, o `OOMKilled` com código 137, as classes
  de QoS, o `ImagePullBackOff` convivendo com os Pods antigos em `Running` e o
  rollback restaurando a imagem. O registro completo, com comando e nível, está
  em `lab.json`.
- A falha de `chown` citada na seção 12 foi observada de verdade durante a
  construção deste laboratório, na versão que usava a imagem oficial do nginx com
  todas as capacidades removidas.
