# Sessão 05 — Dados, fontes e arquitetura do projeto real

## Domínio de referência
Marketing e e-commerce.

## Contexto da trilha
Esta sessão marca a transição de conteúdo conceitual para o início de um projeto realista de dados.
Nas sessões 02 a 04, o mentorado trabalhou Airflow, CDC e particionamento de forma isolada.
A partir desta sessão, todos os conceitos se conectam em um único projeto com domínio, fontes e perguntas de negócio reais.

O domínio já está definido: o `cdc_generator` com o domínio `marketing` descreve as entidades e relações que serão a base do projeto. Nesta sessão o mentorado entende esse modelo — sem rodar nada.

## Objetivo
Apresentar o domínio de dados do projeto real, explorar as fontes disponíveis e, junto com o mentorado, desenhar a arquitetura macro da plataforma que será construída ao longo das próximas sessões.

## Fontes do projeto real

| Fonte | Tecnologia | Tabelas | Natureza |
| --- | --- | --- | --- |
| Banco transacional | PostgreSQL (CDC) | `users`, `campaigns`, `crm` | Master data com histórico de alterações |
| API externa de mídia | API mock (custos de campanha) | `costs` | Batch por data, sem histórico nativo |
| Eventos de funil | Kafka | `events` | Streaming: visit → signup → checkout → purchase |

> Kafka será implementado em sessão futura. Nesta sessão o contrato é projetado e o slot na arquitetura é reservado.

## Tecido conectivo do domínio
- `user_id` une: `users` ↔ `events` ↔ `crm`
- `campaign_id` une: `campaigns` ↔ `costs` ↔ `events`

Nenhuma pergunta de negócio relevante é respondida com uma fonte só — essa é a motivação central da arquitetura.

## Nível da sessão
Design arquitetural orientado por perguntas de negócio: o mentorado parte do briefing dos gestores, entende o modelo de dados do domínio e toma decisões com racional explícito. Nenhum comando é executado — é sessão de caneta e papel.

## Resultado esperado
- Compreensão do domínio e das entidades do projeto.
- Mapa de fontes com a natureza de cada uma (CDC, batch, streaming).
- Arquitetura macro v0 desenhada e validada em conjunto.
- Contratos de dados v0 definidos por fonte (schema, particionamento, formato).
- Backlog claro e priorizado para a Sessão 06.

## Perguntas de negócio que ancoram a arquitetura

A arquitetura deve ser projetada para responder perguntas reais de times e lideranças. O mentorado recebe essas perguntas como briefing e precisa identificar quais fontes e camadas são necessárias para cada uma.

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

### Por que isso importa para a arquitetura
Cada pergunta traça um caminho de volta às fontes:

| Pergunta | Fontes necessárias |
| --- | --- |
| ROI por campanha | `costs` (API) + `events` (Kafka) + `campaigns` (CDC) |
| Taxa de conversão do funil | `events` (Kafka) |
| Novos clientes por semana | `users` (CDC) |
| Risco de churn | `crm` (CDC) + `events` (Kafka) |
| CAC por canal | `costs` (API) + `users` (CDC) + `events` (Kafka) |

Nenhuma dessas perguntas é respondível com uma fonte só. A sessão usa esse mapeamento para justificar cada decisão arquitetural.

## Ferramentas de ingestão — briefing e pesquisa

Durante a discussão de natureza das fontes, o mentor apresenta as categorias de ferramentas existentes para cada tipo de ingestão. O objetivo não é decidir — é abrir o espaço de opções e dar ao mentorado um mapa para pesquisar.

### CDC
Exemplos de ferramentas: Debezium, Airbyte (conector CDC), Fivetran, AWS DMS, Kafka Connect.

### API batch
Exemplos de ferramentas: Airbyte, Fivetran, Meltano, Singer, scripts Python custom.

### Streaming / Kafka
Exemplos de ferramentas: Kafka Connect, Confluent Platform, AWS Kinesis, Flink, Spark Structured Streaming.

### Make vs buy — questão central
Para cada fonte, o mentorado deve refletir:
- Faz sentido usar uma ferramenta pronta (Airbyte, Fivetran) ou construir um script custom?
- Qual é o custo de manutenção de cada opção?
- O que encaixa no perfil de um time pequeno em fase de crescimento?

### Tarefa de casa — trazer para a Sessão 06
Ao final da S05, o mentorado recebe a tarefa de pesquisar e propor uma ferramenta para cada tipo de ingestão:

| Ingestão | Ferramenta proposta | Justificativa (custo, complexidade, manutenção) |
| --- | --- | --- |
| CDC (PostgreSQL) | | |
| API de mídia (batch) | | |
| Streaming (Kafka) | | |

A S06 começa com o mentorado apresentando suas propostas. O mentor valida, questiona os trade-offs e juntos decidem o que será implementado na sessão.

## Conceitos-chave
- Natureza dos dados: por que cada fonte exige uma abordagem de ingestão diferente.
- Tecido conectivo: chaves compartilhadas entre fontes como base de qualquer produto de dados.
- Camadas de dados: Bronze (raw/imutável), Silver (confiável/limpo), Gold (consumo/negócio).
- Contrato de dados: schema + partição + formato + SLA por fonte.
- Design para o futuro: projetar considerando fontes que ainda não estão implementadas.

## Agenda detalhada (90 min)
- **0–20 min**: domínio e modelo de dados — apresentar as cinco entidades com campos e chaves, o tecido conectivo (`user_id`, `campaign_id`) e ancorar o mentorado no modelo antes das perguntas de negócio.
- **20–35 min**: perguntas de negócio e mapa de fontes — partir das perguntas dos gestores (CEO, Growth, Operações, Analytics), com o modelo na frente, para rastrear quais entidades e fontes são necessárias para cada resposta.
- **35–55 min**: natureza das fontes — por que cada entidade exige uma abordagem diferente (CDC, batch, streaming) e apresentação das categorias de ferramentas para cada tipo de ingestão.
- **55–75 min**: desenho da arquitetura macro v0 com os slots de ferramentas marcados e definição dos contratos por fonte.
- **75–85 min**: decisões tomadas, decisões em aberto e backlog priorizado para a Sessão 06.
- **85–90 min**: tarefa de casa — o mentorado pesquisa e propõe uma ferramenta por tipo de ingestão para apresentar no início da S06.

## Exercícios práticos (com entregáveis)

1. **Mapeamento de perguntas de negócio → fontes**
   - Entregável: tabela com pergunta, stakeholder e fontes necessárias para respondê-la.

2. **Mapa de entidades e relações**
   - Entregável: diagrama das tabelas do domínio com chaves e relacionamentos explícitos.

3. **Matriz de natureza das fontes**
   - Entregável: tabela com fonte, natureza (CDC/batch/streaming), frequência, SLA e justificativa da escolha.

4. **Architecture canvas v0**
   - Entregável: diagrama macro com fontes, slots de ferramentas, camadas Bronze/Silver/Gold e consumo.

5. **Contratos de dados v0**
   - Entregável: por fonte — schema esperado, formato de destino (Parquet), estratégia de partição e SLA.

6. **Tarefa de casa — proposta de ferramentas**
   - Entregável: tabela com ingestão, ferramenta proposta e justificativa de escolha (custo, complexidade, manutenção).
   - Apresentada no início da Sessão 06.

## Checklist de validação
- [ ] Perguntas dos gestores mapeadas para fontes necessárias.
- [ ] Entidades do domínio e relações via `user_id` e `campaign_id` desenhadas.
- [ ] Natureza de cada fonte justificada com critério técnico.
- [ ] Categorias de ferramentas apresentadas para CDC, API e streaming.
- [ ] Architecture canvas v0 desenhado com slots de ferramentas marcados.
- [ ] Contratos de dados v0 definidos para as 3 fontes.
- [ ] Contrato do Kafka (`events`) projetado: schema, tópico, partição — sem implementação.
- [ ] Tarefa de casa comunicada: proposta de ferramenta por tipo de ingestão para a S06.
- [ ] Backlog claro e priorizado para a Sessão 06.

## Materiais desta sessão
- `plano-aula.md`
- `apostila-sessao-05-ultra-detalhada.md`
- `checklist-execucao-ao-vivo.md`
- `falas-sessao-05.md` — falas literais para uso como cola rápida durante a sessão
- `roteiro-ao-vivo-sessao-05.md` — roteiro completo de condução com anotações de tela, diagnóstico, sinal, bloqueio e corte

## Próxima sessão
A Sessão 06 implementará as primeiras ingestões (CDC e API), escrevendo dados reais no Bronze (MinIO), com base nos contratos definidos nesta sessão.

## Referências (Design Patterns)
- **Cap. 2 — Data Ingestion Design Patterns**
- **Cap. 6 — Data Flow Design Patterns**
- **Cap. 8 — Data Storage Design Patterns**
