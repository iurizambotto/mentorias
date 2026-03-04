# Sessão 02 — Orquestração e Airflow (plano detalhado)

> Execução conjunta com a Sessão 03: `../sessao-02-03-airflow-cdc-tabelas/plano-aula.md`

## Objetivo da sessão
Ensinar orquestração de pipelines com Airflow, cobrindo dependências, retries, idempotência e SLA com um exemplo executável.

## Resultado esperado
- Entendimento claro de quando usar orquestrador.
- Ambiente local com Airflow pronto via Docker Compose.
- DAG didática de marketing com dependências explícitas.

## Guia de fala em bullets (90 minutos)
### Bloco 1 (0-20 min) — Por que orquestrar
- Diferença entre agendar script e orquestrar fluxo.
- Falhas típicas sem orquestração: ordem errada, duplicidade, perda de rastreio.
- Conceito de idempotência operacional.

### Bloco 2 (20-45 min) — Airflow na prática
- Componentes: webserver, scheduler, triggerer, postgres e init.
- Conceitos: DAG, tasks, dependências, retries, catchup e SLA.
- Padrão de observabilidade mínima para aula.

### Bloco 3 (45-70 min) — Exemplo real da sessão
- DAG `marketing_orchestration_dag.py` com sequência:
  `extract_costs -> extract_events -> build_daily_metrics -> publish_report`.
- Simular falha no estágio de transformação e reprocessar.
- Mostrar logs de task e ordem de execução.

### Bloco 4 (70-90 min) — Exercício orientado
- Ajustar retries e timeout por task.
- Discutir impacto de idempotência no `publish_report`.

## Exercícios com entregáveis
1. Ajustar DAG para incluir task de validação de schema.
   - Entregável: print da DAG + trecho de código alterado.
2. Definir matriz de retries por tipo de falha.
   - Entregável: tabela com política de retry e justificativa.

## Referências de padrões
- Cap. 4 — Idempotency Design Patterns
- Cap. 6 — Data Flow Design Patterns
- Cap. 10 — Data Observability Design Patterns

## Arquivos desta sessão
- `exemplos/airflow/docker-compose.yml`
- `exemplos/airflow/dags/marketing_orchestration_dag.py`
- `exemplos/airflow/tests/test_airflow_assets.py`
- `exemplos/airflow/README.md`

## Infraestrutura operacional da sessão
- `../../infrastructure/sessao-02-orquestracao-airflow/docker-compose.yml`
- `../../infrastructure/sessao-02-orquestracao-airflow/runbooks/`
