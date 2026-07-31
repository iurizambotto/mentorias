---
title: "Apostila, Change Data Capture"
date: 2026-07-30
type: apostila
status: draft
project: zambotto-mentoria
tags: [cdc, ingestao]
---

# Apostila, Change Data Capture

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto.

> Conteudo extraido da apostila consolidada anterior. As secoes marcadas
> como pendentes ainda nao foram escritas no padrao unico.

## Sumario

- [3.1 Change Data Capture (CDC), conceito e lifecycle](#31-change-data-capture-cdc-conceito-e-lifecycle)
- [3.2 CDC por ciclo de vida de ID, regras e pitfalls](#32-cdc-por-ciclo-de-vida-de-id-regras-e-pitfalls)

## Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

## 3.1 Change Data Capture (CDC), conceito e lifecycle

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

## 3.2 CDC por ciclo de vida de ID, regras e pitfalls

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


## Mini-desafio com solucao

Pendente. Escrever enunciado, dicas e gabarito comentado.

## Rubrica de validacao da aprendizagem

Pendente. Definir criterio, suficiente e excelente.

## Erros comuns e como corrigir

Pendente. Levantar sintoma, causa e correcao.

## Plano de continuidade

Pendente. Apontar o proximo modulo da trilha.

## Glossario

Pendente. Listar os termos novos deste modulo.

## Referencias

Pendente. Documentacao oficial com data de consulta.

## Fontes verificadas

Pendente. Nenhuma afirmacao deste modulo foi conferida contra doc oficial.
