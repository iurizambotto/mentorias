# Sessão 04 — Particionamento + integração do pipeline

## Domínio de referência
Marketing analytics para e-commerce (eventos e campanhas).

## Objetivo
Conectar as “caixinhas” do Projeto 1 — CDC, Airflow, MinIO e Trino — e transformar isso em um pipeline coeso, com modelagem básica e estratégia de particionamento.

## Resultado esperado
- Mapa do pipeline end-to-end (origem → CDC → bronze → silver → gold → consumo).
- Modelagem básica definida (grão, chaves, entidades e camadas).
- Laboratório executado: dados carregados no MinIO, tabela bronze e tabela silver particionada criadas no Trino.
- Partition pruning demonstrado via EXPLAIN.
- Plano de particionamento do Projeto 1 + mini ADR inicial.

## Conceitos‑chave
- Pensar o projeto como um todo: fluxo, contratos e responsabilidades.
- Modelagem mínima: grão, chaves e entidades.
- Particionamento por tempo, chave ou híbrido.
- Skew, hot partitions e custo vs performance.

## Ferramentas como exemplo
- Airflow (orquestração), MinIO (storage), Hive Metastore (catálogo), Trino (consulta).

## Agenda detalhada (60–90 min)
- **0–10 min**: mapa do pipeline e decisões principais.
- **10–20 min**: modelagem básica e definição de grão/chaves.
- **20–45 min**: laboratório integrado (MinIO + Trino + particionamento).
- **45–60 min**: validações e entregáveis.
- **60–90 min (opcional)**: custo, skew e particionamento híbrido.

## Exemplos do domínio (marketing)
1. **Eventos**: particionar por `event_date` e medir pruning.
2. **Custos**: particionar por data de custo + campanha.
3. **CRM**: particionar por data de atualização (se existir).

## Exemplo testado (dados sintéticos)
**events.csv** e **events__cdc.csv** com particionamento por `event_date`.

## Exercícios práticos (com entregáveis)
1. **Mapa do pipeline + contrato mínimo**
   - Entregável: diagrama com origem, CDC, bronze, silver, gold e consumo.
2. **Plano de modelagem**
   - Entregável: grão, chaves e entidades do Projeto 1.
3. **Plano de particionamento + mini ADR**
   - Entregável: estratégia com justificativa e trade-offs.

## Checklist de validação
- Pipeline end-to-end desenhado.
- Tabela silver particionada criada e validada.
- Partition pruning demonstrado via EXPLAIN.
- Entregáveis registrados.

## Pós‑sessão (tarefas)
- Revisar o plano após testes iniciais.

## Referências (Design Patterns)
- **Cap. 8 — Data Storage Design Patterns**
- **Cap. 10 — Data Observability Design Patterns**
