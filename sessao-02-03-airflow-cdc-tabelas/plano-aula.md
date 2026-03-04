# Sessão 02+03 — Airflow + CDC + formatos e tipos de tabela

## Contexto
Esta sessão consolidada une os conteúdos planejados originalmente para a Sessão 02 (orquestração com Airflow) e Sessão 03 (CDC + formatos + tipos de tabela).

## Objetivo da sessão
Executar um fluxo prático completo com Airflow + CDC e discutir decisões de armazenamento (formatos de arquivo e table formats) com base em trade-offs reais.

## Resultado esperado
- Airflow 3.1.x funcional localmente.
- Pipeline didático com geração de dados e CDC validado por ID.
- Entendimento aplicado de CSV, JSONL, Parquet e ORC.
- Entendimento aplicado de Hive, Iceberg e Delta.
- Entregável de decisão técnica (bronze/silver/gold + mini ADR).

## Duração recomendada
- **Versão padrão:** 90 minutos (1h30).
- **Versão compacta:** 60 minutos (1h).

## Guia de fala em bullets (versão padrão — 90 min)
### Bloco 1 (0–15 min) — Por que orquestrar
- Diferença entre agendar script e orquestrar pipeline.
- Idempotência, dependências, retries e SLA.
- Quando Airflow faz sentido no contexto da mentoria.

### Bloco 2 (15–30 min) — Airflow em execução
- Subida do Airflow e verificação de saúde.
- Componentes principais (api-server, scheduler, worker, triggerer, postgres, redis).
- Leitura de logs e troubleshooting mínimo.

### Bloco 3 (30–50 min) — CDC por ciclo de vida de ID
- Regra de lifecycle: `insert -> update* -> delete?`.
- Regra crítica: após delete, não existe insert/update.
- Execução dos scripts com debug e leitura das evidências.

### Bloco 4 (50–65 min) — Formatos de dados
- CSV vs JSONL vs Parquet vs ORC.
- Diferenças de tipagem, custo de leitura e casos de uso.

### Bloco 5 (65–80 min) — Tipos de tabela
- Hive, Iceberg e Delta.
- Trade-offs de transacionalidade, evolução de schema e time travel.

### Bloco 6 (80–90 min) — Fechamento
- Definir padrão bronze/silver/gold para o Projeto 1.
- Registrar decisão inicial de table format.

## Exercícios com entregáveis
1. Matriz de decisão de orquestrador e estratégia CDC.
   - Entregável: tabela de decisão com justificativa.
2. Definição de camadas e formatos por camada.
   - Entregável: blueprint bronze/silver/gold.
3. Mini ADR de tipo de tabela.
   - Entregável: comparação Hive vs Iceberg vs Delta.

## Arquivos consolidados (sessões 02 e 03)
- `../sessao-02-orquestracao-airflow/plano-aula.md`
- `../sessao-03-cdc-airflow-tabelas/plano-aula.md`
- `../sessao-03-cdc-airflow-tabelas/exemplos/explicacao-formatos-e-tipos-de-tabela.md`
- `../sessao-03-cdc-airflow-tabelas/checklist-execucao-ao-vivo.md`

## Infraestrutura operacional da sessão consolidada
- `../../infrastructure/sessao-02-orquestracao-airflow/`
- `../../infrastructure/sessao-02-03-airflow-cdc-tabelas/`
