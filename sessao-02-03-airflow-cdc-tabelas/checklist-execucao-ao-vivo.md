# Checklist de execução ao vivo — Sessão 02+03

## Duração da sessão conjunta
- **Versão padrão:** 90 minutos (1h30).
- **Versão compacta:** 60 minutos (1h).

## Ordem de execução

### 1) Preparar ambiente
- [ ] Docker e Compose v2 funcionando.
- [ ] Terminal no projeto (Ubuntu local ou WSL no Windows).
- [ ] Validar comandos:
  ```bash
  docker --version
  docker compose version
  ```

### 2) Subir Airflow (base)
- [ ] Entrar na pasta:
  ```bash
  cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-02-orquestracao-airflow
  ```
- [ ] Inicializar (se necessário):
  ```bash
  docker compose up airflow-init
  ```
- [ ] Subir stack:
  ```bash
  docker compose up -d
  ```
- [ ] Smoke check:
  ```bash
  docker compose ps
  curl -f http://localhost:8080/api/v2/version
  ```

### 3) Subir laboratório CDC (sessão consolidada)
- [ ] Entrar na pasta:
  ```bash
  cd /home/iurizambotto/zambotto_new/projects/zambotto-mentoria/infrastructure/sessao-02-03-airflow-cdc-tabelas
  ```
- [ ] Subir compose combinado:
  ```bash
  docker compose \
    -f ../sessao-02-orquestracao-airflow/docker-compose.yml \
    -f docker-compose.yml \
    --profile lab \
    up -d
  ```
- [ ] Validar laboratório:
  ```bash
  docker compose ps cdc-lab
  ```

### 4) Gerar artefatos e CDC
- [ ] Gerar pacote da sessão com debug:
  ```bash
  docker compose run --rm cdc-lab python scripts/build_session_03_assets.py --debug
  ```
- [ ] Gerar datasets + CDC completo por domínio:
  ```bash
  docker compose run --rm cdc-lab python scripts/generate_domain_data.py \
    --config config/domains/marketing.yaml \
    --output data/generated/marketing \
    --formats csv,jsonl \
    --with-cdc \
    --debug
  ```

### 5) Validar resultados em aula
- [ ] Validar arquivos da sessão:
  ```bash
  ls ../../docs/sessions/sessao-03-cdc-airflow-tabelas/exemplos/output
  ```
- [ ] Validar CDC por ID:
  - [ ] primeira aparição do ID = `insert`
  - [ ] `update` somente após `insert`
  - [ ] `delete` terminal
  - [ ] sem `insert/update` após `delete`
- [ ] Abrir relatório:
  - `../../docs/notes/relatorio-cdc-por-id.md`

### 6) Conduzir discussão conceitual
- [ ] Formatos: CSV, JSONL, Parquet, ORC.
- [ ] Tipos de tabela: Hive, Iceberg, Delta.
- [ ] Definição bronze/silver/gold + mini ADR.

### 7) Encerrar ambiente
- [ ] Teardown:
  ```bash
  docker compose \
    -f ../sessao-02-orquestracao-airflow/docker-compose.yml \
    -f docker-compose.yml \
    down
  ```
