# Apostila — Sessão 05: Dados, fontes e arquitetura do projeto real

## Resumo executivo

Esta apostila é o material de referência completo da Sessão 05. O ponto de entrada não é tecnologia — é negócio. A arquitetura que será construída nas próximas sessões começa com perguntas reais de gestores e stakeholders. Só depois de entender o que precisa ser respondido é possível justificar cada decisão arquitetural.

A sessão apresenta o domínio de dados de uma startup fictícia de marketing/e-commerce, as cinco entidades do projeto, a natureza de cada fonte de dados e as categorias de ferramentas disponíveis para cada tipo de ingestão. O resultado é um architecture canvas v0 com slots de ferramentas marcados e contratos de dados v0 definidos por fonte.

Nenhum comando é executado nesta sessão.

---

## 1. Objetivo pedagógico

Ao final desta sessão, o mentorado deve ser capaz de:

1. Partir de perguntas de negócio para justificar decisões arquiteturais.
2. Identificar as fontes necessárias para responder qualquer pergunta do projeto.
3. Justificar por que cada fonte exige uma abordagem de ingestão diferente (CDC, batch, streaming).
4. Conhecer as categorias de ferramentas disponíveis para cada tipo de ingestão.
5. Desenhar um architecture canvas v0 com camadas Bronze/Silver/Gold e slots de ferramentas marcados.
6. Definir contratos de dados v0 por fonte: schema, formato, partição e SLA.

---

## 2. Contexto do projeto (startup fictícia de marketing/e-commerce)

### 2.1 Cenário

Uma startup de marketing/e-commerce gerencia campanhas pagas em múltiplos canais (Google Ads, Meta, TikTok), tem uma base de usuários em crescimento e precisa responder, semanal e diariamente, perguntas como:

- Quais canais trazem melhor ROI?
- Quais campanhas convertem mais por segmento?
- Onde há queda de conversão no funil?
- Quais usuários estão em risco de churn esta semana?

O time de dados é pequeno. As decisões de arquitetura precisam ser sustentáveis com poucos engenheiros e sem orçamento de enterprise.

### 2.2 Por que OSS

O projeto usa stack OSS (Airflow, MinIO, Trino) como escolha deliberada por portabilidade e ausência de vendor lock-in. A lógica é a mesma que qualquer stack de dados maduro — camadas, contratos, qualidade. A ferramenta é diferente; os princípios são os mesmos.

---

## 3. Perguntas de negócio por stakeholder

A arquitetura não começa pelo diagrama. Começa aqui.

### CEO / Diretoria

- "Qual campanha está gerando mais receita este mês?"
- "Quanto estamos gastando por real faturado em cada canal?"
- "Quantos novos clientes adquirimos esta semana versus a semana passada?"

### Time de Growth / Marketing

- "Qual é a taxa de conversão do funil por campanha e por canal?"
- "Em qual etapa estamos perdendo mais usuários?"
- "Qual canal tem menor CAC (custo de aquisição de cliente)?"

### Time de Operações

- "Há alguma queda anômala no volume de checkouts hoje?"
- "Quais usuários estão em risco de churn esta semana?"

### Time de Analytics / BI

- "Como está a evolução do ROI mês a mês por canal?"
- "Qual é o perfil dos usuários que chegam ao purchase por campanha?"

### Tabela: pergunta → fontes necessárias

| Pergunta | Stakeholder | Fontes necessárias |
| --- | --- | --- |
| ROI por campanha | CEO / Analytics | `costs` (API) + `events` (Kafka) + `campaigns` (CDC) |
| Taxa de conversão do funil | Growth | `events` (Kafka) |
| Novos clientes por semana | CEO | `users` (CDC) |
| Risco de churn | Operações | `crm` (CDC) + `events` (Kafka) |
| CAC por canal | Growth | `costs` (API) + `users` (CDC) + `events` (Kafka) |
| Queda de checkouts hoje | Operações | `events` (Kafka) — requer baixa latência |
| Perfil de usuários que convertem | Analytics | `users` (CDC) + `events` (Kafka) + `campaigns` (CDC) |

**Ponto central:** nenhuma dessas perguntas é respondível com uma fonte só. A motivação da arquitetura é exatamente essa: integrar fontes heterogêneas com contratos claros.

---

## 4. Modelo de dados — as cinco entidades

### 4.1 Entidades e campos principais

**users** — Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `user_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome do usuário |
| `email` | VARCHAR | E-mail |
| `segment` | VARCHAR | Segmento (ex.: premium, free) |
| `created_at` | TIMESTAMP | Data de criação |
| `updated_at` | TIMESTAMP | Última atualização |

**campaigns** — Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `campaign_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome da campanha |
| `channel` | VARCHAR | Canal (google, meta, tiktok) |
| `start_date` | DATE | Data de início |
| `end_date` | DATE | Data de término |
| `status` | VARCHAR | Status (active, paused, ended) |
| `updated_at` | TIMESTAMP | Última atualização |

**events** — Fonte: Kafka (streaming)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `event_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `event_type` | VARCHAR | Tipo: visit, signup, checkout, purchase |
| `occurred_at` | TIMESTAMP | Momento do evento |

**costs** — Fonte: API externa de mídia (batch)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `cost_id` | UUID | Chave primária |
| `campaign_id` | UUID | Chave estrangeira → campaigns |
| `date` | DATE | Data de referência do custo |
| `channel` | VARCHAR | Canal de mídia |
| `amount` | DECIMAL | Valor investido |
| `currency` | VARCHAR | Moeda (BRL, USD) |

**crm** — Fonte: PostgreSQL (CDC)

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `crm_id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira → users |
| `lifecycle_stage` | VARCHAR | Estágio: lead, active, at_risk, churned |
| `churn_risk_score` | FLOAT | Score de risco de churn (0 a 1) |
| `last_contact_at` | TIMESTAMP | Último contato registrado |
| `updated_at` | TIMESTAMP | Última atualização |

### 4.2 Diagrama de relações

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

## 5. Natureza das fontes — por que cada uma exige uma abordagem diferente

### 5.1 PostgreSQL → CDC

**Tabelas:** `users`, `campaigns`, `crm`

**Por que CDC e não batch diário?**

Essas entidades são master data que mudam ao longo do dia. Um usuário pode mudar de segmento, uma campanha pode mudar de status, um score de churn pode ser atualizado múltiplas vezes em um dia.

Com batch diário, você captura apenas o estado final do dia — perde o histórico de alterações. Com CDC, você captura cada alteração com timestamp e tipo de operação (INSERT, UPDATE, DELETE). Isso permite:

- Reconstruir o estado de um registro em qualquer ponto do tempo.
- Detectar anomalias (ex.: campanha que mudou de status três vezes em uma hora).
- Alimentar pipelines downstream com dados frescos sem esperar o batch noturno.

**Frequência esperada:** alterações contínuas ao longo do dia.

**SLA no Bronze:** dados disponíveis em até 30 minutos após alteração.

### 5.2 API externa de mídia → Batch

**Tabela:** `costs`

**Por que batch e não CDC ou streaming?**

Os custos de campanha em APIs de mídia são imutáveis por data — ou seja, o custo do dia 10 é um snapshot do que foi gasto naquele dia. Não há alterações de registro a rastrear. A API expõe um endpoint por data e você extrai o que aconteceu.

Além disso, APIs de mídia têm rate limits e custos de chamada. Uma extração contínua seria ineficiente e cara sem ganho real — o dado muda uma vez por dia, no máximo.

Batch diário por data é a abordagem natural: extrai os custos do dia anterior até às 8h e disponibiliza para análise.

**Frequência esperada:** uma extração por dia.

**SLA no Bronze:** dados do dia anterior disponíveis até às 8h.

### 5.3 Kafka → Streaming

**Tabela:** `events`

**Por que streaming e não batch?**

Eventos de funil têm valor na latência. Detectar uma queda no volume de checkouts às 14h, em tempo quase real, é uma informação acionável — você pode investigar e corrigir o problema antes que o impacto seja maior. Ver isso no relatório de ontem não tem o mesmo valor.

Além disso, eventos têm natureza append-only: cada evento é imutável após ocorrer. Não há UPDATE nem DELETE — só INSERT. Isso torna o streaming uma abordagem natural: cada evento publicado no Kafka é consumido e gravado no Bronze sem complexidade de merge.

**Importante:** Kafka será implementado em sessão futura. Nesta sessão, o contrato é projetado e o slot na arquitetura é reservado. A implementação não existe ainda.

**Frequência esperada:** contínua, por evento.

**SLA no Bronze:** latência máxima de 5 minutos do evento ao Bronze.

---

## 6. Ferramentas de ingestão — categorias e exemplos

O objetivo desta seção não é escolher a ferramenta — é abrir o mapa de opções. A escolha acontece na Sessão 06, depois da tarefa de casa.

### 6.1 CDC

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Debezium | OSS, connector Kafka | Padrão de mercado para CDC em PostgreSQL/MySQL. Requer Kafka. |
| Airbyte | OSS/Cloud, plataforma | Tem conector CDC via log replication. Mais fácil de operar. |
| Fivetran | SaaS | Gerenciado, fácil de configurar, mas tem custo por linha sincronizada. |
| AWS DMS | Cloud (AWS) | Gerenciado pela AWS, bom para ambientes já na AWS. |
| Kafka Connect (JDBC) | OSS | Polling via JDBC, não é CDC puro — não captura DELETEs. |

### 6.2 API batch

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Airbyte | OSS/Cloud, plataforma | Tem conectores prontos para Google Ads, Meta Ads, etc. |
| Fivetran | SaaS | Conectores prontos e gerenciados. Custo por linha. |
| Meltano | OSS | Baseado em Singer. Flexível, mas exige mais configuração. |
| Singer | OSS, protocolo | Base do Meltano/Airbyte. Taps e targets customizáveis. |
| Script Python custom | Custom | Máximo controle, máximo custo de manutenção. |

### 6.3 Streaming / Kafka

| Ferramenta | Tipo | Observação |
| --- | --- | --- |
| Kafka Connect | OSS | Conectores para sources e sinks. Ecosistema amplo. |
| Confluent Platform | Cloud/Enterprise | Kafka gerenciado com operações simplificadas. |
| Flink | OSS | Processamento stateful, janelas, joins em streaming. |
| Spark Structured Streaming | OSS | Bom para times com histórico em Spark. |

---

## 7. Make vs buy — critérios para um time pequeno

Para cada fonte, a decisão não é "qual é a ferramenta mais poderosa?" — é "qual é a ferramenta que sustentamos com o time que temos?"

### Critérios de avaliação

| Critério | Favorece ferramenta pronta | Favorece script custom |
| --- | --- | --- |
| Número de fontes | Muitas fontes | Poucas fontes muito específicas |
| Frequência de mudança do contrato da fonte | Alta (API instável) | Baixa (contrato estável) |
| Disponibilidade de manutenção | Time pequeno, sem plantão | Time com capacidade de manter |
| Custo de licença aceitável | Sim | Não — budget restrito |
| Conector pronto disponível | Sim | Não existe conector adequado |
| Complexidade de lógica custom | Baixa | Alta — regras de negócio embutidas |

### Ponto de atenção

Ferramentas prontas reduzem custo de engenharia inicial, mas introduzem dependência de vendor e custo de licença recorrente. Scripts custom têm custo de manutenção invisível — quem mantém quando o engenheiro que escreveu sai da empresa?

Para um time em fase de crescimento, a pergunta mais honesta é: "quem vai manter isso às 2h da manhã quando quebrar?"

---

## 8. Contratos de dados v0

Para cada fonte, preencha os atributos do contrato com base na discussão da sessão.

### PostgreSQL CDC — `users`, `campaigns`, `crm`

| Atributo | Valor |
| --- | --- |
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

### API de mídia — `costs`

| Atributo | Valor |
| --- | --- |
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

### Kafka — `events` (contrato projetado — implementação futura)

| Atributo | Valor |
| --- | --- |
| Schema | |
| Tópico | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

---

## 9. Exercício 2 — Architecture canvas v0

Guia para desenhar o canvas em conjunto durante o Bloco 4.

**Passo 1 — Fontes (canto esquerdo):**
Listar as três fontes: PostgreSQL, API de mídia, Kafka. Anotar a natureza de cada uma (CDC, batch, streaming).

**Passo 2 — Camada de ingestão:**
Para cada fonte, marcar o slot da ferramenta com `[?]`. A escolha da ferramenta fica aberta — é a tarefa de casa.

**Passo 3 — Camadas de armazenamento:**
Desenhar Bronze → Silver → Gold. Para cada camada, anotar:
- Bronze: raw, imutável, particionado por data de ingestão
- Silver: deduplicado, joins aplicados, schema confiável
- Gold: datasets de negócio, prontos para responder as perguntas da seção 3

**Passo 4 — Consumo (canto direito):**
Listar os consumidores: BI/dashboards, analytics ad-hoc, ativações. Conectar ao Gold.

**Passo 5 — Validação:**
Percorrer o canvas de trás para frente: pegar uma pergunta da seção 3 e traçar o caminho até a fonte. Se o caminho existir e estiver completo, o canvas está correto para essa pergunta.

---

## 10. Exercício 1 — Mapeamento de perguntas para fontes

**Objetivo:** praticar o raciocínio de tracing reverso — partir de uma pergunta de negócio e identificar quais entidades e fontes são necessárias para respondê-la.

**Referência:** use a lista de perguntas da seção 3 e o modelo de dados da seção 4.

**Instrução:**

Escolha três perguntas da seção 3 (uma de stakeholders diferentes, se possível). Para cada pergunta, preencha uma linha da tabela abaixo:

- **Pergunta**: copie a pergunta exatamente como está na seção 3.
- **Entidades necessárias**: liste as tabelas do domínio (seção 4.1) cujos campos são necessários para responder.
- **Fontes de ingestão**: identifique de onde cada entidade vem — CDC, API batch ou Kafka (seção 5).
- **Chave de conexão utilizada**: indique qual chave (`user_id`, `campaign_id` ou nenhuma) conecta as entidades listadas.

| Pergunta (seção 3) | Entidades necessárias | Fontes de ingestão | Chave de conexão utilizada |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

**Exemplo resolvido** (não usar como resposta — é apenas para entender o formato):

| Pergunta | Entidades necessárias | Fontes de ingestão | Chave de conexão |
| --- | --- | --- | --- |
| "Qual canal tem menor CAC?" | `costs`, `users`, `events` | API batch + CDC + Kafka | `campaign_id` (costs↔events) e `user_id` (users↔events) |

**Critério de aceite:** para cada linha, o caminho fonte → entidade → pergunta deve ser traçável sem gaps.

---

## 11. Template — Tarefa de casa

A ser apresentada no início da Sessão 06.

| Ingestão | Ferramenta proposta | Justificativa (custo, complexidade, manutenção) |
| --- | --- | --- |
| CDC (PostgreSQL) | | |
| API de mídia (batch) | | |
| Streaming (Kafka) | | |

---

## 12. Critérios de aceite da sessão

- Perguntas dos gestores mapeadas para fontes necessárias.
- Entidades do domínio e relações via `user_id` e `campaign_id` desenhadas.
- Natureza de cada fonte justificada com critério técnico.
- Categorias de ferramentas apresentadas para CDC, API e streaming.
- Architecture canvas v0 desenhado com slots de ferramentas marcados.
- Contratos de dados v0 definidos para as três fontes.
- Contrato do Kafka projetado — schema, tópico, partição — sem implementação.
- Tarefa de casa comunicada: proposta de ferramenta por tipo de ingestão para a S06.
- Backlog claro e priorizado para a Sessão 06.

---

## 13. O que deliberadamente não decidir agora

Para evitar paralisia por análise:

- Não fechar a escolha de ferramenta de ingestão para nenhuma das fontes — essa é a tarefa de casa.
- Não detalhar os jobs individuais de cada pipeline.
- Não discutir sizing de infraestrutura, tuning ou benchmarks.
- Não modelar as tabelas Silver e Gold em detalhes — isso é Sessão 06 em diante.
- Não buscar perfeição no canvas v0 — ele vai evoluir. O objetivo é ter um ponto de partida validado.
- Não implementar nada. Nenhum arquivo é criado, nenhum comando é executado.
