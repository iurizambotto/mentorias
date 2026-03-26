# Sessão 04 — Particionamento + integração do pipeline

## Contexto
Sessão hands-on para conectar CDC, Airflow, MinIO e Trino e transformar isso em um pipeline real. O foco é ensinar o mentorado a pensar o Projeto 1 como um todo: fluxo, modelagem e particionamento trabalhando juntos.

## Objetivo da sessão
Capacitar o mentorado a ligar as “caixinhas” do projeto, definir modelagem mínima (grão e chaves) e aplicar particionamento de forma consciente, validando o resultado no Trino.

## Resultado esperado
- Mapa do pipeline end-to-end desenhado (origem → CDC → bronze → silver → gold → consumo).
- Modelagem básica definida: grão, chaves e entidades do Projeto 1.
- Lab executado: dados carregados no MinIO, tabela bronze e tabela silver particionada criadas no Trino.
- Partition pruning demonstrado via EXPLAIN.
- Plano de particionamento + mini ADR inicial.

## Duração recomendada
- **Base:** 60 minutos (1h).
- **Máximo:** 90 minutos (1h30), com extensões opcionais.

---

## Guia de fala em bullets (versão base — 60 min)

### Bloco 1 (0–10 min) — Mapa do projeto (as caixinhas)
- Desenhar o fluxo completo: origem → CDC → bronze → silver → gold → consumo.
- Definir responsabilidades de cada caixa (orquestração, storage, consulta).
- Introduzir o papel do Airflow como orquestrador do pipeline.

### Bloco 2 (10–20 min) — Modelagem mínima
- Definir grão das entidades (events, campaigns, costs, crm).
- Definir chaves principais e colunas de tempo.
- Decidir quais tabelas são append-only e quais são upsert.

### Bloco 3 (20–45 min) — Laboratório integrado
- Subir MinIO + Hive Metastore + Trino.
- Carregar dados de marketing no MinIO.
- Criar tabela bronze (raw) via CSV.
- Criar tabela silver particionada (Parquet) via CTAS.
- Validar partition pruning com EXPLAIN.

### Bloco 4 (45–60 min) — Fechamento e entregáveis
- Consolidar plano de particionamento e trade-offs.
- Registrar mini ADR de particionamento.
- Definir próximos passos do Projeto 1.

## Extensão opcional (60–90 min)
- Demonstrar problema de alta cardinalidade e small files.
- Discutir skew e hot partitions.
- Estimar custo de queries com e sem particionamento.

---

## Exercícios com entregáveis

### 1. Mapa do pipeline + contrato mínimo
- Entregável: diagrama com fluxo completo e responsabilidades.

### 2. Plano de modelagem
- Entregável: grão, chaves, entidades e camadas do Projeto 1.

### 3. Plano de particionamento + mini ADR
- Entregável: estratégia de partição para `events` com justificativa.

---

## Infraestrutura da sessão
- `../../infrastructure/sessao-04-particionamento/`
- Serviços: MinIO, Hive Metastore, Trino.
- Porta Trino: `http://localhost:8090`
- Porta MinIO Console: `http://localhost:9001` (login: minioadmin / minioadmin)
