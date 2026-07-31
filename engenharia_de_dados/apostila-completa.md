---
title: "Apostila completa, Engenharia de Dados"
date: 2026-07-30
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
- [Capitulo 8, Streaming com Apache Kafka](#capitulo-8-streaming-com-apache-kafka)

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

## Capitulo 8, Streaming com Apache Kafka

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
