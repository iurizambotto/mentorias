# TASKS - zambotto-mentoria

## 2026-02-24
- [x] 11:56 Criar estrutura inicial docs-only e documentos base.
- [x] 12:17 Importar conteúdo da aba "Sessões" via pandas.
- [ ] 11:56 Revisar política de PII e confirmar fontes externas.
- [x] 12:44 Ler todas as abas do XLSX e consolidar insights.
- [x] 13:00 Gerar documentação detalhada de todas as abas (com PII autorizado).
- [x] 13:15 Criar plano de ação e roteiros das sessões.
- [x] 13:21 Ajustar plano/roteiros com foco conceitual (ferramentas como exemplo).
- [x] 13:35 Criar arquivos individuais detalhados para cada sessão.
- [x] 10:12 Criar pacote completo de aula com gerador e exemplos testados.

## 2026-02-27
- [x] 10:43 Criar pastas detalhadas das sessões 02 e 03 com Airflow, CDC e formatos/tipos de tabela.
- [x] 10:43 Validar exemplos com `docker compose config`, `pytest`, `ruff` e `code-complexity`.
- [x] 11:33 Criar estrutura `infrastructure/` com pastas da sessão 02 até sessão 10.
- [x] 11:33 Criar `docker-compose.yml` e runbooks Ubuntu/Windows+WSL por sessão.
- [x] 11:33 Atualizar Airflow da sessão 02 para 3.1.7 com limites de recursos e comentários em PT-BR nos parâmetros adicionados.
- [x] 11:33 Validar todos os compose com `docker compose config` (sessões 02 a 10).
- [x] 13:11 Refatorar gerador para modelo genérico orientado por YAML (`config/domains/`) com CDC por tabela em seção dedicada.
- [x] 13:11 Criar CLI `generate_domain_data.py` com suporte a `--debug`, `--with-cdc`, `--dry-run` e formatos múltiplos.
- [x] 13:11 Atualizar `build_session_03_assets.py` para usar YAML + CDC genérico e logs de debug.
- [x] 13:11 Remover scripts/módulos legados acoplados ao marketing (`generators.py`, `cdc.py`, `generate_marketing_data.py`, `test_generators.py`).
- [x] 13:11 Validar refatoração com `pytest`, `ruff` e `code-complexity`.
- [x] 13:18 Ajustar YAML para políticas CDC de todas as tabelas (`users`, `campaigns`, `events`, `costs`, `crm`) com campos CDC no final.
- [x] 13:18 Adicionar debug e validação explícita de cabeçalho CDC (`cdc_op`, `cdc_event_ts`, `cdc_source_table`) em todos os arquivos `*__cdc.csv`.
- [x] 13:35 Corrigir motor CDC para lifecycle por ID (`insert -> update* -> delete?`) garantindo que após `delete` não ocorra `insert`/`update`.
- [x] 13:35 Adicionar validações de contrato CDC por ID nos testes (insert único, delete terminal, sem eventos após delete).
- [x] 13:35 Regenerar exemplos CDC e validar operações por tabela com zero violações de lifecycle.
- [x] 13:39 Gerar relatório por ID em `docs/notes/relatorio-cdc-por-id.md` com sequências e resumo por tabela.
- [x] 13:49 Criar checklist de execução ao vivo da Sessão 03 em ordem (`checklist-execucao-ao-vivo.md`) com fluxo Ubuntu/Windows WSL.
- [x] 15:52 Consolidar sessões 02 e 03 em pacote único (`docs/sessions/sessao-02-03-airflow-cdc-tabelas/`).
- [x] 15:52 Criar infraestrutura consolidada 02+03 com runbooks dedicados (`infrastructure/sessao-02-03-airflow-cdc-tabelas/`).
- [x] 15:52 Atualizar índices e referências das sessões para apontar execução conjunta.
- [x] 15:54 Corrigir duração da sessão conjunta 02+03 para 1h/1h30 no plano e checklist.

## 2026-03-03
- [x] 19:19 Subir Airflow 3.1.7 com todos os 8 containers healthy (sessão 02).
- [x] 19:27 Corrigir runbook: subir cdc-lab isolado (sem merge com o compose do Airflow).
- [x] 19:27 Subir container `mentoria-s02s03-cdc-lab` via `docker compose --profile lab up -d`.
- [x] 19:27 Instalar pacote `zambotto_mentoria` no container com `pip install -e .`.
- [x] 19:27 Gerar artefatos da sessão 03 (`build_session_03_assets.py --debug`): OK.
- [x] 19:27 Gerar datasets + CDC completo (`generate_domain_data.py --with-cdc`): 20 arquivos em `data/generated/marketing/`.
- [ ] Corrigir runbook `01_subir_ubuntu.md` para não mesclar composes (subir cdc-lab isolado).
- [x] 19:27 Adicionar `pip install -e .` ao runbook como passo obrigatório antes de rodar scripts.

## 2026-03-04
- [x] 01:00 Validar stack sessão 04 com smoke tests end-to-end (CREATE SCHEMA, CREATE TABLE, INSERT, SELECT, paths S3).
- [x] 01:00 Corrigir hive-site.xml: remover fs.s3a.* inválidos, desabilitar StorageBasedAuthorization, warehouse dir local.
- [x] 01:00 Corrigir docker-compose.yml: HIVE_AUX_JARS_PATH com hadoop-aws e aws-java-sdk-bundle.
- [x] 01:00 Restaurar fs.s3a.* no hive-site.xml após ativação dos JARs S3A no classpath.
- [x] 01:00 Confirmar particionamento por data_evento em s3://bronze/eventos/data_evento=YYYY-MM-DD/ no MinIO.
- [x] 01:09 Auditar e corrigir 7 bugs na apostila da sessão 04 (todos os labs validados end-to-end no Trino 479).

## 2026-03-16
- [x] Atualizar a Sessão 04 para hands-on integrado (CDC + Airflow + MinIO + Trino + particionamento).
- [x] Revisar roteiro, checklist e apostila da Sessão 04 com foco em pipeline end-to-end e modelagem básica.
- [x] Alterar porta do Airflow para 8081 e atualizar docs/runbooks relacionados.
- [x] Validar stack Sessão 02+03 (Airflow + CDC lab) e criar runbook de testes.

## 2026-03-18
- [x] Atualizar comandos do MinIO Client (mc) no checklist e na apostila da Sessão 04.
- [x] Ajustar tabela CSV raw para VARCHAR e aplicar CAST na tabela silver (Trino/Hive CSV limitation).
- [x] Publicar pacote da Sessão 04 no repositório github/zambotto/mentorias (docs + infra + runbooks).
